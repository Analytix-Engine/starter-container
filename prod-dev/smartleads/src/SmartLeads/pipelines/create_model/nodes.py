import itertools

import ibis
from tqdm import tqdm


DEFAULT_MIN_FEATURES_PER_RULE = 1
DEFAULT_MAX_FEATURES_PER_RULE = 2
DEFAULT_MIN_SUPPORT = 0.01
DEFAULT_MIN_CONFIDENCE = 0.1
DEFAULT_MIN_RECOMMENDED_BASKET_SIZE = 1
DEFAULT_MAX_RECOMMENDED_BASKET_SIZE = 1

COMBINATONS_PER_QUERY = 1000
MAX_WORKERS = 1


def get_combined_grouped(combined: ibis.table) -> ibis.table:
    """Get the combined grouped table.

    Args:
        combined (ibis.table): The combined table.

    Returns:
        ibis.table: The combined grouped table.
    """
    return combined.group_by(combined.columns[1:]).aggregate(row_freq=combined.count())


def create_a_and_b_for_combinations(
    product_columns: list,
    combination: list,
    columns: list,
    ts: ibis.table
):
    a_and_b_components = []
    for product_column in product_columns:
        # Add the product column to the combination
        if product_column not in combination:
            a_and_b_columns = list(combination) + [product_column]

            # Group by the columns and find the total
            a_and_b = ts.group_by(a_and_b_columns).aggregate(
                a_and_b_freq=ts["row_freq"].sum()
            )

            # Now, rename the product_column to "Recommendation"
            a_and_b = a_and_b.mutate(
                Recommendation=ibis.literal(product_column),
            ).mutate(**{
                product_column: ibis.literal("")
            })

            for col in columns:
                if col not in a_and_b.columns:
                    a_and_b = a_and_b.mutate(**{col: ibis.literal("")})
            a_and_b_components.append(a_and_b)
    # Now we union all the tables in a_and_b_components in a table called a_and_b
    a_and_b = None
    for table in a_and_b_components:
        if a_and_b is None:
            a_and_b = table
        else:
            a_and_b = a_and_b.union(table)

    return a_and_b


def process_combination_frequency_counts(
        con: ibis.BaseBackend,
        ts, combinations, columns, product_support_table,
        min_confidence: float
):
    product_columns = [c for c in columns if c.startswith("P~")]
    b = product_support_table
    tables = []
    for combination in combinations:
        # Create the LHS table a--------------------------------------------------------        
        a = ts.group_by(combination).aggregate(a_freq=ts["row_freq"].sum())
        for col in columns:
            if col not in combination:
                a = a.mutate(**{col: ibis.literal("")})

        # Concatenate the columns into a single comma-separated string.
        a = a.mutate(num_features=len(combination))

        # Create the tables a and b-----------------------------------------------------
        a_and_b = create_a_and_b_for_combinations(
            product_columns, combination, columns, ts
        )

        if a_and_b is not None:
            # con.create_table('a_and_b', a_and_b, overwrite=True)
            # a_and_b = con.table('a_and_b')

            # Now we join a_and_b to table b to get the product support---------------------
            # Create a table called a_and_b_with_b that joines a_and_b and b
            # on the Recommendation Column
            a_and_b_with_b = a_and_b.join(
                b,
                a_and_b["Recommendation"] == b["Recommendation"],
                how="inner",
                suffixes=["", "_z"]
            )

            join_condition = None
            for c in columns:
                m = a[c] == a_and_b_with_b[c]
                if join_condition is None:
                    join_condition = m
                else:
                    join_condition = join_condition & m

            # Combine the tables into associations------------------------------------------
            associations_temp = a.join(
                a_and_b_with_b,
                join_condition,
                how="inner",
                suffixes=["", "_z"]
            )

            tables.append(associations_temp)

    result = None
    for table in tables:
        if result is None:
            result = table
        else:
            result = result.union(table)

    # Calculate the confidence and lift metrics-----------------------------------------
    result = result.mutate(
        confidence=result["a_and_b_freq"] / result["a_freq"],
        lift=(result["a_and_b_freq"] / result["a_freq"]) / result["product_support"]
    )

    # Filter out the results where the confidence is less than the min_confidence--------
    result = result.filter(result["confidence"] >= min_confidence)

    return result.execute()


