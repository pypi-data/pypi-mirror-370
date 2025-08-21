# GbSharePoint (GbAuth · GbSite · GbList)

A small Python wrapper to work with **Microsoft Graph** and **SharePoint Lists** using **app-only** authentication (Client Credentials).

> The library includes the classes `GbAuth`, `GbSite`, `GbList` and a couple of utilities (`deduplicate_dicts`, field name encoding/decoding).

---

## Requirements

* **Python** ≥ 3.10
* An app registered in **Microsoft Entra ID** (Azure AD) with **Application Permissions** to Microsoft Graph:

  * Read: `Sites.Read.All` (minimum)
  * Write (CRUD): `Sites.ReadWrite.All`
  * Alternatively (recommended for least privilege): **Sites.Selected** + grant site-level access.
* **Admin consent** granted for the app permissions.

## Installation

```bash
pip install azure-identity requests
```

---

## Key concepts

* **GbAuth**: handles credentials and acquires the Graph bearer token (`ClientSecretCredential`).
* **GbSite**: resolves a SharePoint **site id** from `hostname` and `site_path`.
* **GbList**: performs list operations (`list_items`, `list_rows`, `create`, `update`, `delete`, `upload`, …).

All requests target the **v1.0** Graph endpoint (`https://graph.microsoft.com/v1.0`).

---

## Quickstart

```python
from gbsharepoint import GbAuth, GbSite, GbList  # or import from your own module file

# 1) App-only auth
auth = GbAuth(
    tenant_id="00000000-0000-0000-0000-000000000000",
    client_id="11111111-1111-1111-1111-111111111111",
    client_secret="YOUR_CLIENT_SECRET"
)

# 2) SharePoint site (Graph uses hostname + site path)
site = GbSite(
    hostname="contoso.sharepoint.com",
    site_path="/sites/Marketing",   # include the leading slash
    gb_auth=auth
)

print("Site ID:", site.site_id)

# 3) SharePoint list
sp_list = GbList(
    list_name="Campaigns 2025",   # display name of the list
    gb_site=site
)

# 4) Read
print("Fields:", sp_list.list_fields)  # e.g. ['Title', 'Status', 'Owner', ...]
rows = sp_list.list_rows               # list of dicts (the item's 'fields' object)
for r in rows:
    print(r["Title"], r.get("Status"))
```

---

## Usage examples

### Read items

```python
rows = sp_list.list_rows
print(len(rows), "rows")
print(rows[0])  # {'Title': 'Campaign A', 'Status': 'Active', ...}
```

> `list_fields` returns column internal names inferred from the first row. If the list is empty, it returns `[]`.

### Create items

```python
new_item = {
    "Title": "New Campaign",
    "Status": "Active",
    "Budget": 5000
}
result = sp_list.create(new_item)

# {'successes': [{'id': '123', 'success': True, 'item': {...}}], 'failures': []}
print(result["successes"])
```

`create()` accepts either a **single dict** or a **list of dicts**. Each dict is wrapped as `{"fields": row}` as required by Graph.

### Update items (PATCH)

```python
item_id = sp_list.list_ids[0]  # Graph item id (string)
patch = {"Status": "Closed"}

result = sp_list.update(ids=item_id, rows=patch)
# For batch updates: ids=[...], rows=[{...}, {...}]
print(result)
```

Performs a PATCH to `/lists/{list_id}/items/{item_id}/fields` with the passed `rows` dict.

### Delete items

```python
to_delete = sp_list.list_ids[:2]
result = sp_list.delete(to_delete)
print("Deleted:", [s["id"] for s in result["successes"]])
```

### Upsert / sync with `upload()`

```python
# Synchronize the list with the provided rows:
# - if an id exists: update it (or fully replace if force=True)
# - if an id does NOT exist: create a new item
# - if delete=True: remove existing items not present in 'ids'

ids  = ["10", "42"]  # Graph item ids (strings)
rows = [
    {"Title": "Row 10", "Status": "Active"},
    {"Title": "Row 42", "Status": "Closed"}
]

report = sp_list.upload(ids=ids, rows=rows, force=False, delete=False)
print(report)
```

**Important notes on `upload()`**

* **IDs must be Graph item ids** (those from `sp_list.list_ids`).
* For **new** items (id not found), the function creates an item and reports `new_id` in the result.
* `force=True` means *delete + create* (hard replace).
* `delete=True` removes items **not** included in `ids`.

### Filter items with `get_items_by_features()`

