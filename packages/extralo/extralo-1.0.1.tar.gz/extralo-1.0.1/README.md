# ETL using python

Python package for extracting data from a source, transforming it and loading it to a destination, with validation in between.

The provided ETL pipeline provides useful functionality on top of the usual operations:

- **Extract**: Extract data from multiples sources, in parallel (using threads).
- **Validate**: Validate the extracted data, to make sure it matches what will be required by the transform step, using pandera schemas. This provide early fail if there is any unexpected change in the sources.
- **Transform**: Define the logic for transformation of the data, making it reusable, and allowing multiple data frames as input and multiple data frames as output.
- **Validate again**: Validate the transformed data, to make sure it matches your expectation, and what the destination will require.
- **Load**: Load multiple data, each to one or more destination, and load diferent data to diferent destinations in parallel (using threads).

## Installation

The package is available at PyPI, so you can install it using pip:

```bash
pip install extralo
```
