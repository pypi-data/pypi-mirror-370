# DX API Client Library

Welcome to the **DX API Client Library**! This library provides a convenient Python interface to interact with the DX API, allowing you to manage datasets, installations, and perform various operations with ease.

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Prerequisites](#prerequisites)
- [Getting Started](#getting-started)
  - [Authentication](#authentication)
  - [Initialization](#initialization)
- [Usage](#usage)
  - [Who Am I](#who-am-i)
  - [Managing Installations](#managing-installations)
    - [Listing Installations](#listing-installations)
    - [Accessing an Installation Context](#accessing-an-installation-context)
  - [Managing Datasets](#managing-datasets)
    - [Listing Datasets](#listing-datasets)
    - [Creating a Dataset](#creating-a-dataset)
    - [Creating a Dataset with specific tags](#creating-a-dataset-with-specific-tags)
    - [Uploading Data to a Dataset](#uploading-data-to-a-dataset)
    - [Getting Dataset Jobs](#dataset-jobs)
    - [Retrieving Records from a Dataset](#retrieving-records-from-a-dataset)
- [Asynchronous Usage](#asynchronous-usage)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)

## Features

- Authenticate with the DX API using JWT tokens.
- Manage installations and datasets.
- Upload and download data to and from datasets.
- Synchronous and asynchronous support.
- Context managers for handling authentication scopes.

## Installation

You can install the library using `pip`:

```bash
pip install mig-dx-api
```

## Prerequisites

- Python 3.10 or higher.
- An application ID (`app_id`) and a corresponding private key in PEM format.
- DX API access credentials.

## Getting Started

### Authentication

The library uses JWT tokens for authentication. You need to provide your `app_id` and the path to your private key file when initializing the client.

### Initialization

```python
from mig_dx_api import DX

# Initialize the client
dx = DX(app_id='your_app_id', private_key_path='path/to/private_key.pem')

# OR
dx = DX(app_id='your_app_id', private_key='your_private_key')
```

Alternatively, you can set the environment variables `DX_CONFIG_APP_ID` and `DX_CONFIG_PRIVATE_KEY_PATH`:

```bash
export DX_CONFIG_APP_ID='your_app_id'
export DX_CONFIG_PRIVATE_KEY_PATH='path/to/private_key.pem'

# OR
export DX_CONFIG_PRIVATE_KEY='your_private_key'
```

And initialize the client without arguments:

```python
dx = DX()
```

## Usage

### Who Am I

Retrieve information about the authenticated user:

```python
user_info = dx.whoami()
print(user_info)
```

### Managing Installations

#### Listing Installations

```python
installations = dx.get_installations()
for installation in installations:
    print(installation.name)
```

#### Accessing an Installation Context

Use the installation context to perform operations related to a specific installation:

```python
# Find an installation by name or ID
installation = dx.installations.find(install_id=1)

# Use the installation context
with dx.installation(installation) as ctx:
    # Perform operations within the context
    datasets = list(ctx.datasets)
    for dataset in datasets:
        print(dataset.name)
```

Or enter context with a lookup by name:

```python

with dx.installation(install_id=1) as ctx:
    # Perform operations within the context
    datasets = list(ctx.datasets)
    for dataset in datasets:
        print(dataset.name)


```

### Managing Datasets

#### Listing Datasets

```python
with dx.installation(installation) as ctx:
    for dataset in ctx.datasets:
        print(dataset.name)
```

#### Creating a Dataset

```python
from mig_dx_api import DatasetSchema, SchemaProperty

# Define the schema
schema = DatasetSchema(
    properties=[
        SchemaProperty(name='my_string', type='string', required=True),
        SchemaProperty(name='my_integer', type='integer', required=True),
        SchemaProperty(name='my_boolean', type='boolean', required=False),
    ],
    primary_key=['my_string']
)

# Create the dataset
with dx.installation(installation) as ctx:
    new_dataset = ctx.datasets.create(
        name='My Dataset',
        description='A test dataset',
        schema=schema.model_dump()  # this can also be defined as a dictionary
    )
```
### Creating a Dataset with specific tags
```python
# Get tag options
with dx.installation(installation) as ctx:
    tag_options = ctx.datasets.get_tags
    tags = [tags['data'][0]['movementAppId'], tags['data'][1]['movementAppId']]
    new_dataset = ctx.datasets.create(
        name='My Tagged Dataset',
        description='A test tagged dataset',
        schema={
            "primaryKey": ["my_van_id"],
            "properties": [
                {"name": "my_van_id", "type": "string"},
                {"name": "first_name", "type": "string"},
                {"name": "last_name", "type": "string"},
            ],
        },
        tagIds=[tags]
    )
```

#### Uploading Data to a Dataset

```python
data = [
    {'my_string': 'string1', 'my_integer': 1, 'my_boolean': True},
    {'my_string': 'string2', 'my_integer': 2, 'my_boolean': False},
    {'my_string': 'string3', 'my_integer': 3, 'my_boolean': True},
]

with dx.installation(installation) as ctx:
    dataset_ops = ctx.datasets.find(name='My Dataset')
    dataset_ops.load(data, validate_records=True)  # validate_records=True will validate the records against the schema using Pydantic
```
#### Dataset Jobs
```python
with dx.installation(installation) as ctx:
    dataset_ops = ctx.datasets.find(name='My Dataset')
    # Job Id comes from load, load_from_file or load_from_url
    job_id = dataset_ops.load(data, validate_records=True)["jobId"]
    # Get dataset job
    job = ctx.datasets.get_dataset_job(job_id)
    # Get logs for dataset job
    job_logs = ctx.datasets.get_dataset_job_logs(job_id)
    # Get latest status for dataset job
     job_logs_current = ctx.datasets.get_current_dataset_logs(job_id)

```
#### Retrieving Records from a Dataset

```python
with dx.installation(installation) as ctx:
    dataset_ops = ctx.datasets.find(name='My Dataset')
    records = dataset_ops.records()
    for record in records:
        print(record)
```

## Asynchronous Usage

The library supports asynchronous operations using `async`/`await`.

```python
import asyncio

async def main():
    dx = DX()
    async with dx.installation(installation) as ctx:
        async for dataset in ctx.datasets:
            print(dataset.name)

        dataset = await ctx.datasets.find(name='My Dataset')

        data = [
            {'my_string': 'string1', 'my_integer': 1, 'my_boolean': True},
            {'my_string': 'string2', 'my_integer': 2, 'my_boolean': False},
            {'my_string': 'string3', 'my_integer': 3, 'my_boolean': True},
        ]

        await dataset.load(data)

        async for record in dataset.records():
            print(record)

asyncio.run(main())
```

## Examples

### Example: Loading Data from a File

```python
with dx.installation(installation) as ctx:
    dataset_ops = ctx.datasets.find(name='My Dataset')
    dataset_ops.load_from_file('data.csv')
```

### Example: Uploading Data from a URL

```python
with dx.installation(installation) as ctx:
    dataset_ops = ctx.datasets.find(name='My Dataset')
    dataset_ops.load_from_url('https://example.com/data.csv')
```



---

*Note: This README assumes that the package name is `mig-dx-api` and that the code is properly packaged and available for installation via `pip`. Adjust the instructions accordingly based on the actual package name and installation method.*