def create_product_support_table(ts: ibis.table) -> ibis.table:
    """Create the product frequency table.

    Args:
        ts (ibis.table): The table to create the product frequency table from.

    Returns:
        ibis.table: The product frequency table.
    """
    # We will need to create a table that has the same number of rows as the ts table.
    # This table will have one column for each product in the ts table.
    # The value of each cell will be the product name if the product is in the row,
    # and an empty string if the product is not in the row.
    # We will then group by the product columns and find the total.
    # This will give us the product frequency table.

    # Get the product columns.
    product_columns = [c for c in ts.columns if c.startswith("P~")]

    # Get the total number of rows as the divisor.
    support_divisor = ts["row_freq"].sum().execute()

    tables = []
    for product in product_columns:
        # First filter that the product column is not an empty string.
        t = ts.filter(ts[product] != "")

        # Then group by the product column and find the total.
        t = t.group_by(product).aggregate(
            product_support=ts["row_freq"].sum() / ibis.literal(support_divisor)
        )

        # Now rename the product column to "Product"
        t = t.mutate(
            Recommendation=ibis.literal("P~").concat(t[product])
        )

        # Then we drop the product column.
        t = t.drop(product)

        # Append it to the tables to be unioned
        tables.append(t)

    # Now we union all the tables
    result = None
    for table in tables:
        if result is None:
            result = table
        else:
            result = result.union(table)

    return result


def get_combo_frequency_counts(
    con: ibis.BaseBackend,
    combined_grouped: ibis.expr.types.relations.Table,
    min_features_per_rule: int = DEFAULT_MIN_FEATURES_PER_RULE,
    max_features_per_rule: int = DEFAULT_MAX_FEATURES_PER_RULE,
    min_confidence: float = DEFAULT_MIN_CONFIDENCE

):
    ts = combined_grouped

    product_support_table = create_product_support_table(ts)
    con.create_table("temp_table_product_support", product_support_table, overwrite=True)
    product_support_table = con.table("temp_table_product_support")

    # We take all of the columns except the count column.
    columns = ts.columns[:-1]

    # Now we will loop through the number of features per rule.
    num_features_progress = tqdm(
        list(range(min_features_per_rule, max_features_per_rule + 1)),
        desc="Number of features per rule"
    )
    combos = []

    for num_features in num_features_progress:
        # Now give me all combinations of num_features from columns.
        # Order does not matter, so we can use combinations instead of permutations.
        combinations_to_process = list(itertools.combinations(columns, num_features))

        # Loop through the combinations_to_progress in batches of
        # COMBINATIONS_PER_QUERY.
        combinations_to_process_progress = tqdm(
            range(0, len(combinations_to_process), COMBINATONS_PER_QUERY),
            desc="Combinations to process"
        )
        table_ref_num_total = 0
        for table_ref_num, i in enumerate(combinations_to_process_progress):
            # Get the next COMBINATIONS_PER_QUERY combinations.
            combinations_to_process_chunk = \
                combinations_to_process[i:i + COMBINATONS_PER_QUERY]

            table_ref_num_total += 1

            temp_table_name = f"temp_table_combinations_{num_features}_{table_ref_num}"

            con.create_table(
                temp_table_name,
                process_combination_frequency_counts(
                    con,
                    ts,
                    combinations_to_process_chunk,
                    columns,
                    product_support_table,
                    min_confidence
                ),
                overwrite=True
            )

            combos.append(con.table(temp_table_name))

    result = None
    for table in combos:
        if result is None:
            result = table
        else:
            result = result.union(table)

    return result


def clear_temp_tables(con: ibis.BaseBackend):
    for table in con.list_tables():
        if table.startswith("temp_table_"):
            con.drop_table(table, force=True)
