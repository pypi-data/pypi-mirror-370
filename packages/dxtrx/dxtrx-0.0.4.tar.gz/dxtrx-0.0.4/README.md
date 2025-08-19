# Dxtr Dagster Library

A Python library that provides utilities and components for data engineering workflows using Dagster. The library focuses on data processing capabilities including downloading data from Sharepoint, loading to PostgreSQL, and performing data transformations.

## Project Structure

The library is organized into the following components:

```
dxtr/
├── dxtr/     # Main library package
│   ├── dagster/          # Dagster-specific components and resources
│   └── utils/            # Utility functions
├── pyproject.toml        # Project configuration and dependencies
└── README.md            # This file
```

## Features

- Sharepoint data file downloading
- SQLAlchemy data loading
- Data transformation capabilities
- Integration with Dagster for workflow orchestration

## Dependencies

The library requires Python 3.11.8 or higher and includes key dependencies such as:
- polars
- google-cloud-storage
- requests
- msal
- pandas
- sqlalchemy
- psycopg2-binary
- and more (see pyproject.toml for complete list)

## Development

### Installation

For development purposes, install the package in editable mode:
```bash
pip install -e ".[dev] --config-settings editable_mode=compat"
```

Please refer to the Wiki to usage of `./dxtrx.sh` to setup the environment and start the Dagster code server a more convenient way of working with this code.

The library requires several environment variables to be set:
- Sharepoint credentials
- Database credentials
- Other configuration variables

Please refer to the Wiki for detailed setup instructions using `./dxtrx.sh` to configure the environment and start the Dagster code server.

### Contributing Guidelines

When contributing to this library:
1. Follow the existing code structure and naming conventions
2. Add new components in the appropriate directories
3. Update documentation as needed
4. Test changes locally
5. Submit PRs with evidence of testing and team review

#### Running tests

To run the tests, use the following command:
```bash
pytest
```

Or you can also run them in watching mode:
```bash
ptw
```

