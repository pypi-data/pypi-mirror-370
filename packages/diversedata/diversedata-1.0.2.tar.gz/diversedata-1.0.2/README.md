[![codecov](https://codecov.io/gh/diverse-data-hub/diversedata-py/branch/main/graph/badge.svg?token=OO2HCJBWU1)](https://codecov.io/gh/diverse-data-hub/diversedata-py)

# diversedata <img src="https://raw.githubusercontent.com/diverse-data-hub/diversedata-py/main/img/logo.png" align="right" width="49"/>

`diversedata` is a Python package that provides a curated collection of real-world data sets centered on themes of equity, diversity and inclusion (EDI). These data sets are intended to support teaching, learning, and analysis by offering meaningful and socially relevant data that can be used in data science workflows.

Each data set includes contextual background and documentation to support thoughtful exploration. Example use cases are included to demonstrate practical applications in R and Python are available on the [website](https://diverse-data-hub.github.io/).

For more information, please visit: <https://diverse-data-hub.github.io/>

## Installation

The `diversedata` Python package can be installed via pip:

```bash
pip install diversedata
```

## Usage

Once installed, you can explore the available data sets and their documentation:

```python
import diversedata as dd

# List available datasets
dd.list_available_datasets()

# View documentation for a specific dataset
dd.print_data_description('wildfire')

# To load a dataset and save it to an object:
df = dd.load_data('wildfire')
```

## Package Dependencies

This package has the following dependency:

- `pandas>=2.3.1`

Please note that this dependency will be installed automatically when pip installing the `diversedata` package.

## Contributing

Interested in contributing? Check out the contributing guidelines. Please note that this project is released with a Code of Conduct. By contributing to this project, you agree to abide by its terms.

## License

`diversedata` was created by Katie Burak, Elham E. Khoda, and Stephanie Ta. It is licensed under the terms of the MIT license and Creative Commons Attribution 4.0 International license.

Data sets used in this project are licensed by their respective original creators, as indicated on each data set’s individual page. These data sets may have been adapted for use within this project.

## Credits

`diversedata` was created with [`cookiecutter`](https://cookiecutter.readthedocs.io/en/latest/) and the `py-pkgs-cookiecutter` [template](https://github.com/py-pkgs/py-pkgs-cookiecutter).
