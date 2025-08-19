import requests
from typing import Optional, Dict, Any, List, Union, BinaryIO
import os

class PinarkiveClient:
    def __init__(self, token: Optional[str] = None, api_key: Optional[str] = None, base_url: str = 'https://api.pinarkive.com/api/v2'):
        self.base_url = base_url
        self.token = token
        self.api_key = api_key
        self.session = requests.Session()

    def _headers(self) -> Dict[str, str]:
        headers = {}
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        elif self.api_key:
            headers['X-API-Key'] = self.api_key
        return headers

    # --- Authentication ---
    def login(self, email: str, password: str) -> Any:
        return self.session.post(
            f'{self.base_url}/auth/login',
            json={'email': email, 'password': password}
        )

    def signup(self, data: Dict[str, Any], locale: Optional[str] = None, refCode: Optional[str] = None) -> Any:
        params: Dict[str, str] = {}
        if locale:
            params['locale'] = locale
        if refCode:
            params['refCode'] = refCode
        return self.session.post(
            f'{self.base_url}/auth/signup',
            json=data,
            params=params
        )

    def logout(self) -> Any:
        return self.session.post(
            f'{self.base_url}/auth/logout',
            headers=self._headers()
        )

    # --- File Management ---
    def upload_file(self, file_path: str) -> Any:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            return self.session.post(
                f'{self.base_url}/files',
                files=files,
                headers=self._headers()
            )

    def upload_directory(self, dir_path: str) -> Any:
        return self.session.post(
            f'{self.base_url}/files/directory',
            json={'dirPath': dir_path},
            headers=self._headers()
        )

    # New: Directory DAG upload
    def upload_directory_dag(self, files_dict: Dict[str, Any], dir_name: Optional[str] = None) -> Any:
        """
        Upload directory structure as DAG (Directed Acyclic Graph).
        
        Args:
            files_dict: Dictionary with file paths as keys and file content as values
            dir_name: Optional directory name for the DAG
        
        Returns:
            API response with DAG CID and file information
        """
        files = []
        for path, content in files_dict.items():
            if isinstance(content, str):
                # If content is a string, treat it as file content
                files.append(('files', (path, content, 'text/plain')))
            elif isinstance(content, (bytes, BinaryIO)):
                # If content is bytes or file-like object
                files.append(('files', (path, content, 'application/octet-stream')))
            else:
                # Try to convert to string
                files.append(('files', (path, str(content), 'text/plain')))
        
        data = {}
        if dir_name:
            data['dirName'] = dir_name
        
        return self.session.post(
            f'{self.base_url}/files/directory-dag',
            files=files,
            data=data,
            headers=self._headers()
        )

    # New: Directory cluster upload
    def upload_directory_cluster(self, files: List[Dict[str, Any]]) -> Any:
        """
        Upload directory using cluster-based approach.
        
        Args:
            files: List of dictionaries with 'path' and 'content' keys
        
        Returns:
            API response with cluster CID
        """
        files_data = []
        for file_info in files:
            path = file_info.get('path')
            content = file_info.get('content')
            if path and content is not None:
                if isinstance(content, str):
                    files_data.append(('files', (path, content, 'text/plain')))
                elif isinstance(content, (bytes, BinaryIO)):
                    files_data.append(('files', (path, content, 'application/octet-stream')))
                else:
                    files_data.append(('files', (path, str(content), 'text/plain')))
        
        return self.session.post(
            f'{self.base_url}/files/directory-cluster',
            files=files_data,
            headers=self._headers()
        )

    # New: Upload file to existing directory
    def upload_file_to_directory(self, file_path: str, dir_path: str) -> Any:
        """
        Upload a file to an existing directory.
        
        Args:
            file_path: Path to the file to upload
            dir_path: Path of the existing directory
        
        Returns:
            API response with file CID
        """
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {'dirPath': dir_path}
            return self.session.post(
                f'{self.base_url}/files/directory-files',
                files=files,
                data=data,
                headers=self._headers()
            )

    # New: Rename file
    def rename_file(self, upload_id: str, new_name: str) -> Any:
        """
        Rename an uploaded file.
        
        Args:
            upload_id: ID of the uploaded file
            new_name: New name for the file
        
        Returns:
            API response with rename status
        """
        return self.session.put(
            f'{self.base_url}/files/rename/{upload_id}',
            json={'newName': new_name},
            headers=self._headers()
        )

    def pin_cid(self, cid: str) -> Any:
        return self.session.post(
            f'{self.base_url}/files/pin/{cid}',
            headers=self._headers()
        )

    # New: Pin CID with custom name
    def pin_cid_with_name(self, cid: str, custom_name: Optional[str] = None) -> Any:
        """
        Pin a CID with an optional custom name.
        
        Args:
            cid: IPFS CID to pin
            custom_name: Optional custom name for the pinned content
        
        Returns:
            API response with pin status
        """
        data = {}
        if custom_name:
            data['customName'] = custom_name
        
        return self.session.post(
            f'{self.base_url}/files/pin/{cid}',
            json=data,
            headers=self._headers()
        )

    def remove_file(self, cid: str) -> Any:
        return self.session.delete(
            f'{self.base_url}/files/remove/{cid}',
            headers=self._headers()
        )

    # --- User Profile ---
    def get_profile(self) -> Any:
        return self.session.get(
            f'{self.base_url}/users/me',
            headers=self._headers()
        )

    def update_profile(self, data: Dict[str, Any]) -> Any:
        return self.session.put(
            f'{self.base_url}/users/me',
            json=data,
            headers=self._headers()
        )

    def list_uploads(self, page: int = 1, limit: int = 10) -> Any:
        return self.session.get(
            f'{self.base_url}/users/me/uploads',
            params={'page': page, 'limit': limit},
            headers=self._headers()
        )

    def delete_upload(self, cid: str) -> Any:
        return self.session.delete(
            f'{self.base_url}/users/me/uploads/{cid}',
            headers=self._headers()
        )

    def get_referrals(self) -> Any:
        return self.session.get(
            f'{self.base_url}/users/me/referrals',
            headers=self._headers()
        )

    # --- Token Management ---
    def generate_token(self, name: str, options: Optional[Dict[str, Any]] = None) -> Any:
        """
        Generate an API token with enhanced options.
        
        Args:
            name: Name for the token
            options: Optional dictionary with:
                - permissions: List of permissions
                - expires_in_days: Number of days until expiration
                - ip_allowlist: List of allowed IP addresses
        
        Returns:
            API response with token information
        """
        data = {'name': name}
        
        if options:
            if 'permissions' in options:
                data['permissions'] = options['permissions']
            if 'expires_in_days' in options:
                data['expiresInDays'] = options['expires_in_days']
            if 'ip_allowlist' in options:
                data['ipAllowlist'] = options['ip_allowlist']
        
        return self.session.post(
            f'{self.base_url}/tokens/generate',
            json=data,
            headers=self._headers()
        )

    def list_tokens(self) -> Any:
        return self.session.get(
            f'{self.base_url}/tokens/list',
            headers=self._headers()
        )

    def revoke_token(self, name: str) -> Any:
        return self.session.delete(
            f'{self.base_url}/tokens/revoke/{name}',
            headers=self._headers()
        )

    # --- Status and Monitoring ---
    def get_status(self, cid: str) -> Any:
        return self.session.get(
            f'{self.base_url}/status/{cid}',
            headers=self._headers()
        )

    def get_allocations(self, cid: str) -> Any:
        return self.session.get(
            f'{self.base_url}/status/allocations/{cid}',
            headers=self._headers()
        )