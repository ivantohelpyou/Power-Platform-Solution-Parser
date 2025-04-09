# Solution Parser

This repository contains a Python script, `parse-entities.py`, designed to parse and extract information from a Power Platform or Dynamics 365 solution's `customizations.xml` file. The script focuses on extracting details about entities, attributes, relationships, primary keys, foreign keys, and workflows.

## Features

- **Entity Parsing**: Extracts entity names, attributes, relationships, primary keys, and foreign keys.
- **Workflow Parsing**: Extracts workflow names and their associated primary entities.
- **Custom Prefix Handling**: Strips custom publisher prefixes (`mcdev_` and `new_`) from entity and attribute names for cleaner output.
- **Error Handling**: Validates the existence of the solution folder and `customizations.xml` file before parsing.

## Requirements

- Python 3.6 or higher
- `customizations.xml` file located in the specified solution folder

## Usage

1. Clone this repository:
   ```bash
   git clone <repository-url>
   cd <repository-folder>