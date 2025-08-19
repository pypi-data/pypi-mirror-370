import base64
import os
import requests
from requests.auth import HTTPBasicAuth

class PromptAPI:
    def __init__(self, ampa_url=None, username=None, password=None, api_token=None):
        if ampa_url is None:
            ampa_url = os.getenv("AMPA_API_URL", "https://ampa-api.the37lab.com/")
        if username is None:
            username = os.getenv("AMPA_API_USERNAME")
        if password is None:
            password = os.getenv("AMPA_API_PASSWORD")
        if api_token is None:
            api_token = os.getenv("AMPA_API_TOKEN")
        self.base_url = ampa_url.rstrip('/')
        if username and password:
            self.auth = HTTPBasicAuth(username, password)
            self.api_token = None
        elif api_token:
            self.auth = None
            self.api_token = api_token
        else:
            raise ValueError("Either username and password or api_token must be provided")

    def _get_headers(self):
        if self.api_token:
            return {"X-API-Token": self.api_token}
        return {}

    def create_prompt(self, **kwargs):
        url = f"{self.base_url}/api/v1/prompts"
        response = requests.post(url, params=kwargs, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def list_prompts(self):
        url = f"{self.base_url}/api/v1/prompts"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_prompt(self, prompt):
        url = f"{self.base_url}/api/v1/prompts/{prompt}"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_prompt_versions(self, prompt):
        url = f"{self.base_url}/api/v1/prompts/{prompt}/versions"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def call_prompt(self, prompt, variables=None, prompt_text=None):
        url = f"{self.base_url}/api/v1/prompts/{prompt}/call"
        params = []
        if prompt_text:
            params.append(('prompt', prompt_text))
        if variables:
            def encode_bytes(data):
                if isinstance(data, bytes):
                    return {'bytes': base64.b64encode(data).decode('utf-8')}
                elif isinstance(data, dict):
                    return {k: encode_bytes(v) for k, v in data.items()}
                elif isinstance(data, list):
                    return [encode_bytes(item) for item in data]
                return data
            variables = {k: encode_bytes(v) for k, v in variables.items()}
        response = requests.post(url, params=params, json={'var': variables}, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        if response.headers.get('Content-Type', '').startswith('text/plain'):
            return response.text
        return response.json()

    def update_prompt(self, prompt_id, **kwargs):
        url = f"{self.base_url}/api/v1/prompts/{prompt_id}/update_prompt"
        response = requests.put(url, params=kwargs, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def delete_prompt(self, prompt_id):
        url = f"{self.base_url}/api/v1/prompts/{prompt_id}"
        response = requests.delete(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def delete_prompt_version(self, prompt_id, version_id):
        url = f"{self.base_url}/api/v1/prompts/{prompt_id}/versions/{version_id}"
        response = requests.delete(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()
    
    def wiki_facts(self, entities):
        url = f"{self.base_url}/api/v1/wiki_facts"
        response = requests.post(url, auth=self.auth, headers=self._get_headers(), json=entities)
        response.raise_for_status()
        return response.json()

    def create_prompt_test(self, **kwargs):
        """Create a prompt_test row."""
        url = f"{self.base_url}/api/v1/prompt_tests"
        response = requests.post(url, json=kwargs, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def get_prompt_test(self, id):
        """Get a prompt_test by id."""
        url = f"{self.base_url}/api/v1/prompt_tests/{id}"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def update_prompt_test(self, id, **kwargs):
        """Update a prompt_test by id."""
        url = f"{self.base_url}/api/v1/prompt_tests/{id}"
        response = requests.put(url, json=kwargs, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def delete_prompt_test(self, id):
        """Delete a prompt_test by id."""
        url = f"{self.base_url}/api/v1/prompt_tests/{id}"
        response = requests.delete(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def list_prompt_tests(self):
        """List all prompt_tests."""
        url = f"{self.base_url}/api/v1/prompt_tests"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()

    def list_prompt_tests_by_prompt_id(self, prompt_id):
        """List prompt_tests by prompt id."""
        url = f"{self.base_url}/api/v1/prompts/{prompt_id}/prompt_tests"
        response = requests.get(url, auth=self.auth, headers=self._get_headers())
        response.raise_for_status()
        return response.json()