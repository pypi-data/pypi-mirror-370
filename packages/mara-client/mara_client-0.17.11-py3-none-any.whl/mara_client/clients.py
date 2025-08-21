import requests
from typing import List, Optional, Union
from .models import ChatFile, ChatResult, DataTable
from . import utils


DEFAULT_URL = 'https://mara.nanome.ai'


class MARAClient:
    """A client for the MARA conversational agent for cheminformatics."""

    def __init__(self, api_key: str, url: str = DEFAULT_URL):
        self.api_key = api_key
        self.url = url

    def new_chat(self):
        """Start a new chat with MARA."""
        return Chat(self)

    def get_chat(self, chat_id):
        """Get an existing chat with MARA."""
        return Chat(self, chat_id)

    def _request(self, path, method='POST', headers={}, json={}, **kwargs) -> requests.Response:
        if self.api_key:
            headers = {**headers, 'Authorization': f'Bearer {self.api_key}'}
        r = requests.request(method, f'{self.url}/api/{path}', headers=headers, json=json, **kwargs)
        if r.status_code == 403:
            raise ValueError('Invalid API key')
        if not r.ok:
            raise ValueError(f'Error {r.status_code}: {r.text}')
        return r

    def run_molstar_chain(self, prompt: str) -> str:
        """Run the Mol* update prompt and return the result."""
        path = 'prompt/molstar'
        payload = {'input': prompt}
        resp = self._request(path=path, json=payload)
        return resp.json()


class DataTableManager:
    """A submanager for data tables in the MARA Chat."""

    def __init__(self, client: MARAClient, chat_id: str = None):
        self.client = client
        self.chat_id = chat_id

    def list(self) -> List[dict]:
        """List all data tables in the chat."""
        path = f'chats/{self.chat_id}/datasets'
        resp = self.client._request(method='GET', path=path)
        return resp.json()

    def create(self, filepath: str = None, file_id: str = None) -> DataTable:
        """Create a data table from a new file or previoiusly uploaded file with id."""
        path = f'chats/{self.chat_id}/datasets'
        payload = {'stream': False}
        if file_id and filepath:
            raise ValueError('Specify either a file path or a file ID, not both')
        if not file_id and not filepath:
            raise ValueError('Specify a file path or a file ID')
        if filepath:
            with open(filepath, 'rb') as file:
                files_payload = {'file': file}
                resp = self.client._request(method='POST', data=payload, path=path, files=files_payload)
        elif file_id:
            payload['file_id'] = file_id
            resp = self.client._request(method='POST', path=path, json=payload)
        return DataTable(**resp.json())

    def get(self, datatable_id: int) -> DataTable:
        """Get a data table by ID. Return the data table."""
        path = f'chats/{self.chat_id}/datasets/{datatable_id}'
        resp = self.client._request(method='GET', path=path)
        return DataTable(**resp.json())

    def delete(self, datatable_id: int) -> None:
        """Delete a data table by ID."""
        path = f'chats/{self.chat_id}/datasets/{datatable_id}'
        self.client._request(method='DELETE', path=path)

    def prompt(self, datatable_id: int, prompt: str) -> ChatResult:
        """Prompt the chat with a message and a data table. Return the result."""
        path = f'chats/{self.chat_id}/datasets/{datatable_id}'
        data = {'input': prompt}
        resp = self.client._request(path=path, json=data)
        return ChatResult.from_response(resp.text)

    def generate(self) -> DataTable:
        """Generate a data table from the chat."""
        path = f'chats/{self.chat_id}/datasets/generate'
        resp = self.client._request(method='POST', path=path)
        sse_event_list = utils.sse_stream_to_dict_list(resp.content)
        final_table_event = next((d for d in sse_event_list if d.get('event') == 'FINAL_TABLE'), None)
        if final_table_event is None:
            raise ValueError('No FINAL_TABLE event found in the generate() response')
        table_data = final_table_event.get('data')
        table_value = table_data.get('value')
        table_value = final_table_event.get('data', {}).get('value')
        if table_value is None:
            raise ValueError('No final table found in the Server-Sent Event')
        datatable_payload = {
            'id': table_data['id'],
            'page': 1,
            'total': len(table_value),
            'pages': 1,
            'name': 'Generated Payload',
            'modifications': table_data['modifications'],
            'table': table_value
        }
        datatable = DataTable(**datatable_payload)
        return datatable


class FileManager:

    def __init__(self, client: MARAClient, chat_id: str = None):
        self.client = client
        self.chat_id = chat_id

    def upload(self, filepath: str) -> ChatFile:
        path = f'chats/{self.chat_id}/files'
        resp = self.client._request(
            method='POST',
            path=path,
            json=None,
            files={'file': open(filepath, 'rb')}
        )
        return ChatFile(**resp.json())

    def list(self) -> List[dict]:
        """List all files in the chat."""
        path = f'chats/{self.chat_id}/files'
        resp = self.client._request(method='GET', path=path)
        return resp.json()

    def download(self, filename: str, out_filename: Optional[str] = None) -> str:
        """Download a file from the chat to the current working directory. Return the filename."""
        path = f'chats/{self.chat_id}/files/{filename}'
        resp = self.client._request(method='GET', path=path)
        if out_filename is None:
            out_filename = filename
        with open(out_filename, 'wb') as f:
            f.write(resp.content)
        return out_filename


class Chat:
    """A chat with the MARA conversational agent for cheminformatics."""

    datatables: DataTableManager
    files: FileManager

    def __init__(self, client: MARAClient, chat_id: str = None):
        self.client = client
        self.chat_id = chat_id
        if chat_id is None:
            r = self.client._request(path='chats')
            self.chat_id = r.json()['id']
        self.datatables = DataTableManager(client, self.chat_id)
        self.files = FileManager(client, self.chat_id)

    def delete(self) -> None:
        """Delete the chat and all of its data and files."""
        self.client._request(method='DELETE', path=f'chats/{self.chat_id}')

    def prompt(self, content: str, files: List[Union[str, ChatFile]] = None) -> ChatResult:
        """Prompt the chat with a message and optional files. Return the result."""
        files = files or []

        file_ids = []
        for fi in files:
            if isinstance(fi, str):
                fi = self.files.upload(fi)
            elif not isinstance(fi, ChatFile):
                raise ValueError('Files must be either string file paths or ChatFile objects')
            file_ids.append(fi.id)
        data = {'content': content, 'files': file_ids}
        path = f'chats/{self.chat_id}'
        r = self.client._request(path=path, json=data)
        return ChatResult.from_response(r.text)

    def get_context(self) -> str:
        """Get the context of the chat."""
        chat: dict = self.get_details()
        return chat['context']

    def set_context(self, context: str) -> None:
        """Get the context of the chat."""
        path = f'chats/{self.chat_id}/context'
        payload = {'context': context}
        resp = self.client._request(path=path, json=payload)
        if not resp.ok:
            raise ValueError(f'Error {resp.status_code}: {resp.text}')

    def get_details(self) -> dict:
        """Get the details of the chat."""
        path = f'chats/{self.chat_id}'
        resp = self.client._request(path=path, method='GET')
        return resp.json()
