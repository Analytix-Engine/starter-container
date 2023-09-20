import ibis
import pandas as pd
from typing import Tuple

INFREQUENT_PERCENTAGE_DEFAULT = 0.01


class IbisCategoricalTransformer:
    def __init__(
            self,
            table: ibis.expr.types.relations.Table,
            column_name: str,
            infrequent_percentage: float = 0.01
    ):
        self.table = table
        self.column_name = column_name
        self.infrequent_percentage = infrequent_percentage

    def fit(self):
        t = self.table
        # Get the frequency of each value
        freq = t.group_by(self.column_name).count().execute()
        freq.columns = ['value', 'count']
        freq['percentage'] = freq['count'] / freq['count'].sum()
        # Get the infrequent values
        self.frequent_values = (
            freq[freq['percentage'] >= self.infrequent_percentage]['value'].tolist()
        )
        return self

    def build_case_statement_element(self, case_statement, value, reference):
        return case_statement.when(value, reference)

    def build_case_statement(self, reference):
        case_statement = reference.case()
        for frequent_value in self.frequent_values:
            case_statement = self.build_case_statement_element(
                case_statement, frequent_value, reference
            )
        case_statement = case_statement.else_("_other").end()
        return case_statement

    def transform(self, table: ibis.expr.types.relations.Table):
        t = table
        # Replace the infrequent values with the string 'infrequent'
        t = t.mutate(**{
            self.column_name: self.build_case_statement(t[self.column_name])
        })
        return t


class IbisBinningTransformer:
    """
    A class for binning a column in an Ibis table based on quantiles.

    Args:
        con (ibis.backends.duckdb.Backend): The Ibis backend connection.
        table (ibis.expr.types.relations.Table): The Ibis table containing the data.
        column_name (str): The name of the column to be binned.
        n_bins (int, optional): The number of bins to create. Default is 10.

    Attributes:
        con (ibis.backends.duckdb.Backend): The Ibis backend connection.
        table (ibis.expr.types.relations.Table): The Ibis table containing the data.
        column_name (str): The name of the column to be binned.
        n_bins (int): The number of bins to create.
        bin_edges (list): The quantile-based bin edges.
    """

    def __init__(
        self,
        table: ibis.expr.types.relations.Table,
        column_name: str,
        n_bins: int = 10,
    ):
        self.table = table
        self.column_name = column_name
        self.n_bins = n_bins
        self.bin_edges = None

    def bin_label_element(self, statement, bin_label):
        return statement.when(bin_label, bin_label)

    def fit(self):
        """
        Fit the binning transformer to the specified column based on quantiles.

        This method calculates bin edges based on quantiles of the data in the
        specified column.

        Returns:
            None
        """
        # Get the specified column from the table
        column = self.table[self.column_name]

        # Calculate quantile-based bin edges
        quantiles = [i / self.n_bins for i in range(1, self.n_bins)]
        self.bin_edges = column.quantile(quantiles).execute()
        return self

    def transform(self, table: ibis.expr.types.relations.Table = None):
        """
        Apply the quantile-based binning transformation to the specified column.

        This method assigns bin labels to the data in the specified column based on
        the quantile-based bin edges calculated during the fitting process.

        Returns:
            ibis.expr.api.NumericValue: A new Ibis expression representing the binned
            column.
        """
        if table is None:
            t = self.table
        else:
            t = table
        if self.bin_edges is None:
            raise ValueError("Fit method must be called before transform.")

        # Get the specified column from the table
        column = t[self.column_name]

        # Use ibis case statement to assign bin labels based on quantiles
        last_bin_edge = None

        fmt = "{:.2f}"
        # Calculate if the column max is greater than 100
        # If so, we include a space thousands separator
        # in the fmt string
        column_max = column.max().execute()
        if column_max > 100:
            fmt = "{:,.0f}"
        elif column_max > 10:
            fmt = "{:,.1f}"
        elif column_max > 1:
            fmt = "{:,.2f}"
        elif column_max > 0.1:
            # Format this as a percentage
            fmt = "{:.1%}"
        elif column_max > -1:
            fmt = "{:,.2f}"
        elif column_max > -10:
            fmt = "{:,.1f}"
        elif column_max > -100:
            fmt = "{:,.0f}"

        conditions = []
        labels = []
        for i, bin_edge in enumerate(self.bin_edges):
            # The bin label is ([last bin edge], [current bin edge)]
            # but rounded to 2 decimal places
            if last_bin_edge is None:
                bin_label = f"""(-inf, {
                    fmt.format(round(bin_edge, 2)).replace(',', ' ')
                }]"""
            else:
                bin_label = f"""[{
                    fmt.format(round(last_bin_edge, 2)).replace(',', ' ')
                }, {
                    fmt.format(round(bin_edge, 2)).replace(',', ' ')
                }]"""
            labels.append(bin_label)
            if i == 0:
                # Handle the first bin separately
                conditions.append(column <= bin_edge)
            elif i == len(self.bin_edges) - 1:
                # Handle the last bin separately
                conditions.append(column > self.bin_edges[i - 1])
            else:
                conditions.append(
                    (column > self.bin_edges[i - 1]) & (column <= bin_edge)
                )
            last_bin_edge = bin_edge

        def add_when(expr, condition, label):
            return expr.when(condition, label)

        statement = ibis.case()
        for condition, label in zip(conditions, labels):
            statement = add_when(statement, condition, label)

        statement = statement.else_("Other").end()

        # Do the mutation
        t = t.mutate(**{
            self.column_name: statement
        })

        return t
    

