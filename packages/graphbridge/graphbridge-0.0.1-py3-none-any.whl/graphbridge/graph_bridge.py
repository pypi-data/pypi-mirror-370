# pip install azure-identity requests
from azure.identity import ClientSecretCredential

import requests
from urllib.parse import quote
import json

from copy import deepcopy, copy




def deduplicate_dicts(dict_list: list[dict]) -> list[dict]:
    unique_items = []
    seen_keys = []

    for item in dict_list:
        key = json.dumps(item, sort_keys=True)
        if key not in seen_keys:
            seen_keys.append(key)
            unique_items.append(item)
    
    return unique_items




class GbAuth(object):
    def __init__(self, tenant_id: str, client_id: str, client_secret: str) -> None:
        self.__auth_name = "GbAuth"
        
        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        
        # Autenticazione app-only con ClientSecretCredential
        # self.credential
        # self.token
        # self.headers
    
    def __str__(self) -> str:
        return f"< {self.__auth_name} | Tenant ID: {self.tenant_id}, Client ID: {self.client_id}, Client Secret: {self.client_secret} >"
    
    def __repr__(self) -> str:
        return f"{self.__auth_name}(tenant_id={self.tenant_id}, client_id={self.client_id}, client_secret={self.client_secret})"
    
    @property
    def tenant_id(self) -> str:
        return self.__tenant_id
    @tenant_id.setter
    def tenant_id(self, value: str) -> None:
        if not value:
            raise ValueError(f"<ERROR {self.__auth_name} | Tenant ID cannot be empty>")
        elif not isinstance(value, str):
            raise TypeError(f"<ERROR {self.__auth_name} | Tenant ID must be string>")
        self.__tenant_id: str = value
        try:
            del self.__credential, self.__token # Reset cached properties if tenant_id changes
        except:
            ...
    
    @property
    def client_id(self) -> str:
        return self.__client_id
    @client_id.setter
    def client_id(self, value) -> str:
        if not value:
            raise ValueError(f"<ERROR {self.__auth_name} | Client ID cannot be empty>")
        elif not isinstance(value, str):
            raise TypeError(f"<ERROR {self.__auth_name} | Client ID must be string>")
        self.__client_id: str = value
        try:
            del self.__credential, self.__token # Reset cached properties if client_id changes
        except:
            ...
    
    @property
    def client_secret(self) -> str:
        return self.__client_secret
    @client_secret.setter
    def client_secret(self, value: str) -> None:
        if not value:
            raise ValueError(f"<ERROR {self.__auth_name} | Client Secret cannot be empty>")
        elif not isinstance(value, str):
            raise TypeError(f"<ERROR {self.__auth_name} | Client Secret must be string>")
        self.__client_secret: str = value
        try:
            del self.__credential, self.__token # Reset cached properties if client_secret changes
        except:
            ...
    
    @property
    def credential(self) -> ClientSecretCredential:
        """Azure AD ClientSecretCredential for authentication."""
        
        if f"_{self.__auth_name}__credential" in self.__dict__:
            return self.__credential
        else:
            self.__credential = ClientSecretCredential(self.tenant_id, self.client_id, self.client_secret)
            return self.__credential
    
    @property
    def token(self) -> str:
        """Access token for Microsoft Graph API."""
        
        if f"_{self.__auth_name}__token" in self.__dict__:
            return self.__token
        else:
            try:
                self.__token = self.credential.get_token('https://graph.microsoft.com/.default').token
                return self.__token
            except Exception as e:
                raise RuntimeError(f"<ERROR {self.__auth_name} | Failed to get token: {e}>") from e
    
    @property
    def headers(self) -> dict:
        """Headers for requests to Microsoft Graph API."""
        # Preparazione dell'header di autorizzazione per le richieste Graph
        return {'Authorization': f'Bearer {self.token}'}
    
    
    

