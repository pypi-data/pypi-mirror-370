# abstract_test_package

This is a Python package that facilitates testing with abstract scenarios. Utilizing PyTest, it offers extra utilities to streamline the creation and execution of abstract tests.

You can locate this package in the `abstract_essentials` project at `github.io/abstract_endeavors/abstract_essentials/abstract_test_package/`.

## Installation

You can install the `abstract_test_package` module via pip:

```sh
pip install abstract_test_package
```

Or directly from the source:

```sh
git clone https://github.io/abstract_endeavors/abstract_essentials/abstract_test_package/
cd abstract_test_package
python setup.py install
```

## Usage

Below is a usage example of the `abstract_test_package`:

```python
from abstract_test_package import create_test, execute_test

test = create_test(name="Test 1", scenario=[...])
execute_test(test)
```

This example creates an abstract test and then executes it.

## Documentation

The `abstract_test_package` module provides the following classes and functions:

### `create_test(name: str = 'Test', scenario: list = [...])`

Generates an abstract test scenario with the provided name and details.

### `execute_test(test: any)`

Executes the given abstract test scenario.

### `validate_test(test: any) -> bool`

Verifies if the given object is a valid test scenario.

### `calculate_test_results(test: any) -> dict`

Calculates the results of a given abstract test scenario.

### `compare_test_results(test1: any, test2: any) -> bool`

Compares two test scenarios and returns True if their results are equivalent, False otherwise.

... and many more!

Please refer to the source code for the complete list of classes and functions provided by the module, as well as their detailed documentation.

## Contributing

Contributions are welcome! Please fork this repository and open a pull request to add snippets, make grammar tweaks, etc.

## Contact

If you have any questions, feel free to reach out to us at partners@abstractendeavors.com.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Authors

* putkoff - main developer

This README file was last updated on May 29, 2023.
