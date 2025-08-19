# read version from installed package
from importlib.metadata import version
__version__ = version("diversedata")

# populate package namespace
from diversedata.diversedata import load_data, list_available_datasets, print_data_description