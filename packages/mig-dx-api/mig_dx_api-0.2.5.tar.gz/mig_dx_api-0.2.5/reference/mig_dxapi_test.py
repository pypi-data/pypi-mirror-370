import sys
import os
from time import sleep
import uuid
from dotenv import load_dotenv
### Uncomment below if you are using a local package ###
# Add the src directory to the Python path to import the local package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mig_dx_api import DX

load_dotenv()

# Configuration variables
APP_ID = os.getenv("APP_ID", "replace_with_your_app_id") # Replace with your Movement App ID
DATASET_NAME = f'My Test Dataset {uuid.uuid4()}'  # Unique dataset name
# UPLOAD_URL = os.getenv("UPLOAD_URL", "upload_url")  # Replace with your actual upload URL
CSV_FILE = os.getenv("CSV_FILE", "path/to/csv")  # Replace with the path to your CSV file
# Initialize the client
dx = DX(
  # Your movement app ID
  app_id=APP_ID, 
  # Your private key path (currently looks in the local directory)
  private_key_path=os.getenv("private_key_path", ".keys/privateKey.pem"),
  # You can optionally pass baseUrl if you are using a different URL than the default
  base_url=os.getenv("BASE_URL", None)
)

### Uncomment below if you are using a local test server / self-signed certificate ###
# Disable SSL verification for localhost testing
# Override the session_config method to include SSL bypass
# original_session_config = dx.session_config

# def session_config_with_ssl_bypass(self):
#     config = original_session_config()
#     config['verify'] = False  # Disable SSL verification for localhost
#     return config

# Monkey patch the session_config method
# dx.session_config = session_config_with_ssl_bypass.__get__(dx, type(dx))

# # Force reset sessions so they use the new config
# dx._session = None
# dx._asession = None
### End of SSL bypass ###
print("=== Getting User Information ===")
user_info = dx.whoami()
print(user_info)

print("=== Getting All Installations ===")
installations = dx.get_installations()
print(f"Found {len(installations)} installations:")
for installation in installations:
    print(f"  - Installation: {installation.name} (ID: {installation.installation_id})")

# Get the first installation ID
install_id = installations[0].installation_id
workspace_key = installations[0].workspace_key

print("\n=== Finding Specific Installation ===")
# Find an installation by name or ID
installation = dx.installations.find(install_id=install_id)
print(f"Found installation: {installation.name} (ID: {installation.installation_id})")

print("\n=== Using Installation Context (Method 1) ===")
# Use the installation context
with dx.installation(installation) as ctx:
    # Perform operations within the context
    datasets = list(ctx.datasets)
    print(f"Found {len(datasets)} datasets in installation '{installation.name}':")
    for dataset in datasets:
        print(f"  - Dataset: {dataset.name}")

print("\n=== Using Installation Context (Method 2) ===")
with dx.installation(install_id=install_id) as ctx:
    # Perform operations within the context
    datasets = list(ctx.datasets)
    print(f"Found {len(datasets)} datasets using install_id={install_id}:")
    for dataset in datasets:
        print(f"  - Dataset: {dataset.name}")

print("\n=== Creating New Dataset ===")
# Creating datasets
from mig_dx_api import DatasetSchema, SchemaProperty

# Define the schema
schema = DatasetSchema(
    properties=[
        SchemaProperty(name='Id', type='string', required=True),
        SchemaProperty(name='Method', type='string', required=False),
        SchemaProperty(name='RequestBody', type='string', required=False),
        SchemaProperty(name='ResponseBody', type='string', required=False),
        SchemaProperty(name='StatusCode', type='integer', required=False),
        SchemaProperty(name='Url', type='string', required=False),
        SchemaProperty(name='Path', type='string', required=False),
        SchemaProperty(name='RouteTemplate', type='string', required=False),
        SchemaProperty(name='QueryString', type='string', required=False),
        SchemaProperty(name='DateLoggedUtc', type='string', required=False),
        SchemaProperty(name='MigVid', type='string', required=False),
        SchemaProperty(name='RequestProperties', type='string', required=False),
        SchemaProperty(name='ResponseProperties', type='string', required=False),
        SchemaProperty(name='HeaderUsername', type='string', required=False),
        SchemaProperty(name='DatabaseModeId', type='integer', required=False),
        SchemaProperty(name='HashedApiKey', type='string', required=False),
    ],
    primary_key=['Id']
)
print(f"Created schema with {len(schema.properties)} properties and primary key: {schema.primary_key}")