class ProductOneHotEncoder:
    def __init__(
        self,
        product_data: ibis.table,
        product_table: ibis.table,
    ):
        self.product_data = product_data
        self.product_table = product_table

    def fit(self):
        # Get the products from the product_data table
        products = self.product_table['Product'].execute()
        self.products = products.tolist()
        return self

    def transform(self, table: ibis.table = None):
        if table is None:
            t = self.product_data
        else:
            t = table

        # Loop through the products and create a new column for each product.
        # The column's name should be the product name prefixed with "P~".
        # The column's value should be 1 if the Product column is equal to the product name,
        # otherwise 0.
        for product in self.products:
            t = t.mutate(
                **{f'P~{product}': t['Product'].case().when(
                    ibis.literal(product),
                    ibis.literal(product)).else_(ibis.literal("")).end()}
            )

        # Grouping per customer and seeing if they have at least one of each of
        # the products.
        customer_id_column = self.product_data.columns[0]
        grouped_product_data = t.group_by(customer_id_column).aggregate(
            **{f'P~{product}': t[f'P~{product}'].max() for product in self.products}
        )

        return grouped_product_data


class IbisPipe:
    def __init__(self):
        self.steps = []

    def add_step(self, step):
        self.steps.append(step)
        return self

    def fit(self):
        for step in self.steps:
            step.fit()
        return self

    def transform(self):
        t = None
        for step in self.steps:
            if t is None:
                t = step.transform(step.table)
            else:
                t = step.transform(t)
        return t


def preprocess_customer_data(
    customer_data: ibis.table,
    infrequent_percentage: float = INFREQUENT_PERCENTAGE_DEFAULT
) -> Tuple[pd.DataFrame]:
    t = customer_data

    # Find the categorical columns in the ibis table
    categorical_columns = []
    numeric_columns = []
    for column in t.columns[1:]:
        if isinstance(t[column], ibis.expr.types.StringColumn):
            categorical_columns.append(column)
        if isinstance(t[column], ibis.expr.types.NumericColumn):
            numeric_columns.append(column)

    pipe = IbisPipe()
    for c in categorical_columns:
        pipe = pipe.add_step(
            IbisCategoricalTransformer(t, c, infrequent_percentage)
        )
    for c in numeric_columns:
        pipe = pipe.add_step(IbisBinningTransformer(t, c))

    pipe = pipe.fit()
    t = pipe.transform()

    return t, pipe


def get_products_table(product_data: ibis.table) -> ibis.table:
    # Create a variable called products_table that is a table with the distinct values
    # from the Product column in the product_data table
    return product_data.distinct(on=['Product'])[['Product']]


def preprocess_product_data(
    product_data: ibis.table,
    products_table: ibis.table
) -> Tuple[ibis.table, IbisPipe]:
    """ Preprocess product data

    Args:
        product_data (ibis.table): The product data table.
        products_table (ibis.table): The products table.

    Returns:
        Tuple[ibis.table, IbisPipe]: A tuple containing the preprocessed product data
        and the IbisPipe used to preprocess the data."""
    product_one_hot_encoder = ProductOneHotEncoder(product_data, products_table)
    product_one_hot_encoder = product_one_hot_encoder.fit()
    product_data_preprocessed = product_one_hot_encoder.transform(product_data)
    pipe = IbisPipe()
    pipe.add_step(product_one_hot_encoder)
    return product_data_preprocessed, pipe


def combine_customer_and_product_data(
    customer_data_preprocessed: ibis.table,
    product_data_preprocessed: ibis.table,
) -> ibis.table:
    """ Combines the customer and product data based on customer id.

    Args:
        customer_data_preprocessed (ibis.table): The preprocessed customer data.
        product_data_preprocessed (ibis.table): The preprocessed product data.

    Returns:
        ibis.table: The combined customer and product data.
    """
    # Join the customer_data_preprocessed and product_data_preprocessed tables
    # on the CustomerID column

    customer_id_column = customer_data_preprocessed.columns[0]

    return customer_data_preprocessed.join(
        product_data_preprocessed,
        customer_data_preprocessed[customer_id_column] == product_data_preprocessed[customer_id_column],
        how='inner'
    )