This method evaluates predicates against **`sp_list.list_items`** (the full Graph item object that includes the `fields` sub-object).
To filter on list columns, specify predicates **nested under `fields`**:

```python
features = [
    {"fields": {"Status": "Active"}},                 # AND within the same dict
    {"fields": {"Owner": "mario.rossi@contoso.com"}}
]
matched_items = sp_list.get_items_by_features(features)
# Returns a de-duplicated list of Graph items (with 'id', 'fields', etc.)
```

* The list of dicts in `features` is combined in **OR**.
* Key/value pairs inside a single dict are combined in **AND**.
* One level of nesting is supported (e.g., `{"fields": {"Category": {"Name": "Premium"}}}` if your `fields` contains nested objects).

---

## Field name encoding/decoding

SharePoint internal names may contain sequences like `_x0020_` for spaces.
`GbList` exposes:

* `encode_row(row: dict) -> dict`: replaces special characters in **key names** (`' '` → `_x0020_`, etc.)
* `decode_row(row: dict) -> dict`: reverse operation.

Example:

```python
human = {"Customer name": "ACME", "Close date": "2025-08-01"}
encoded = sp_list.encode_row(human)  # {'Customer_x0020_name': 'ACME', ...}
created = sp_list.create(encoded)
```

If you already use the correct **internal names**, you don’t need to encode.

---

## API reference (main properties & methods)

### `GbAuth`

* `token` → Graph bearer token (cached).
* `headers` → `{'Authorization': 'Bearer <token>'}`

> Changing `tenant_id`, `client_id`, or `client_secret` clears cached auth/token.

### `GbSite`

* `site_url` → `https://graph.microsoft.com/v1.0/sites/{hostname}:{site_path}`
* `site_data` → site JSON (cached)
* `site_id` → `site_data["id"]`

### `GbList`

* `list_url`   → `https://graph.microsoft.com/v1.0/sites/{site_id}/lists/{quote(list_name)}`
* `list_data`  → list metadata (cached)
* `list_id`    → `list_data["id"]`
* `list_items` → `GET {list_url}/items?expand=fields` (list of Graph items)
* `list_rows`  → `[item["fields"] for item in list_items]`
* `list_ids`   → `[item["id"] for item in list_items]`
* `list_fields`→ column names from the first row (or `[]`)

CRUD:

* `create(rows)`  → POST `/items` (accepts dict or list of dicts; wraps as `{"fields": ...}`).
* `update(ids, rows)` → PATCH `/items/{id}/fields`
* `delete(ids)`   → DELETE `/items/{id}`
* `upload(ids, rows, force=False, delete=False)` → upsert + optional cleanup.

Utilities:

* `get_items_by_features(features)` → OR across groups of predicates (AND within each group).
* `encode_row(row)`, `decode_row(row)`
* `deduplicate_dicts(list_of_dicts)` (free function)

---

## Best practices & limitations

* **Pagination**: `list_items` does not follow `@odata.nextLink`. For very large lists, implement paging if needed.
* **Field names**: prefer **internal names**. If you rely on display names/spaces/special chars, use `encode_row`.
* **Error handling**: the code raises `ValueError`, `TypeError`, `RuntimeError` with Graph response details when available.
* **Rate limiting**: Graph may return 429/503. Add retries/backoff for large batch operations.
* **Security**: never commit `client_secret`. Use environment variables.

Example with environment variables:

```python
import os
auth = GbAuth(
    tenant_id=os.environ["AZURE_TENANT_ID"],
    client_id=os.environ["AZURE_CLIENT_ID"],
    client_secret=os.environ["AZURE_CLIENT_SECRET"]
)
```

---

## End-to-end (quick CRUD)

```python
# CREATE
created = sp_list.create([
    {"Title": "Task A", "Status": "Active"},
    {"Title": "Task B", "Status": "Active"},
])
new_ids = [s["id"] for s in created["successes"]]

# READ
print(sp_list.list_rows)

# UPDATE
sp_list.update(ids=new_ids[0], rows={"Status": "Closed"})

# DELETE
sp_list.delete(new_ids[1])
```

---

## Project layout (minimal)

If you don’t publish a package, paste the classes into `gbsharepoint.py` and:

```python
# file: gbsharepoint.py
# (paste the provided classes/utilities here)

# then in your script:
from gbsharepoint import GbAuth, GbSite, GbList
```

---

## License

Add the license that applies to your repository (e.g., MIT).

---

If you want, I can tailor examples to your actual site/list—just share `hostname`, `site_path`, and the list name.
