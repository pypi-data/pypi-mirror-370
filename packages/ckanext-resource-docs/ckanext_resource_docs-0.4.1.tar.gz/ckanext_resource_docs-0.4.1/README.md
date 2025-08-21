[![Tests](https://github.com/DataShades/ckanext-resource-docs/actions/workflows/test.yml/badge.svg)](https://github.com/DataShades/ckanext-resource-docs/actions/workflows/test.yml)

A CKAN extension that allows attaching a flexible data dictionary (resource documentation) to any resource — not just those backed by the Datastore.

Each resource’s documentation can include a validation schema defined individually using JSON Schema Draft 2020-12, enabling optional enforcement of structure and constraints while maintaining the flexibility of a free-form data dictionary.

The official specification for JSON Schema Draft 2020-12 is available [here](https://json-schema.org/draft/2020-12/).

Here is an example of a resource documentation in a format of Datastore fields. But it's not limited to that format, you can save any custom data you need.

![Documentation table](./docs/rdoc-1.png)

It's also possible to define a validation schema for the resource documentation, which will be used to validate the documentation data.

![Validation schema](./docs/rdoc-2.png)

- [Requirements](#requirements)
- [Installation](#installation)
- [Config settings](#config-settings)
  - [ckanext.resource\_docs.append\_docs\_to\_resource\_api](#ckanextresource_docsappend_docs_to_resource_api)
    - [Example API response](#example-api-response)
  - [ckanext.resource\_docs.api\_field\_name](#ckanextresource_docsapi_field_name)
  - [ckanext.resource\_docs.show\_view](#ckanextresource_docsshow_view)
- [Interface](#interface)
  - [Example implementation](#example-implementation)
- [Developer installation](#developer-installation)
- [Tests](#tests)
- [License](#license)

## Requirements

Compatibility with core CKAN versions:

| CKAN version    | Compatible?   |
| --------------- | ------------- |
| 2.9 and earlier | no            |
| 2.10+           | yes           |

## Installation
To install ckanext-resource-docs:

1. Activate your CKAN virtual environment, for example:

    ```bash
    . /usr/lib/ckan/default/bin/activate
    ```

2. Install the extension from PyPI:

    ```bash
    pip install ckanext-resource-docs
    ```

3. Add `resource_docs` to the `ckan.plugins` setting in your CKAN config file (usually located at `/etc/ckan/default/ckan.ini`).

4. Restart CKAN. For example, if you've deployed CKAN with Apache on Ubuntu:

    ```bash
    sudo service apache2 reload
    ```


## Config settings

The following options control how ckanext-resource-docs behaves.

### ckanext.resource_docs.append_docs_to_resource_api

Type: `bool`

Default: `false`

When `true`, resource documentation is automatically included in the standard CKAN resource API response. This allows clients to retrieve documentation without making a separate API call.

> [!IMPORTANT]
> Appending resource documentation to the API response can impact performance and response size.

Example:
```ini
ckanext.resource_docs.append_docs_to_resource_api = true
```

#### Example API response

With `append_docs_to_resource_api = true` and the default `api_field_name`:

```json
{
  "id": "resource-id-123",
  "name": "my-resource.csv",
  "url": "https://example.com/data.csv",
  "format": "CSV",
  "resource_docs": {
    "documentation": "This dataset contains...",
    "fields": [
      {
        "name": "column1",
        "description": "Description of column1",
        "type": "string"
      }
    ]
  }
}
```

---

### ckanext.resource_docs.api_field_name

Type: `string`

Default: `resource_docs`

Specifies the field name in the API response that will contain the resource documentation. Only applies if `append_docs_to_resource_api` is enabled.

> [!WARNING]
> Ensure, that your schema doesn't use the same field name to avoid conflicts.

Example:
```ini
ckanext.resource_docs.api_field_name = documentation
```

With this setting, the documentation appears under "documentation" field instead of "resource_docs".

---

### ckanext.resource_docs.show_view

Type: `bool`

Default: `false`

When `true`, the resource documentation is displayed in the resource view page in the CKAN web interface.

Example:

```ini
ckanext.resource_docs.show_view = true
```

View example:

![Resource doc view example](./docs/rdoc-3.png)

## Interface

The `IResourceDocs` interface allows CKAN plugins to extend the behavior of resource documentation extension.

Current methods:
 - `prepopulate_resource_docs` - Provide initial documentation using resource metadata.

### Example implementation

```python
import json

import ckan.plugins as p
import ckan.logic as tk

from ckanext.resource_docs.interfaces import IResourceDocs

class YourPlugin(p.SingletonPlugin):
    """Example plugin implementing IResourceDocs."""

    ...
    p.implements(IResourceDocs, inherit=True)

    def prepopulate_resource_docs(self, resource: dict[str, Any]) -> str:
        """Provide initial documentation using the DataStore Data Dictionary."""
        try:
            result = tk.get_action("datastore_info")(
                {"user": tk.current_user.name if tk.current_user else ""},
                {"id": resource["id"]}
            )
        except (tk.ValidationError, tk.ObjectNotFound):
            return ""

        return json.dumps(result["fields"])
```


## Developer installation

To install ckanext-resource-docs for development, activate your CKAN virtualenv and
do:
```sh
git clone https://github.com/DataShades/ckanext-resource-docs.git
cd ckanext-resource-docs
pip install -e .
```

## Tests

To run the tests, do:

```sh
pytest --ckan-ini=test.ini
```

## License

[AGPL](https://www.gnu.org/licenses/agpl-3.0.en.html)