class GbSite(GbAuth):
    """Class to handle SharePoint site operations."""
    
    def __init__(self, *args, hostname: str, site_path: str, gb_auth: GbAuth | None = None, **kwargs) -> None:
        self.__site_name = "GbSite"
        
        self.hostname = hostname
        self.site_path = site_path
        # site_url
        # site_data
        
        if gb_auth == None:
            super().__init__(*args, **kwargs)
        else:
            if not isinstance(gb_auth, GbAuth):
                raise TypeError(f"<ERROR {self.__site_name} | sp_auth must be an instance of 'SPAuth'>")
            self.__gb_auth = gb_auth
            super().__init__(tenant_id=gb_auth.tenant_id, client_id=gb_auth.client_id, client_secret=gb_auth.client_secret)
    
    def __str__(self) -> str:
        return f"< {self.__site_name} | Hostname: {self.hostname}, Site Path: {self.site_path}, Site ID: {self.site_id} >"
    
    @property
    def hostname(self) -> str:
        """Hostname of the SharePoint site."""
        return self.__hostname
    @hostname.setter
    def hostname(self, value: str) -> None:
        if not value:
            raise ValueError(f"<ERROR {self.__site_name} | Hostname cannot be empty>")
        elif not isinstance(value, str):
            raise TypeError(f"<ERROR {self.__site_name} | Hostname must be string>")
        self.__hostname: str = value
        
    @property
    def site_path(self) -> str:
        """Path of the SharePoint site."""
        
        return self.__site_path
    @site_path.setter
    def site_path(self, value: str) -> None:
        if not value:
            raise ValueError(f"<ERROR {self.__site_name} | Site path cannot be empty>")
        elif not isinstance(value, str):
            raise TypeError(f"<ERROR {self.__site_name} | Site path must be string>")
        self.__site_path: str = value
    
    @property
    def site_url(self) -> str:
        """Constructs the SharePoint site URL."""
        
        return f"https://graph.microsoft.com/v1.0/sites/{self.hostname}:{self.site_path}"
    
    @property
    def site_data(self) -> dict:
        """Fetches the SharePoint site data."""
        
        if "_SPSite__site_data" in self.__dict__:
            return self.__site_data
        else:
            site_response = requests.get(self.site_url, headers=self.headers)
            if site_response.status_code != 200:
                raise RuntimeError(f"<ERROR {self.__site_name} | Failed to set site data: {site_response.status_code} {site_response.text}>")
            self.__site_data = site_response.json()
            return self.__site_data
    
    @property
    def site_id(self) -> str:
        """Returns the ID of the SharePoint site."""
        return self.site_data.get("id", "<WARNING SPM | Site ID not found>")
    
    
    
    