# Create the dataset
with dx.installation(installation) as ctx:
    print(f"Creating dataset in installation: {installation.name}")

    # Get tag options
    tags = ctx.datasets.get_tags()['data']
    print(f"Found {len(tags)} tags in installation '{installation.name}':")
    # specific tag to use
    tag = [tags[0]['movementAppId'], tags[1]['movementAppId']]
    print(f"Using tags: {tag}")
    new_dataset = ctx.datasets.create(
        name=DATASET_NAME,
        description='A test dataset',
        schema=schema.model_dump(),
        tag_ids=tag
    )
    print(f"Successfully created dataset: {new_dataset.name}")

    refresh_dataset = ctx.datasets.get(new_dataset.dataset_id)
    print(f"Dataset details: {refresh_dataset}")

print("\n=== Listing All Datasets After Creation ===")
#  Listing datasets
with dx.installation(installation) as ctx:
    datasets = list(ctx.datasets)
    print(f"Total datasets in installation '{installation.name}': {len(datasets)}")
    for dataset in datasets:
        print(f"  - Dataset: {dataset.name}")

# Send some records to the dataset
data = [
    { 'my_string': "my string value", 'my_integer': 10, 'my_boolean': True},
]

with dx.installation(installation) as ctx:
    dataset_ops = ctx.datasets.find(name=DATASET_NAME)
    # job_id = dataset_ops.load(data, validate_records=True)["jobId"]  # validate_records=True will validate the records against the schema using Pydantic
    # job = ctx.datasets.get_dataset_job(job_id)
    # print(f"Job:\n{job}")
    # job_logs = ctx.datasets.get_dataset_job_logs(job_id)
    # print(f"Job Logs:\n{job_logs}")
    # job_logs_current = ctx.datasets.get_current_dataset_logs(job_id)
    # print(f"Current Job Logs:\n{job_logs_current}")

    # #retrieve records after upload
    # while job_logs_current['datasetJobStatusName'] != "Completed":
    #     sleep(5)
    #     print("Waiting for job to complete...")
    #     job_logs_current = ctx.datasets.get_current_dataset_logs(job_id)
    #     print(f"Current job status: {job_logs_current['datasetJobStatusName']}")
    #     if job_logs_current['datasetJobStatusName'] == "UnknownError":
    #         print(job_logs_current)
    #         break
        
    # print("Job completed successfully.")
    # records = dataset_ops.records()
    # print(records)
    # print(f"Retrieved {len(records)} records from dataset '{dataset_ops.name}':")

    # # replace records 
    # print("replacing records in dataset")
    # Uncomment below to replace records in the dataset using load_from_url method
    # replace_job_id = dataset_ops.load_from_url(UPLOAD_URL, mode="replace")["jobId"]
    # Uncomment below to replace records using load_from_file method

    replace_job_id = dataset_ops.load_from_file(CSV_FILE, upload_mode="create")["jobId"]
    # # Uncomment to replace records using load method
    # replace_job_id = dataset_ops.load(data, mode="replace")["jobId"]

    job_logs_current = ctx.datasets.get_current_dataset_logs(replace_job_id)
    print(f"Current Job Logs:\n{job_logs_current}")

    # #retrieve records after upload
    while job_logs_current['datasetJobStatusName'] != "Completed":
        sleep(5)
        print("Waiting for job to complete...")
        job_logs_current = ctx.datasets.get_current_dataset_logs(replace_job_id)
        print(f"Current job status: {job_logs_current['datasetJobStatusName']}")
        if job_logs_current['datasetJobStatusName'] == "UnknownError":
            print(job_logs_current)
            break
        
    print("Job completed successfully.")
    records = dataset_ops.records()
    print(records)
    print(f"Retrieved {len(records)} records from dataset '{dataset_ops.name}':")