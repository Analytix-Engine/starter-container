import os
import pickle
from typing import List

from kedro.io import DataCatalog
from kedro_datasets.pickle.pickle_dataset import PickleDataSet

from SmartLeads.streamlit_app.util.folders import get_workspace_folders

CATALOG_FOLDER = get_workspace_folders(tool_name="SmartLeads")["CATALOG"]
CATALOG = "DATA"


def create_catalog_safe_name(
    catalog_name: str, dataset_name: str, component: str
) -> str:
    """Creates a safe name for a data catalog.

    Args:
        name (str): The name to create a safe name for.

    Returns:
        str: The safe name.
    """
    a = catalog_name.strip().replace(" ", "_").lower()
    b = dataset_name.strip().replace(" ", "_").strip().lower()
    c = component.strip().replace(" ", "_").lower()
    return f"{a} ~ {b} ~ {c}"


def get_select_labels_from_catalog(catalog_name_str: str):
    """Gets the labels for a select box from a data catalog.

    Args:
        catalog_name_str (str): The name of the data catalog.

    Returns:
        List[str]: The list of labels for the select box.
    """
    datasets = load_catalog(CATALOG).list()
    catalog_name_str = catalog_name_str.strip().replace(" ", "_").lower()
    labels = [
        x.split(" ~ ")[1]
        for x in datasets
        if ((x.split(" ~ ")[0] == catalog_name_str) and (x.split(" ~ ")[2] == "parms"))
    ]
    return labels


def load_catalog(identifier: str) -> DataCatalog:
    """Loads a data catalog from a pickle file using the identifier.

    Args:
        identifier (str): The identifier for the data catalog.

    Returns:
        DataCatalog: The data catalog that is loaded from the pickle file.
    """
    catalog_path = os.path.join(CATALOG_FOLDER, f"{identifier}.pickle")
    # If the file doesn't exist, return an empty DataCatalog
    if not os.path.exists(catalog_path):
        return DataCatalog()
    else:
        with open(catalog_path, "rb") as file_reader:
            return pickle.load(file_reader)


def save_catalog(data_catalog: DataCatalog, identifier: str) -> None:
    """Saves a data catalog to a pickle file using the identifier.

    Args:
        data_catalog (DataCatalog): The data catalog to save.
        identifier (str): The identifier for the data catalog.
    """
    catalog_path = os.path.join(CATALOG_FOLDER, f"{identifier}.pickle")
    with open(catalog_path, "wb") as file_writer:
        pickle.dump(data_catalog, file_writer)


def combine_catalogs(catalog_list=List[DataCatalog]) -> DataCatalog:
    """Combines a list of data catalogs into a single data catalog.

    Args:
        catalog_list (List[DataCatalog]): A list of data catalogs to combine.

    Returns:
        DataCatalog: A single data catalog that is the combination of all the
            data catalogs in the list.
    """

    # If there's nothing in the list, return None.
    if len(catalog_list) == 0:
        return None

    # If there's only one item in the list, return that item.
    elif len(catalog_list) == 0:
        return catalog_list[0]

    else:
        # Start with the first datacatalog in the list.
        catalog = catalog_list[0]
        # Loop through the other ones in the list and add them to the
        # first one.
        for i in range(1, len(catalog_list)):
            # Gets a dictionary of all the items in the catalog to add.
            catalog_to_add = catalog_list[i]._data_sets

            # Loop through each item and add them to the original catalog.
            for name, dataset in catalog_to_add.items():
                catalog.add(
                    name,
                    dataset,
                    replace=True,
                )
        return catalog


def remove_dataset_from_data_catalog(
    dataset_name: str, data_catalog: DataCatalog
) -> DataCatalog:
    """Removes a dataset from the data catalog.

    Args:
        dataset_name (str): Name of the dataset to remove.
        data_catalog (DataCatalog): Data catalog to remove the dataset from.

    Returns:
        DataCatalog: Data catalog with the dataset removed.
    """
    list_of_entries = data_catalog.list()
    new_catalog = DataCatalog()
    for c in list_of_entries:
        if c != dataset_name:
            new_catalog.add(c, data_catalog._data_sets[c])
    return new_catalog


def add_pickle_to_catalog(
    data_path: str,
    data_catalog: DataCatalog,
    data_catalog_identifier: str,
    dataset_name: str,
) -> DataCatalog:
    """Add a PickleDataSet to the data catalog.

    Args:
        data_path (str): Path name in data folder
        data_catalog (DataCatalog): Data catalog to add the dataset to.
        data_catalog_identifier (str): Identifier for the data catalog.
        dataset_name (str): Name of the dataset to add.

    Returns:
        DataCatalog: _description_
    """

    data_folder = get_workspace_folders(tool_name="SmartLeads")["DATA"]

    output_path = os.path.join(
        data_folder,
        data_path,
        f"{dataset_name}.pickle",
    )

    data_catalog.add(dataset_name, PickleDataSet(output_path), replace=True)

    save_catalog(data_catalog, data_catalog_identifier)

    return data_catalog
