# ApiLinker

[![PyPI version](https://badge.fury.io/py/apilinker.svg)](https://badge.fury.io/py/apilinker)
[![docs](https://readthedocs.org/projects/apilinker/badge/?version=latest)](https://apilinker.readthedocs.io/en/latest/)
[![build](https://github.com/kkartas/APILinker/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/kkartas/APILinker/actions/workflows/ci.yml)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/apilinker)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)


<div align="center">
  <h3>A universal bridge to connect, map, and automate data transfer between any two REST APIs</h3>
</div>

---

**ApiLinker** is an open-source Python package that simplifies the integration of REST APIs by providing a universal bridging solution. Built for developers, data engineers, and researchers who need to connect different systems without writing repetitive boilerplate code.

---

## 🌟 Features

- 🔄 **Universal Connectivity** - Connect any two REST APIs with simple configuration
- 🗺️ **Powerful Mapping** - Transform data between APIs with field mapping and path expressions
- 📊 **Data Transformation** - Apply built-in or custom transformations to your data
 - 🔒 **Authentication & Security** - Support for API Key, Bearer Token, Basic Auth, and multiple OAuth2 flows (including PKCE and Device Flow). Optional secure credential storage and role-based access control.
- 📝 **Flexible Configuration** - Use YAML/JSON or configure programmatically in Python
- 🕒 **Automated Scheduling** - Run syncs once, on intervals, or using cron expressions
- 📋 **Schema Validation** - JSON Schema validation for responses and requests, with optional strict mode and readable diffs
- 🔌 **Plugin Architecture** - Extend with custom connectors, transformers, and authentication methods
- 📈 **Pagination Handling** - Automatic handling of paginated API responses
- 🔍 **Robust Error Handling** - Circuit breakers, Dead Letter Queues (DLQ), and configurable recovery strategies
- 🧬 **Scientific Connectors** - Built-in connectors for research APIs (NCBI/PubMed, arXiv) with domain-specific functionality
- 📦 **Minimal Dependencies** - Lightweight core with minimal external requirements

## Security

APILinker provides security features to protect your API credentials and data:

### Role-Based Access Control

```python
# Enable multi-user access with different permission levels
linker = ApiLinker(
    security_config={
        "enable_access_control": True,
        "users": [
            {"username": "admin1", "role": "admin"},
            {"username": "viewer1", "role": "viewer"}
        ]
    }
)
```

For more details, see the [Security Documentation](docs/security.md). Note: ApiLinker defaults to no request/response encryption and recommends HTTPS and provider-recommended authentication. Optional request/response encryption utilities are available for advanced scenarios; review the security docs before enabling.

## 📋 Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Authentication Methods](#authentication-methods)
- [Field Mapping](#field-mapping)
- [Error Handling](#error-handling)
- [Data Transformations](#data-transformations)
- [Scheduling](#scheduling)
- [Command Line Interface](#command-line-interface)
- [Schema Validation and Strict Mode](#schema-validation-and-strict-mode)
- [Python API](#python-api)
- [Examples](#examples)
- [Extending ApiLinker](#extending-apilinker)
- [Contributing](#contributing)
- [Documentation](#documentation)
- [License](#license)

## 🚀 Installation

### Standard Installation

Install ApiLinker using pip (Python's package manager):

```bash
pip install apilinker
```

If you're using Windows, you might need to use:

```bash
py -m pip install apilinker
```

Make sure you have Python 3.8 or newer installed. To check your Python version:

```bash
python --version
# or
py --version
```

### Development Installation

To install from source (for contributing or customizing):

```bash
# Clone the repository
git clone https://github.com/kkartas/apilinker.git
cd apilinker

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Install with documentation tools
pip install -e ".[docs]"
```

### Verifying Installation

To verify ApiLinker is correctly installed, run:

```bash
python -c "import apilinker; print(apilinker.__version__)"
```

You should see the version number printed if installation was successful.

## 🎯 Beginner's Guide

New to API integration? Follow this step-by-step guide to get started with ApiLinker.

### Step 1: Install ApiLinker

```bash
pip install apilinker
```

### Step 2: Create Your First API Connection

Let's connect to a public API (Weather API) and print some data:

```python
from apilinker import ApiLinker

# Create an API connection
linker = ApiLinker()

# Configure a simple source
linker.add_source(
    type="rest",
    base_url="https://api.openweathermap.org/data/2.5",
    endpoints={
        "get_weather": {
            "path": "/weather",
            "method": "GET",
            "params": {
                "q": "London",
                "appid": "YOUR_API_KEY"  # Get a free key at openweathermap.org
            }
        }
    }
)

# Fetch data from the API
weather_data = linker.fetch("get_weather")

# Print results
print(f"Temperature: {weather_data['main']['temp']} K")
print(f"Conditions: {weather_data['weather'][0]['description']}")
```

### Step 3: Save the Script and Run It

Save the above code as `weather.py` and run it:

```bash
python weather.py
```

### Step 4: Try a Data Transformation

Let's convert the temperature from Kelvin to Celsius:

```python
# Add this to your script
def kelvin_to_celsius(kelvin_value):
    return kelvin_value - 273.15

linker.mapper.register_transformer("kelvin_to_celsius", kelvin_to_celsius)

# Get the temperature in Celsius
temp_kelvin = weather_data['main']['temp']
temp_celsius = linker.mapper.transform(temp_kelvin, "kelvin_to_celsius")

print(f"Temperature: {temp_celsius:.1f}°C")
```

### Common Beginner Issues

- **ImportError**: Make sure ApiLinker is installed (`pip install apilinker`)
- **API Key errors**: Register for a free API key at the service you're using
- **Connection errors**: Check your internet connection and API endpoint URL
- **TypeError**: Make sure you're passing the correct data types to functions

## 🏁 Quick Start

### Using the CLI

Create a configuration file `config.yaml`:

```yaml
source:
  type: rest
  base_url: https://api.example.com/v1
  auth:
    type: bearer
    token: ${SOURCE_API_TOKEN}  # Reference environment variable
  endpoints:
    list_items:
      path: /items
      method: GET
      params:
        updated_since: "{{last_sync}}"  # Template variable
      pagination:
        data_path: data
        next_page_path: meta.next_page
        page_param: page
target:
  type: rest
  base_url: https://api.destination.com/v2
  auth:
    type: api_key
    header: X-API-Key
    key: ${TARGET_API_KEY}
  endpoints:
    create_item:
      path: /items
      method: POST

mapping:
  - source: list_items
    target: create_item
    fields:
      - source: id
        target: external_id
      - source: name
        target: title
      - source: description
        target: body.content
      - source: created_at
        target: metadata.created
        transform: iso_to_timestamp
      # Conditional field mapping
      - source: tags
        target: labels
        condition:
          field: tags
          operator: exists
        transform: lowercase

schedule:
  type: interval
  minutes: 60

logging:
  level: INFO
  file: apilinker.log
```

Run a sync with:

```bash
apilinker sync --config config.yaml
```

Run a dry run to see what would happen without making changes:

```bash
apilinker sync --config config.yaml --dry-run
```

Run a scheduled sync based on the configuration:

```bash
apilinker run --config config.yaml
```

Probe schemas and suggest a starter mapping from example payloads:

```bash
apilinker probe_schema --source source_sample.json --target target_sample.json
```

### Using as a Python Library

```python
from apilinker import ApiLinker

# Initialize with config file
linker = ApiLinker(config_path="config.yaml")

# Or configure programmatically
linker = ApiLinker()

# Step 1: Set up your source API connection
linker.add_source(
    type="rest",                          # API type (REST is most common)
    base_url="https://api.github.com",   # Base URL of the API
    auth={                              # Authentication details
        "type": "bearer",              # Using bearer token authentication
        "token": "${GITHUB_TOKEN}"     # Reference to an environment variable
    },
    endpoints={                          # Define API endpoints
        "list_issues": {               # A name you choose for this endpoint
            "path": "/repos/owner/repo/issues",  # API path
            "method": "GET",           # HTTP method
            "params": {"state": "all"}  # Query parameters
        }
    }
)

# Step 2: Set up your target API connection
linker.add_target(
    type="rest",
    base_url="https://gitlab.com/api/v4",
    auth={
        "type": "bearer",
        "token": "${GITLAB_TOKEN}"
    },
    endpoints={
        "create_issue": {
            "path": "/projects/123/issues",
            "method": "POST"           # This endpoint will receive data
        }
    }
)

# Step 3: Define how data maps from source to target
linker.add_mapping(
    source="list_issues",               # Source endpoint name (from Step 1)
    target="create_issue",              # Target endpoint name (from Step 2)
    fields=[                            # Field mapping instructions
        {"source": "title", "target": "title"},           # Map source title → target title
        {"source": "body", "target": "description"}      # Map source body → target description
    ]
)

# Step 4: Execute the sync (one-time)
result = linker.sync()
print(f"Synced {result.count} records")

# Step 5 (Optional): Set up scheduled syncing
linker.add_schedule(interval_minutes=60)  # Run every hour
linker.start_scheduled_sync()
```

#### Step-by-Step Explanation:

1. **Import the library**: `from apilinker import ApiLinker`
2. **Create an instance**: `linker = ApiLinker()`
3. **Configure source API**: Define where to get data from
4. **Configure target API**: Define where to send data to
5. **Create mappings**: Define how fields translate between APIs
6. **Run the sync**: Either once or on a schedule

## 🔧 Configuration

ApiLinker uses a YAML configuration format with these main sections:

### Source and Target API Configuration

Both `source` and `target` sections follow the same format:

```yaml
source:  # or target:
  type: rest  # API type
  base_url: https://api.example.com/v1  # Base URL
  auth:  # Authentication details
    # ...
  endpoints:  # API endpoints
    # ...
  timeout: 30  # Request timeout in seconds (optional)
  retry_count: 3  # Number of retries (optional)
```

### Authentication Methods

ApiLinker supports multiple authentication methods:

```yaml
# API Key Authentication
auth:
  type: api_key
  key: your_api_key  # Or ${API_KEY_ENV_VAR}
  header: X-API-Key  # Header name

# Bearer Token Authentication
auth:
  type: bearer
  token: your_token  # Or ${TOKEN_ENV_VAR}

# Basic Authentication
auth:
  type: basic
  username: your_username  # Or ${USERNAME_ENV_VAR}
  password: your_password  # Or ${PASSWORD_ENV_VAR}

# OAuth2 Client Credentials
auth:
  type: oauth2_client_credentials
  client_id: your_client_id  # Or ${CLIENT_ID_ENV_VAR}
  client_secret: your_client_secret  # Or ${CLIENT_SECRET_ENV_VAR}
  token_url: https://auth.example.com/token
  scope: read write  # Optional
```

### Field Mapping

Mappings define how data is transformed between source and target:

```yaml
mapping:
  - source: source_endpoint_name
    target: target_endpoint_name
    fields:
      # Simple field mapping
      - source: id
        target: external_id
      
      # Nested field mapping
      - source: user.profile.name
        target: user_name
      
      # With transformation
      - source: created_at
        target: timestamp
        transform: iso_to_timestamp
      
      # Multiple transformations
      - source: description
        target: summary
        transform:
          - strip
          - lowercase
      
      # Conditional mapping
      - source: status
        target: active_status
        condition:
          field: status
          operator: eq  # eq, ne, exists, not_exists, gt, lt
          value: active
```

### Schema Validation and Strict Mode

Validate source responses and target requests against JSON Schemas, and optionally enable strict mode to fail early when mismatches occur.

```yaml
source:
  endpoints:
    list_items:
      path: /items
      method: GET
      response_schema:
        type: object
        properties:
          data:
            type: array
            items:
              type: object
              properties:
                id: { type: string }
                name: { type: string }

target:
  endpoints:
    create_item:
      path: /items
      method: POST
      request_schema:
        type: object
        properties:
          external_id: { type: string }
          title: { type: string }
        required: [external_id, title]

validation:
  strict_mode: true  # Fail sync if target payloads do not satisfy the request schema
```

CLI to infer minimal schemas and a starter mapping from samples:

```bash
apilinker probe_schema --source src_sample.json --target tgt_sample.json
```

## 🔄 Data Transformations

ApiLinker provides built-in transformers for common operations:

| Transformer | Description |
|-------------|-------------|
| `iso_to_timestamp` | Convert ISO date to Unix timestamp |
| `timestamp_to_iso` | Convert Unix timestamp to ISO date |
| `lowercase` | Convert string to lowercase |
| `uppercase` | Convert string to uppercase |
| `strip` | Remove whitespace from start/end |
| `to_string` | Convert value to string |
| `to_int` | Convert value to integer |
| `to_float` | Convert value to float |
| `to_bool` | Convert value to boolean |
| `default_empty_string` | Return empty string if null |
| `default_zero` | Return 0 if null |
| `none_if_empty` | Return null if empty string |

You can also create custom transformers:

```python
def phone_formatter(value):
    """Format phone numbers to E.164 format."""
    if not value:
        return None
    digits = re.sub(r'\D', '', value)
    if len(digits) == 10:
        return f"+1{digits}"
    return f"+{digits}"

# Register with ApiLinker
linker.mapper.register_transformer("phone_formatter", phone_formatter)
```

## 🧬 Comprehensive Research Connector Ecosystem

ApiLinker includes **8 specialized research connectors** covering scientific literature, chemical data, researcher profiles, code repositories, and more:

### 🔬 Scientific Literature & Data
- **NCBI (PubMed, GenBank)** - Biomedical literature and genetic sequences
- **arXiv** - Academic preprints across all sciences  
- **CrossRef** - Citation data and DOI resolution
- **Semantic Scholar** - AI-powered academic search with citation analysis

### 🧪 Chemical & Biological Data
- **PubChem** - Chemical compounds, bioassays, and drug discovery data
- **ORCID** - Researcher profiles and academic credentials

### 💻 Code & Implementation Research
- **GitHub** - Code repositories, contribution analysis, and software research
- **NASA** - Earth science, climate data, and space research

### Quick Start with Multiple Connectors

```python
from apilinker import (
    NCBIConnector, ArXivConnector, CrossRefConnector, 
    SemanticScholarConnector, PubChemConnector, ORCIDConnector,
    GitHubConnector, NASAConnector
)

# Initialize research connectors
ncbi = NCBIConnector(email="researcher@university.edu")
arxiv = ArXivConnector()
semantic = SemanticScholarConnector(api_key="optional")
pubchem = PubChemConnector()
github = GitHubConnector(token="optional")

# Cross-platform drug discovery research
topic = "BRCA1 inhibitors"

# Literature search
pubmed_papers = ncbi.search_pubmed(topic, max_results=50)
ai_papers = semantic.search_papers(f"machine learning {topic}", max_results=30)

# Chemical compound analysis  
compounds = pubchem.search_compounds("BRCA1 inhibitor")

# Implementation code
github_repos = github.search_repositories(f"{topic} drug discovery", language="Python")

print(f"PubMed papers: {len(pubmed_papers.get('esearchresult', {}).get('idlist', []))}")
print(f"AI/ML papers: {len(ai_papers.get('data', []))}")
print(f"GitHub repositories: {len(github_repos.get('items', []))}")
```

### Interdisciplinary Research Workflows

```python
from apilinker import ApiLinker

# Climate science + AI research
linker = ApiLinker()

# Combine NASA climate data with arXiv ML papers
nasa = NASAConnector(api_key="nasa_key")
arxiv = ArXivConnector()

# Get earth observation data
climate_data = nasa.get_earth_imagery(lat=40.7128, lon=-74.0060)

# Find AI methods for climate analysis
ml_climate_papers = arxiv.search_papers("machine learning climate", max_results=100)

# Researcher collaboration analysis
orcid = ORCIDConnector()
climate_researchers = orcid.search_by_research_area(["climate science", "machine learning"])

print(f"Climate data sources: {len(climate_data)}")
print(f"ML climate papers: {len(ml_climate_papers)}")
print(f"Researchers found: {len(climate_researchers.get('result', []))}")
```

## 📊 Examples

### GitHub to GitLab Issue Migration

```python
from apilinker import ApiLinker

# Configure ApiLinker
linker = ApiLinker(
    source_config={
        "type": "rest",
        "base_url": "https://api.github.com",
        "auth": {"type": "bearer", "token": github_token},
        "endpoints": {
            "list_issues": {
                "path": f"/repos/{owner}/{repo}/issues",
                "method": "GET",
                "params": {"state": "all"},
                "headers": {"Accept": "application/vnd.github.v3+json"}
            }
        }
    },
    target_config={
        "type": "rest",
        "base_url": "https://gitlab.com/api/v4",
        "auth": {"type": "bearer", "token": gitlab_token},
        "endpoints": {
            "create_issue": {
                "path": f"/projects/{project_id}/issues",
                "method": "POST"
            }
        }
    }
)

# Custom transformer for labels
linker.mapper.register_transformer(
    "github_labels_to_gitlab",
    lambda labels: [label["name"] for label in labels] if labels else []
)

# Add mapping
linker.add_mapping(
    source="list_issues",
    target="create_issue",
    fields=[
        {"source": "title", "target": "title"},
        {"source": "body", "target": "description"},
        {"source": "labels", "target": "labels", "transform": "github_labels_to_gitlab"},
        {"source": "state", "target": "state"}
    ]
)

# Run the migration
result = linker.sync()
print(f"Migrated {result.count} issues from GitHub to GitLab")
```

### More Examples

See the `examples` directory for more use cases:

- Salesforce to HubSpot contact sync
- CSV file to REST API import
- Weather API data collection
- Custom plugin development

## 💻 Common Use Cases with Examples

### 1. Sync Data Between Two APIs

This example shows how to sync customer data from CRM to a marketing platform:

```python
from apilinker import ApiLinker
import os

# Set environment variables securely before running
# os.environ["CRM_API_KEY"] = "your_crm_api_key"
# os.environ["MARKETING_API_KEY"] = "your_marketing_api_key"

# Initialize ApiLinker
linker = ApiLinker()

# Configure CRM source
linker.add_source(
    type="rest",
    base_url="https://api.crm-platform.com/v2",
    auth={
        "type": "api_key",
        "header": "X-API-Key",
        "key": "${CRM_API_KEY}"  # Uses environment variable
    },
    endpoints={
        "get_customers": {
            "path": "/customers",
            "method": "GET",
            "params": {"last_modified_after": "2023-01-01"}
        }
    }
)

# Configure marketing platform target
linker.add_target(
    type="rest",
    base_url="https://api.marketing-platform.com/v1",
    auth={
        "type": "api_key",
        "header": "Authorization", 
        "key": "${MARKETING_API_KEY}"  # Uses environment variable
    },
    endpoints={
        "create_contact": {
            "path": "/contacts",
            "method": "POST"
        }
    }
)

# Define field mapping with transformations
linker.add_mapping(
    source="get_customers",
    target="create_contact",
    fields=[
        {"source": "id", "target": "external_id"},
        {"source": "first_name", "target": "firstName"},
        {"source": "last_name", "target": "lastName"},
        {"source": "email", "target": "emailAddress"},
        {"source": "phone", "target": "phoneNumber", "transform": "format_phone"},
        # Custom field creation with default value
        {"target": "source", "value": "CRM Import"}
    ]
)

# Register a custom transformer for phone formatting
def format_phone(phone):
    if not phone:
        return ""
    # Remove non-digits
    digits = ''.join(c for c in phone if c.isdigit())
    # Format as (XXX) XXX-XXXX for US numbers
    if len(digits) == 10:
        return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
    return phone

linker.mapper.register_transformer("format_phone", format_phone)

# Execute the sync
result = linker.sync()
print(f"Synced {result.count} customers to marketing platform")
```

### 2. Scheduled Data Collection

This example collects weather data hourly and saves to a CSV file:

```python
from apilinker import ApiLinker
import csv
import datetime
import time
import os

# Create a function to handle the collected data
def save_weather_data(data, city):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create CSV if it doesn't exist
    file_exists = os.path.isfile(f"{city}_weather.csv")
    with open(f"{city}_weather.csv", mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write header if file is new
        if not file_exists:
            writer.writerow(["timestamp", "temperature", "humidity", "conditions"])
        
        # Write data
        writer.writerow([
            timestamp,
            data['main']['temp'] - 273.15,  # Convert K to C
            data['main']['humidity'],
            data['weather'][0]['description']
        ])
    print(f"Weather data saved for {city} at {timestamp}")

# Initialize ApiLinker
linker = ApiLinker()

# Configure weather API
linker.add_source(
    type="rest",
    base_url="https://api.openweathermap.org/data/2.5",
    endpoints={
        "get_london_weather": {
            "path": "/weather",
            "method": "GET",
            "params": {
                "q": "London,uk",
                "appid": "YOUR_API_KEY"  # Replace with your API key
            }
        },
        "get_nyc_weather": {
            "path": "/weather",
            "method": "GET",
            "params": {
                "q": "New York,us",
                "appid": "YOUR_API_KEY"  # Replace with your API key
            }
        }
    }
)

# Create a custom handler for the weather data
def collect_weather():
    london_data = linker.fetch("get_london_weather")
    nyc_data = linker.fetch("get_nyc_weather")
    
    save_weather_data(london_data, "London")
    save_weather_data(nyc_data, "NYC")

# Run once to test
collect_weather()

# Then schedule to run hourly
linker.add_schedule(interval_minutes=60, callback=collect_weather)
linker.start_scheduled_sync()

# Keep the script running
try:
    print("Weather data collection started. Press Ctrl+C to stop.")
    while True:
        time.sleep(60)
except KeyboardInterrupt:
    print("Weather data collection stopped.")
```

## 🔌 Extending ApiLinker

### Creating Custom Plugins

ApiLinker can be extended through plugins. Here's how to create a custom transformer plugin:

```python
from apilinker.core.plugins import TransformerPlugin

class SentimentAnalysisTransformer(TransformerPlugin):
    """A transformer plugin that analyzes text sentiment."""
    
    plugin_name = "sentiment_analysis"  # This name is used to reference the plugin
    version = "1.0.0"                   # Optional version information
    author = "Your Name"                # Optional author information
    
    def transform(self, value, **kwargs):
        # Simple sentiment analysis (example)
        if not value or not isinstance(value, str):
            return {"sentiment": "neutral", "score": 0.0}
        
        # Add your sentiment analysis logic here
        positive_words = ["good", "great", "excellent"]
        negative_words = ["bad", "poor", "terrible"]
        
        # Count positive and negative words
        text = value.lower()
        positive_count = sum(1 for word in positive_words if word in text)
        negative_count = sum(1 for word in negative_words if word in text)
        
        # Calculate sentiment score
        total = positive_count + negative_count
        score = 0.0 if total == 0 else (positive_count - negative_count) / total
        
        return {
            "sentiment": "positive" if score > 0 else "negative" if score < 0 else "neutral",
            "score": score
        }
```

### Using Your Custom Plugin

After creating your plugin, you need to register it before using:

```python
from apilinker import ApiLinker

# Create your custom plugin instance
from my_plugins import SentimentAnalysisTransformer

# Initialize ApiLinker
linker = ApiLinker()

# Register the plugin
linker.plugin_manager.register_plugin(SentimentAnalysisTransformer)

# Configure APIs and mappings...
linker.add_mapping(
    source="get_reviews",
    target="save_analysis",
    fields=[
        {"source": "user_id", "target": "user_id"},
        # Use your custom plugin to transform the review text
        {"source": "review_text", "target": "sentiment_data", "transform": "sentiment_analysis"}
    ]
)
```

## ❓ Troubleshooting Guide

### Installation Issues

1. **Package not found error**
   ```
   ERROR: Could not find a version that satisfies the requirement apilinker
   ```
   - Make sure you're using Python 3.8 or newer
   - Check your internet connection
   - Try upgrading pip: `pip install --upgrade pip`

2. **Import errors**
   ```python
   ImportError: No module named 'apilinker'
   ```
   - Verify installation: `pip list | grep apilinker`
   - Check if you're using the correct Python environment
   - Try reinstalling: `pip install --force-reinstall apilinker`

### Connection Issues

1. **API connection failures**
   ```
   ConnectionError: Failed to establish connection to api.example.com
   ```
   - Check your internet connection
   - Verify the API base URL is correct
   - Make sure the API service is online
   - Check if your IP is allowed by the API provider

2. **Authentication errors**
   ```
   AuthenticationError: Invalid credentials
   ```
   - Verify your API key or token is correct
   - Check if the token has expired
   - Ensure you're using the correct authentication method

### Mapping Issues

1. **Field not found errors**
   ```
   KeyError: 'Field not found in source data: user_profile'
   ```
   - Check the actual response data structure
   - Make sure you're referencing the correct field names
   - For nested fields, use dot notation (e.g., `user.profile.name`)

2. **Transformation errors**
   ```
   ValueError: Invalid data for transformer 'iso_to_timestamp'
   ```
   - Check if the data matches the expected format
   - Make sure the transformer is properly registered
   - Add validation to your custom transformers

### Common Code Examples

## 📚 Documentation

Documentation is available in the `/docs` directory and at Read the Docs: https://apilinker.readthedocs.io/

### Core Documentation

1. [Getting Started](docs/getting_started.md) - A beginner-friendly introduction
2. [Installation Guide](docs/installation.md) - Detailed installation instructions
3. [Configuration Guide](docs/configuration.md) - Configuration options and formats
4. [API Reference](docs/api_reference/index.md) - Detailed API reference

### Quick Resources

- [Quick Reference](docs/quick_reference.md) - Essential commands and patterns
- [FAQ](docs/faq.md) - Frequently asked questions
- [Troubleshooting Guide](docs/troubleshooting.md) - Solutions to common problems

### Guides and Examples

- [Cookbook](docs/cookbook.md) - Ready-to-use recipes for common tasks
- [Examples](docs/examples/index.md) - Example use cases and code
- [Extending with Plugins](docs/plugins/index.md) - Creating and using plugins
- [Security Considerations](docs/security.md) - Security best practices (no custom encryption or built-in rate limiting)

### Technical Documentation

- [Architecture](docs/architecture.md) - System architecture and data flow diagrams
- [Comparison](docs/comparison.md) - How ApiLinker compares to other integration tools

### Step-by-Step Tutorials

- [API-to-API Sync Tutorial](docs/tutorials/api_to_api_sync.md) - Learn to sync data between APIs
- [Custom Transformers Tutorial](docs/tutorials/custom_transformers.md) - Create data transformation functions
- [More tutorials](docs/tutorials/index.md) - Browse all available tutorials

### Comprehensive API Reference

For developers who want to extend ApiLinker or understand its internals, we provide comprehensive API reference documentation that can be generated using Sphinx:

```bash
# Install Sphinx and required packages
pip install sphinx sphinx-rtd-theme myst-parser

# Generate HTML documentation
cd docs/sphinx_setup
sphinx-build -b html . _build/html
```

The generated documentation will be available in `docs/sphinx_setup/_build/html/index.html`

### Community Support

- [GitHub Issues](https://github.com/kkartas/apilinker/issues) - Report bugs or request features
- [Stack Overflow](https://stackoverflow.com/questions/tagged/apilinker) - Ask questions using the `apilinker` tag

## 🔒 Security Considerations

When working with APIs that require authentication, follow these security best practices:

1. **Never hardcode credentials** in your code or configuration files. Always use environment variables or secure credential stores.

2. **API Key Storage**: Use environment variables referenced in configuration with the `${ENV_VAR}` syntax.
   ```yaml
   auth:
     type: api_key
     header: X-API-Key
     key: ${MY_API_KEY}
   ```

3. **OAuth Security**: For OAuth flows, ensure credentials are stored securely and token refresh is handled properly.

4. **Credential Validation**: ApiLinker performs validation checks on authentication configurations to prevent common security issues.

5. **HTTPS**: Use HTTPS endpoints whenever possible to protect data in transit.

6. **Audit Logging**: Enable detailed logging for security-relevant events with:
   ```yaml
   logging:
     level: INFO
     security_audit: true
   ```

## 🤝 Contributing

Contributions are welcome! Please see our [Contributing Guide](CONTRIBUTING.md) for details.

- Use GitHub “New issue” to open a bug report or feature request (templates provided)
- Fork the repo and create a focused branch for changes
- Add tests and docs where applicable, then open a Pull Request

## 📄 Citation

If you use ApiLinker in your research, please cite:

```bibtex
@software{apilinker2025,
  author = {Kartas, Kyriakos},
  title = {ApiLinker: A Universal Bridge for REST API Integrations},
  url = {https://github.com/kkartas/apilinker},
  version = {0.4.0},
  year = {2025}
}
```

## 📃 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
