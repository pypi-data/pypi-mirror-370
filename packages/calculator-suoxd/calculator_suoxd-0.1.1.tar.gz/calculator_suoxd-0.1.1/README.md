# Calculator Project

## Overview
The Calculator Project is a simple yet effective tool designed to help elementary school students practice basic arithmetic operations, specifically addition and subtraction. This project provides a user-friendly interface for generating random math problems and validating user input.

## Features
- **Addition and Subtraction**: The core functionality allows users to perform addition and subtraction operations.
- **Random Problem Generation**: Utility functions generate random math problems to keep practice sessions engaging.
- **Input Validation**: Ensures that user inputs are valid integers, preventing errors during calculations.

## Installation
To install the Calculator Project, you can use pip. Run the following command in your terminal:

```
pip install calculator_project
```

## Usage
After installation, you can use the calculator in your Python scripts as follows:

```python
from calculator import Calculator

calc = Calculator()
result_add = calc.add(5, 3)  # Returns 8
result_subtract = calc.subtract(5, 3)  # Returns 2
```

## Running Tests
To ensure the functionality of the calculator, you can run the unit tests provided in the project. Navigate to the `src/tests` directory and run:

```
python -m unittest test_core.py
```

## Contributing
Contributions to the Calculator Project are welcome! If you have suggestions for improvements or new features, please feel free to submit a pull request.

## License
This project is licensed under the MIT License. See the LICENSE file for more details.