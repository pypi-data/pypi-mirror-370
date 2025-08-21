# mara client module

This package provides a Python interface for the MARA conversational agent for cheminformatics.

## Installation

```bash
pip install mara-client
```

## Usage

To use the MARA client, you need to have an API key. You can create one at https://mara.nanome.ai/settings/api-keys.

MARA chats are created using the `new_chat` method, or retrieved with the `get_chat` method of the client. You can then interact with the chat using the `prompt` method. The `prompt` method returns a `ChatResult` object, which contains the response from MARA, intermediate messages such as tool runs, and any files that were generated during the conversation. You can download these files using the `download_file` method of the chat. Chat will be visible as conversations in the MARA web interface, and can be deleted using the `delete` method.

```python
from mara_client import MARAClient

API_KEY = "..."
URL = "https://mara.example.com" # optional
client = MARAClient(API_KEY, URL)

chat = client.new_chat()
# or, chat = client.get_chat("chat_id")

result = chat.prompt('Download SDF of aspirin')
print(result.response)
# The SDF file for the compound aspirin has been downloaded successfully. You can access it [here](CHEMBL25.sdf).
print(result.files)
# [ChatFile(id='...', name='CHEMBL25.sdf', size=1203, date=...)]

chat.files.download('CHEMBL25.sdf', 'aspirin.sdf')
# downloaded as aspirin.sdf in current working directory

result = chat.prompt('Calculate chem props')
print(result.response)
# The chemical properties of the compound with ChEMBL ID CHEMBL25 (aspirin) are as follows:
#
# | Property | Value |
# | --- | --- |
# | Molecular Weight (MW) | 180.159 |
# | LogP | 1.310 |
# | Total Polar Surface Area (TPSA) | 63.600 |
# | Hydrogen Bond Acceptors (HBA) | 3 |
# | Hydrogen Bond Donors (HBD) | 1 |
# | Rotatable Bonds (RB) | 2 |

chat.delete()
# remove chat from history, delete associated files and data
```

### Files

The chat object contains a `files` attribute for working with files.

```python
# Upload a file as part of a prompt
file_path = './example.sdf'
result = chat.prompt('Convert this to SMILES', files=[file_path])

# List all files
file_list = chat.files.list()

# Download a file
file_name = file_list[0].name
chat.files.download(file_name, 'output.sdf')

# Upload a file directly
file_path = './example.sdf'
file = chat.files.upload(file_path)
print(file.id)
```

### Data Tables

The chat object contains a `datatables` attribute for working with DataTables.

```python
# Create a data table from already uploaded file
csv_file = './example.csv'
datatable: DataTable = chat.datatables.create(csv_file)

# List all data tables
table_list = chat.datatables.list()

# Generate a new DataTable based on Chat context
chat.datatables.generate()

# Run prompt to update/query a datatable
dt_id = datatable.id
chat.datatables.prompt(dt_id, prompt)

# Retrieve a datatable
chat.datatables.get(dt_id)

# View datatable as a pandas Dataframe
df = datatable.dataframe
```
