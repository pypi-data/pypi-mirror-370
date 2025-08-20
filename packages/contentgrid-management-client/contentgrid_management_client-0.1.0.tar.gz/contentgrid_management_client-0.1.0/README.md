# ContentGrid Management Client

This ContentGrid Management Client is a Python library designed to interact with the ContentGrid Management API endpoints, specifically in the HAL response type. It provides a convenient interface for performing various operations such as fetching organizations, projects, and blueprints, and managing automations and automation annotations.

## Features

- **Organization Handling**: Fetch organizations and their associated projects.
- **Project Handling**: Fetch projects and their associated blueprints.
- **Blueprint Handling**: Manage blueprints including entity definitions and automations.
- **Automation Management**: Create and manage automations and their annotations.
- **Error Handling**: Provides basic error handling for network requests.

## Installation

To install the ContentGrid Management Client, you can use pip:

```bash
pip install contentgrid-management-client
```

## Usage

### Initialization and Organization Handling

```python
from contentgrid_client import HALFormsClient

# Initialize a HALFormsClient with service account
client = HALFormsClient(
    client_endpoint="https://api.contentgrid.com/",
    auth_uri="https://auth.eu-west-1.contentgrid.cloud/realms/cg-eade54da-3903-4554-aa5e-2982cd4126f1/protocol/openid-connect/token",
    client_id="your_client_id",
    client_secret="your_client_secret"
)

# Initialize a HALFormsClient with a token
client = HALFormsClient(
    client_endpoint="https://api.contentgrid.com/",
    auth_uri="https://auth.eu-west-1.contentgrid.cloud/realms/cg-eade54da-3903-4554-aa5e-2982cd4126f1/protocol/openid-connect/token",
    token="your_token"
)

# Get all organizations
organization = get_organizations(hal_client=client)[0]
```

### Project Handling

```python
# Get the first project
project = organization.get_projects()[0]

# Get blueprints of the project
blueprints = project.get_blueprints()
```

### Blueprint Handling

```python
# Get a specific blueprint
blueprint = project.get_blueprint_by_name("blueprint_name")

# Create a new entity definition in the blueprint
entity_definition = blueprint.create_entity("entity_name", "entity_description")

# Get entity definitions
entity_definitions = blueprint.get_entity_definitions()
```

### Automation Management

```python
# Get automations in a blueprint
automations = blueprint.get_automations()

# Create a new automation in the blueprint
automation_data = {
    "foo" : "bar"
}
automation = blueprint.create_automation("automation_name", "system_name", automation_data)

# Create an annotation for an automation
annotation_data = {
    "key": "value"
}
annotation = automation.create_annotation_on_entity("entity_name", annotation_data)
```

## Testing

### Installing Requirements

```bash
pip install -r requirements.txt
```

### Running Tests

```bash
python -m pytest
```

### Running Tests with Coverage

```bash
coverage run -m pytest && coverage report -m
```
