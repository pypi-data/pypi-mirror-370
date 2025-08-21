# Singleton Package

The `singleton_package` is a simple Python package that provides a `Singleton` metaclass. This metaclass can be used to create singleton objects, ensuring that only one instance of a class exists throughout the application.

## Installation

You can install the `singleton_package` using pip:

```bash
pip install singleton_package
```

## Usage
To use the Singleton metaclass in your classes, simply specify Singleton as the metaclass:

```python
from singleton import Singleton

class MyClass(metaclass=Singleton):
    def __init__(self):
        # Your initialization code here
        pass

# Usage
instance1 = MyClass()
instance2 = MyClass()

# instance1 and instance2 will be the same object
assert instance1 is instance2
```

## Contributing
Contributions are welcome! Please feel free to submit pull requests or report any issues you encounter.

## License
This project is licensed under the MIT License - see the [LICENSE](https://opensource.org/license/mit) file for details.
