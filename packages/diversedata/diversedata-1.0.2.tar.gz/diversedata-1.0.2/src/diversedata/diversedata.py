import pandas as pd
import importlib.resources as resources

def load_data(data_name: str):
    """
    Returns a pandas.DataFrame of a .csv file that is bundled in this
    package.

    Looks for data_name.csv in this package's resources (in the data
    directory) and raises an error if data_name is not a string or if
    the file is missing.

    Parameters
    ----------
    data_name : str
        The filename (excluding the .csv extension) of the data resource to
        load.

    Returns
    -------
    pandas.DataFrame
        A DataFrame with the contents of data_name.csv.

    Raises
    ------
    TypeError
        If data_name is not a string.
    FileNotFoundError
        If data_name.csv cannot be found in this package.

    Example
    --------
    >>> import diversedata as dd
    >>> df = dd.load_data("wildfire")
    >>> df.head()
       year     fire_number     current_size  ...
    0  2006     PWF001          0.1           ...
    """
    # Raise TypeError if data_name is not a string
    if not isinstance(data_name, str):
        raise TypeError(
            f"{data_name} must be a string with no file extension.")

    # Get the root package name
    package_name = __name__.split('.')[0]

    # Construct the file path
    file_path = f"data/{data_name}.csv"

    try:
        # Use importlib.resources to access the file in this package
        with resources.files(package_name).joinpath(file_path).open("r", encoding="utf-8") as data_file:
            data = pd.read_csv(data_file)
        return data
    except FileNotFoundError:
        raise FileNotFoundError(
            f"{data_name}.csv is not found in the {package_name} package.")

def print_data_description(data_name: str):
    """
    Prints the description of a dataset contained in a .txt file that is
    bundled in this package.

    Looks for data_name.txt in this package's resources (in the
    data_descriptions directory) and raises an error if data_name is not a
    string or if the file is missing.

    Parameters
    ----------
    data_name : str
        The filename (excluding the .txt extension) of the data description
        file to print.

    Raises
    ------
    TypeError
        If data_name is not a string.
    FileNotFoundError
        If data_name.txt cannot be found in this package.
    
    Example
    --------
    >>> import diversedata as dd
    >>> dd.print_data_description("wildfire")
    Alberta Historical Wildfire Dataset (2006-2024).

    This dataset contains detailed records of wildfire...
    """
    # Raise TypeError if data_name is not a string
    if not isinstance(data_name, str):
        raise TypeError(
            f"{data_name} must be a string with no file extension.")

    # Get the root package name
    package_name = __name__.split('.')[0]

    # Construct the file path
    file_path = f"data_descriptions/{data_name}.txt"

    try:
        # Use importlib.resources to access the file in this package
        with resources.files(package_name).joinpath(file_path).open('r', encoding='utf-8') as description_file:
            description = description_file.read()
            print(description, end='')
    except FileNotFoundError:
        raise FileNotFoundError(
            f"{data_name}.txt is not found in the {package_name} package.")


def list_available_datasets():
    """
    Prints a list of available datasets in this package, and how
    to load them and how to access their documentation.

    Scans the data/ resource for .csv files included in this package.
    For each dataset found, prints:

    - The dataset name (excluding the .csv extension)
    - The function to load the dataset (e.g., load_data('<datasetname>'))
    - The method to view the dataset documentation (e.g.,
      print_data_description('<datasetname>') if a description file exists,
      or a note if it is missing.

    Assumes datasets are stored as .csv files in the data/ resource and
    descriptions as .txt files in the data_descriptions/ resource of this
    package.

    Parameters
    ----------
    None

    Returns
    -------
    None
        Prints dataset information.
        Prints "No datasets found." if no datasets in data/.
        Prints "Data directory not found in package." if the data/ is missing.

    Example
    --------
    >>> import diversedata as dd
    >>> dd.list_available_datasets()
    Available datasets:
    • wildfire
      Load with:    load_data('wildfire')
      View documentation with:  print_data_description('wildfire')
    ...
    """
    # Get the root package name
    package_name = __name__.split('.')[0]

    try:
        # Directories for data and descriptions
        data_dir = resources.files(package_name).joinpath("data")
        desc_dir = resources.files(package_name).joinpath("data_descriptions")

        # Get all .csv files in data/
        csv_files = [f.name for f in data_dir.iterdir() if f.name.endswith('.csv')]

        # If no .csv files found in data/, print a message
        if not csv_files:
            print("No datasets found.")
            return None

        # List the available datasets
        print("Available datasets:\n")
        for file in sorted(csv_files):
            dataset_name = file.replace(".csv", "")

            # Check if corresponding description file exists
            desc_file = desc_dir.joinpath(f"{dataset_name}.txt")
            has_description = desc_file.is_file()

            print(f"• {dataset_name}")
            print(f"  Load with:                load_data('{dataset_name}')")
            if has_description:
                print(f"  View documentation with:  print_data_description('{dataset_name}')")
            else:
                print(f"  Description file not found.")
            print()

    except FileNotFoundError:
        raise FileNotFoundError(
            "Data directory not found in package.")