class GbList(GbSite):
    """Class to handle SharePoint list operations."""
    
    def __init__(self, *args, list_name: str, gb_site: GbSite | None = None, **kwargs) -> None:
        self.__list_obj_name = "GbList"
        
        self.list_name = list_name
        
        if gb_site == None:
            super().__init__(*args, **kwargs)
        else:
            if not isinstance(gb_site, GbSite):
                raise TypeError(f"<ERROR {self.__list_obj_name} | gb_site must be an instance of 'GbSite'>")
            self.__gb_site = gb_site
            super().__init__(tenant_id=gb_site.tenant_id, client_id=gb_site.client_id, client_secret=gb_site.client_secret, 
                            hostname=gb_site.hostname, site_path=gb_site.site_path)
    
    def __str__(self) -> str:
        return f"< {self.__list_obj_name} | list_name: {self.list_name}, list_id: {self.list_id} >"
    
    def __repr__(self) -> str:
        return f"{self.__list_obj_name}(list_name={repr(self.list_name)}, hostname={repr(self.hostname)}, site_path={repr(self.site_path)}, tenant_id={repr(self.tenant_id)}, client_id={repr(self.client_id)}, client_secret={repr(self.client_secret)})"
    
    @property
    def encode_map(self) -> dict:
        """Map of characters to be URL-encoded."""
        self.__encode_map = {
            # Spazio e punteggiatura comune
            ' ': '_x0020_',
            '/': '_x002f_',
            '.': '_x002e_',
            ',': '_x002c_',
            ':': '_x003a_',
            ';': '_x003b_',
            '!': '_x0021_',
            '?': '_x003f_',
            '@': '_x0040_',
            '#': '_x0023_',
            '$': '_x0024_',
            '%': '_x0025_',
            '&': '_x0026_',
            '(': '_x0028_',
            ')': '_x0029_',
            '+': '_x002b_',
            '-': '_x002d_',
            '=': '_x003d_',
            "'": '_x0027_',
            '"': '_x0022_',
            '\\': '_x005c_',
            '*': '_x002a_',

            # Numeri da 0 a 9
            '0': '_x0030_',
            '1': '_x0031_',
            '2': '_x0032_',
            '3': '_x0033_',
            '4': '_x0034_',
            '5': '_x0035_',
            '6': '_x0036_',
            '7': '_x0037_',
            '8': '_x0038_',
            '9': '_x0039_',

            # Lettere accentate (facoltativo, se usi nomi internazionali)
            'à': '_x00e0_',
            'è': '_x00e8_',
            'é': '_x00e9_',
            'ì': '_x00ec_',
            'ò': '_x00f2_',
            'ù': '_x00f9_',
            'ç': '_x00e7_',

            # Simboli matematici e vari
            '<': '_x003c_',
            '>': '_x003e_',
            '[': '_x005b_',
            ']': '_x005d_',
            '{': '_x007b_',
            '}': '_x007d_',
            '^': '_x005e_',
            '`': '_x0060_',
            '|': '_x007c_',
            '~': '_x007e_',
        }
        return self.__encode_map
    
    @property
    def decode_map(self) -> dict:
        """Map of URL-encoded characters to their original form."""
        
        self.__decode_map = {v: k for k, v in self.encode_map.items()}
        return self.__decode_map
    
    def decode_row(self, row: dict) -> dict:
        """Decodes the keys of a row dictionary using the decode_map."""
        
        decoded_row = {}
        for k, v in row.items():
            decoded_k = copy(k)
            for char, decoded_char in self.decode_map.items():
                if char in k:
                    decoded_k = decoded_k.replace(char, decoded_char)
            decoded_row[decoded_k] = v
        return decoded_row
    
    def encode_row(self, row: dict) -> dict:
        """Encodes the keys of a row dictionary using the encode_map."""
        
        encoded_row = {}
        for k, v in row.items():
            encoded_k = copy(k)
            for char, encoded_char in self.encode_map.items():
                if char in k:
                    encoded_k = encoded_k.replace(char, encoded_char)
            encoded_row[encoded_k] = v
        return encoded_row
    
    @property
    def list_name(self) -> str:
        """Name of the SharePoint element."""
        return self.__list_name
    @list_name.setter
    def list_name(self, value: str) -> None:
        if not value:
            raise ValueError(f"<ERROR {self.__list_obj_name} | Name cannot be empty>")
        elif not isinstance(value, str):
            raise TypeError(f"<ERROR {self.__list_obj_name} | Name must be string>")
        self.__list_name: str = value
    
    @property
    def list_url(self) -> str:
        """Constructs the URL for the SharePoint list."""
        
        return f"https://graph.microsoft.com/v1.0/sites/{self.site_id}/lists/{quote(self.list_name)}"
    
    @property
    def list_data(self) -> dict:
        """Fetches the SharePoint list data."""
        
        if f"_{self.__list_obj_name}__list_data" in self.__dict__:
            return self.__list_data
        else:
            element_response = requests.get(self.list_url, headers=self.headers)
            if element_response.status_code != 200:
                raise RuntimeError(f"<ERROR {self.__list_obj_name} | Failed to set element data: {element_response.status_code} {element_response.text}>")
            self.__list_data = element_response.json()
            return self.__list_data
        
    @property
    def list_id(self) -> str:
        """Returns the ID of the SharePoint list."""
        
        return self.list_data.get("id", f"<WARNING {self.__list_obj_name} | Element ID not found>")
    
    @property
    def list_items(self) -> list:
        """Fetches all items in the SharePoint list."""
        
        items_url = f"{self.list_url}/items?expand=fields"
        items_response = requests.get(items_url, headers=self.headers)
        if items_response.status_code != 200:
            raise RuntimeError(f"<ERROR {self.__list_obj_name} | Failed to fetch list items: {items_response.status_code} {items_response.text}>")
        self.__list_items = items_response.json().get("value", [])
        return self.__list_items
    
    @property
    def list_rows(self) -> list[dict]:
        """Fetches all rows in the SharePoint list with their fields."""
        
        self.__list_rows = [item["fields"] for item in self.list_items]
        return self.__list_rows
    
    @property
    def list_ids(self) -> list[str]:
        """Fetches all IDs of items in the SharePoint list."""
        
        return [item.get("id") for item in self.list_items if "id" in item]
    
    @property
    def list_fields(self) -> list[str]:
        """Fetches all field names in the SharePoint list."""
        
        return [field for field in list(self.list_rows[0].keys())] if self.list_rows != [] else []
    
    
    def get_items_by_features(self, features: list[dict]) -> list[dict[str, object]]:
        """
        Return SharePoint list items that match at least ONE of the provided feature
        sets (logical OR across the dicts in `features`). Within each single feature
        dict, all key/value pairs must match (logical AND). One level of nesting is
        supported (e.g., {"Field": {"SubField": value}}).

        Args:
            features (list[dict]): A list of criteria dictionaries. Each dict may
                contain:
                - flat pairs {field: value} for direct comparisons; and/or
                - nested pairs {field: {sub_field: value}} for nested comparisons.

        Returns:
            list[dict]: A de-duplicated list of items that satisfy at least one dict
            in `features`.

        Example:
            features = [
                {"Status": "Active"},
                {"Category": {"Name": "Premium"}}
            ]
            items = obj.get_items_by_features(features)
        """

        
        items = []
        for feature in features:
            for item in self.list_items:
                has_features = []
                for k, v in feature.items():
                    if not isinstance(v, dict):
                        has_features.append(item.get(k) == v)
                    else:
                        nested_has_features = []
                        for nested_k, nested_v in v.items():
                            nested_has_features.append(item.get(k, {}).get(nested_k) == nested_v)
                        has_features.append(all(nested_has_features))
                
                if all(has_features):
                    items.append(item)
            
            # if all(item.get(k) == v if not isinstance(v, dict) else all(item.get(k, {}).get(nested_k) == nested_v for nested_k, nested_v in v.items()) for k, v in feature.items()):
            #     items.append(item)
        return deduplicate_dicts(items)
    
    
    def update(self, ids: str | int | list[str] | tuple[str] | set[str], rows: dict | list[dict] | tuple[dict]) -> dict[str, list[dict[str, object]]]:
        """
        Update one or more SharePoint list items by their IDs.

        IDs and rows can be single values or sequences; the method normalizes them to
        lists and requires a 1:1 correspondence (same length).

        Args:
            ids (str | int | list[str] | tuple[str] | set[str]): A single ID or a
                collection of IDs. Single values are accepted and will be converted.
            rows (dict | list[dict] | tuple[dict]): Update payload (field/value pairs)
                for each ID. A single dict is accepted and will be converted to a list.

        Returns:
            dict: A result object with:
                - "successes": list of {"id", "success", "updated_row"}
                - "failures":  list of {"id", "success", "error"}

        Raises:
            TypeError: If `rows` or `ids` cannot be converted to a list as required.
            ValueError: If the number of `ids` does not match the number of `rows`.

        Note:
            Although the type hint says `-> bool`, this function actually returns a
            result dictionary with "successes"/"failures".
        """
        
        if isinstance(rows, dict):
            rows = [rows]
        elif not isinstance(rows, list):
            try:
                rows = list(rows)
            except TypeError:
                raise TypeError(f"<ERROR {self.__list_obj_name} | rows must be a list, tuple or dict>")
        
        if isinstance(ids, str | int):
            ids = [ids]
        elif not isinstance(ids, list):
            try:
                ids = list(ids)
            except TypeError:
                raise TypeError(f"<ERROR {self.__list_obj_name} | IDs must be a list, tuple, set or string>")
        
        if len(ids) != len(rows):
            raise ValueError(f"<ERROR {self.__list_obj_name} | Number of IDs must match number of rows to update>")
        
        update_successes: list = []
        update_failures: list = []
        for i, id in enumerate(ids):
            row = rows[i]
            
            update_url: str = f"{self.list_url}/items/{id}/fields"
            update_response: requests.Response = requests.patch(update_url, headers={**self.headers, "Content-Type": "application/json"}, json=row)
            
            if update_response.status_code == 200:
                updated_row: dict = update_response.json()
                update_successes.append({"id": updated_row.get("id", None), "success": True, "updated_row": updated_row})
            else:
                update_failures.append({"id": id, "success": False, "error": f"Error updating: {update_response.status_code} {update_response.text}"})
        
        return {"successes": update_successes, "failures": update_failures}
        
        
    def create(self, rows: dict | list[dict] | tuple[dict] | set[dict]) -> dict[str, list[dict[str, object]]]:
        """
        Create one or more new items in the SharePoint list.

        Each row is wrapped as {"fields": row} before being sent to the creation
        endpoint.

        Args:
            rows (dict | list[dict] | tuple[dict] | set[dict]): Field data for new
                items. You may pass a single dict or a collection of dicts; non-list
                inputs are converted.

        Returns:
            dict: A result object with:
                - "successes": list of {"id", "success", "item"}
                - "failures":  list of {"success", "error"}

        Raises:
            TypeError: If any row is not a dict, or if `rows` cannot be converted to a
                collection of dicts.

        Note:
            The return annotation is `dict[str, dict]`, but the actual return value is
            a dictionary containing lists of outcome records.
        """

        if isinstance(rows, dict):
            rows = [{"fields": rows}]
        elif not isinstance(rows, list):
            try:
                rows = list(rows)
                rows = [{"fields": row} for row in rows]
            except TypeError:
                raise TypeError(f"<ERROR {self.__list_obj_name} | rows must be a list, tuple, set or dict>")
        else:
            rows = [{"fields": row} for row in rows]

        for new_row in rows:
            if not isinstance(new_row, dict):
                raise TypeError(f"<ERROR {self.__list_obj_name} | Each row must be a dictionary>")
        
        create_successes: list = []
        create_failures: list = []
        for new_row in rows:
            create_url: str = self.list_url + "/items"
            create_resp: requests.Response = requests.post(create_url, headers={**self.headers, "Content-Type": "application/json"}, json=new_row)

            if create_resp.status_code == 201:
                item_created: dict = create_resp.json()
                create_successes.append({"id": item_created.get("id", None), "success": True, "item": item_created})
            else:
                create_failures.append({"success": False, "error": f"Error while creating a new item: {create_resp.status_code} {create_resp.text}"})
        
        return {"successes": create_successes, "failures": create_failures}


    def delete(self, ids: str | list[str] | tuple[str] | set[str]) -> dict[str, list[dict[str, object]]]:
        """
        Delete one or more SharePoint list items by ID.

        Args:
            ids (str | list[str] | tuple[str] | set[str]): A single ID or a collection
                of IDs. Single values are converted to a list.

        Returns:
            dict: A result object with:
                - "successes": list of {"id", "completed", "message"}
                - "failures":  list of {"id", "completed", "error"}

        Raises:
            TypeError: If `ids` cannot be converted to a list.
            ValueError: If `ids` is empty.

        Note:
            The delete endpoint returns HTTP 204 on success.
        """

        if isinstance(ids, str):
            ids = [ids]
        elif not isinstance(ids, list):
            try:
                ids = list(ids)
            except TypeError:
                raise TypeError(f"<ERROR {self.__list_obj_name} | IDs must be a list, tuple, set or string>")
        
        if not ids:
            raise ValueError(f"<ERROR {self.__list_obj_name} | IDs cannot be empty>")
        
        del_successes: list = []
        del_failures: list = []
        for id in ids:
            del_url: str = f"{self.list_url}/items/{id}"
            del_resp: requests.Response = requests.delete(del_url, headers=self.headers)
            
            if del_resp.status_code == 204:
                del_successes.append({"id": id, "completed": True, "message": "Item deleted successfully."})
            else:
                del_failures.append({"id": id, "completed": False, "error": f"Error while deleting: {del_resp.status_code} {del_resp.text}"})
        
        return {"successes": del_successes, "failures": del_failures}
    
    
    def upload(self, ids: str | int | list[str | int] | tuple[str | int] | set[str | int], rows: dict | list[dict] | tuple[dict], force: bool = False, delete: bool = False) -> dict[str, dict[str, object]]:
        """
        Uploads items to a SharePoint list using the provided rows data.

        Parameters:
        - rows (list[dict]): A list of dictionaries, each containing the fields values for an item to be uploaded.
        - force (bool): If True, replaces existing items with the same ID. If False, updates them without full replacement.
        - delete (bool): If True, deletes all existing items whose IDs are not present in ids. If False, updates only items with matching IDs, leaving others unchanged.
        
        Upsert items into the SharePoint list with optional replacement and cleanup.

        Behavior:
            - If `delete=True`, remove existing items whose IDs are NOT present in `ids`
            (i.e., old_ids - ids).
            - For each ID in `ids`:
                * If the ID exists:
                    - `force=True`: delete the existing item and create a new one.
                    - `force=False`: patch-update the existing item.
                * If the ID does not exist: create a new item.

        Args:
            ids (str | int | list[str | int] | tuple[str | int] | set[str | int]):
                A single ID or a collection of IDs. All values are converted to strings.
            rows (dict | list[dict] | tuple[dict]): Field data for each ID. A single
                dict is accepted; every element must be a dict.
            force (bool): If True, fully replace existing items (delete + create).
                If False, perform a patch update.
            delete (bool): If True, delete items not included in `ids`. If False, do
                not delete anything.

        Returns:
            dict: An object with two sections:
                {
                "delete_results": {
                    "successes": list | None,
                    "failures":  list | None
                },
                "force_results": {
                    "replaced": {"successes": list, "failures": list},
                    "updated":  {"successes": list, "failures": list},
                    "created":  {"successes": list, "failures": list}
                }
                }

        Raises:
            TypeError: If `ids` or `rows` are not in acceptable/convertible formats,
                or if `force`/`delete` are not booleans.
            ValueError: If the counts of `ids` and `rows` differ.

        Note:
            IDs and rows are validated and normalized before processing.
        """
    
        # check ids
        if isinstance(ids, str | int):
            ids: list = [str(ids)]
        elif not isinstance(ids, list):
            try:
                ids: list = list(ids)
                ids: list = [str(i) for i in ids]
            except TypeError:
                raise TypeError(f"<ERROR {self.__list_obj_name} | IDs must be a list, tuple, set, string or integer>")
        
        # check rows
        if isinstance(rows, dict):
            rows: list = [rows]
        elif not isinstance(rows, list):
            try:
                rows: list = list(rows)
            except TypeError:
                raise TypeError(f"<ERROR {self.__list_obj_name} | rows must be a list, tuple or dict>")
        if not all(isinstance(row, dict) for row in rows):
            raise TypeError(f"<ERROR {self.__list_obj_name} | Each row must be a dictionary>")
        
        # check if ids and rows have the same length
        if len(ids) != len(rows):
            raise ValueError(f"<ERROR {self.__list_obj_name} | Number of IDs must match number of rows to upload>")
        
        # check force and delete parameters
        if not isinstance(force, bool):
            raise TypeError(f"<ERROR {self.__list_obj_name} | force must be a boolean>")
        if not isinstance(delete, bool):
            raise TypeError(f"<ERROR {self.__list_obj_name} | delete must be a boolean>")
        
        old_rows: list[dict] = self.list_rows
        old_ids: list[str] = self.list_ids
        
        delete_results: dict = {}
        if delete:
            ids_to_delete: set[str] = set(old_ids) - set(ids)
            if ids_to_delete:
                del_status: dict = self.delete(ids=ids_to_delete)
                delete_results["successes"] = del_status.get("successes", [])
                delete_results["failures"] = del_status.get("failures", [])
            else:
                delete_results["successes"] = []
                delete_results["failures"] = []
        else:
            delete_results["successes"] = None
            delete_results["failures"] = None
            
        
        force_results: dict = {
            "replaced": {"successes": [], "failures": []}, 
            "updated": {"successes": [], "failures": []}, 
            "created": {"successes": [], "failures": []}
        }
        for i, id in enumerate(ids):
            row = rows[i]
            
            if id in old_ids:
                if force:
                    # Replace the entire item by deleting and creating a new one
                    del_status: dict = self.delete(ids=[id])
                    if del_status.get("successes"):
                        create_status: dict = self.create(rows=[row])
                        if create_status.get("successes"):
                            force_results["replaced"]["successes"].append({"id": id, "row": row, "new_id": create_status.get("successes")[0].get("id")})
                        else:
                            force_results["replaced"]["failures"].append({"id": id, "row": row, "error": create_status.get("failures")[0].get("error")})
                    else:
                        force_results["replaced"]["failures"].append({"id": id, "row": row, "error": del_status.get("failures")[0].get("error")})
                else:
                    # Update the existing item
                    update_status: dict = self.update(ids=[id], rows=[row])
                    if update_status.get("successes"):
                        force_results["updated"]["successes"].append({"id": id, "row": row})
                    else:
                        force_results["updated"]["failures"].append({"id": id, "row": row, "error": update_status.get("failures")[0].get("error")})
            else:
                # Create a new item
                create_status: dict = self.create(rows=[row])
                if create_status.get("successes"):
                    force_results["created"]["successes"].append({"id": id, "row": row, "new_id": create_status.get("successes")[0].get("id")})
                else:
                    force_results["created"]["failures"].append({"id": id, "row": row, "error": create_status.get("failures")[0].get("error")})
            
        return {"delete_results": delete_results, "force_results": force_results}
