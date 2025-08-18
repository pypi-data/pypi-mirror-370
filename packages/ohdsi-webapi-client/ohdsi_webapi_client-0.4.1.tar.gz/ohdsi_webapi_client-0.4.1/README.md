# OHDSI WebAPI Client (Python)

[![PyPI version](https://img.shields.io/pypi/v/ohdsi-webapi-client)](https://pypi.org/project/ohdsi-webapi-client/)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Alpha-stage Python client for interacting with an OHDSI WebAPI instance.

## MVP Scope
- Info & health check
- Sources listing
- Vocabulary: concept lookup, search (basic), hierarchy (descendants)
- Concept Set: CRUD, expression export, resolve (included concepts)
- Cohort Definitions: CRUD, generate, job polling, inclusion stats, counts

## Install (development)
```bash
poetry install
```

(Ensure local venv is in-project: `.venv/` created via `poetry.toml`.)

## Environment Configuration
Copy the sample environment file and customize:
```bash
cp .env.sample .env
# Edit .env with your settings
```

The `.env` file is automatically loaded when you import the package. Key settings:
- `OHDSI_WEBAPI_BASE_URL`: Your WebAPI server URL
- `OHDSI_WEBAPI_AUTH_TOKEN`: Authentication token (optional)
- `OHDSI_CACHE_ENABLED`: Enable/disable caching (default: true)  
- `OHDSI_CACHE_TTL`: Cache TTL in seconds (default: 300)
- `OHDSI_CACHE_MAX_SIZE`: Maximum cache entries (default: 128)
- `INTEGRATION_WEBAPI`: Enable live integration tests (default: 0)

### Interactive Development
The `.env` file works seamlessly with Poetry and IPython:
```bash
# Environment variables are automatically loaded
poetry run ipython
poetry run python your_script.py
poetry run pytest
```

## Install (from PyPI - when published)
```bash
pip install ohdsi-webapi-client
```

## Quickstart
```python
from ohdsi_webapi import WebApiClient

# Uses OHDSI_WEBAPI_BASE_URL from .env if set, otherwise explicit URL
client = WebApiClient("https://atlas-demo.ohdsi.org/WebAPI")

# Check WebAPI health and version
info = client.info()
print(f"WebAPI version: {info.version}")

# List available data sources
sources = client.sources()
for src in sources:
    print(f"Source: {src.source_key} - {src.source_name}")

# Search for concepts
diabetes_concepts = client.vocabulary.search("type 2 diabetes", domain_id="Condition")
print(f"Found {len(diabetes_concepts)} diabetes concepts")

# Get a specific concept
metformin = client.vocabulary.concept(201826)  # Metformin
print(f"Concept: {metformin.concept_name}")

# Work with concept sets
concept_sets = client.conceptset()  # List all concept sets
print(f"Available concept sets: {len(concept_sets)}")

# Get vocabulary domains
domains = client.vocabulary.domains()
print(f"Available domains: {[d['domainId'] for d in domains[:5]]}")

client.close()
```

## API Design Philosophy

### Predictable REST-Style Methods
This client uses a **predictable naming convention** that mirrors WebAPI REST endpoints exactly, making it self-documenting for developers:

| REST Endpoint | Python Method | Description |
|--------------|---------------|-------------|
| `GET /info` | `client.info()` | WebAPI version and health |
| `GET /source/sources` | `client.sources()` | List data sources |
| `GET /vocabulary/domains` | `client.vocabulary.domains()` | List all domains |
| `GET /vocabulary/concept/{id}` | `client.vocabulary.concept(id)` | Get a concept |
| `GET /conceptset/` | `client.conceptset()` | List concept sets |
| `GET /conceptset/{id}` | `client.conceptset(id)` | Get concept set by ID |
| `GET /conceptset/{id}/expression` | `client.conceptset_expression(id)` | Get concept set expression |

**Why This Approach:**
- **Self-documenting**: `client.conceptset()` clearly maps to `GET /conceptset/`
- **Predictable**: If you know the REST endpoint, you know the Python method
- **Beginner-friendly**: Easy to learn for engineers new to OHDSI
- **No confusion**: One clear way to do each operation

See the [Supported Endpoints](docs/supported_endpoints.md) page for the complete mapping.


## Testing
### Unit tests (mocked, fast)
```bash
poetry run pytest
```
These use `respx` to mock HTTP endpoints.

### Live integration tests (public demo, read-only)
Disabled by default. To run:
```bash
export INTEGRATION_WEBAPI=1
export OHDSI_WEBAPI_BASE_URL=https://atlas-demo.ohdsi.org/WebAPI
poetry run pytest tests/live -q
```
Only GET/read-only endpoints are exercised (concept lookup & search). Write operations are intentionally excluded to avoid mutating the shared demo server.

### Local full integration (future)
Spin up a local WebAPI + database (Docker) to safely test create/update/delete for concept sets and cohorts. (Compose file TBD.)

## Concept & Concept Sets Summary
- `client.vocabulary.concept(id)` fetches a single concept by ID
- `client.vocabulary.search(query)` returns concepts matching text
- `client.vocabulary.concept_descendants(id)` navigates hierarchy
- `client.conceptset()` lists all concept sets
- `client.conceptset(id)` gets a specific concept set  
- `client.conceptset_expression(id)` gets the concept set expression
- `client.conceptset_items(id)` resolves expression to concrete included concepts

## Additional Documentation
See the docs directory for deeper guides:
- [OHDSI Sources](docs/sources.md) - working with data sources and CDM databases  
- [Vocabulary & Concepts](docs/vocabulary.md) - concept lookup, search, and hierarchies
- [Finding Codes](docs/finding_codes.md) - techniques for discovering OMOP concept codes
- [Concept Sets](docs/concept_sets.md) - creating and managing concept collections
- [Cohorts](docs/cohorts.md) - cohort definition management and generation
- [Cohort Building](docs/cohort_building.md) - advanced cohort construction patterns
- [Supported Endpoints](docs/supported_endpoints.md) - which WebAPI endpoints are supported
- [Caching](docs/caching.md) - performance optimization with intelligent caching

## Roadmap
- Auth strategies & configuration
- Asynchronous job polling patterns


## License
Apache 2.0
