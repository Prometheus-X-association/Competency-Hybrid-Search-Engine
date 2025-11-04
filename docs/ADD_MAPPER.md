# Guide: How to Add a New Mapper

This guide explains how to create a new mapper to import data from new data sources into the hybrid competency search engine.

## Table of Contents

1. [Overview](#overview)
2. [Mapper Architecture](#mapper-architecture)
3. [Steps to Create a New Mapper](#steps-to-create-a-new-mapper)
4. [Using the API to Import Data](#using-the-api-to-import-data)

## Overview

Mappers are classes responsible for transforming raw data from different sources (ESCO, ROME, Forma, etc.) into standardized `Competency` objects. Each mapper inherits from the abstract `MapperContract` class and must implement the `to_competency()` method.

## Mapper Architecture

### Base Class: MapperContract

All mappers inherit from `MapperContract` which defines:

```python
from abc import ABC, abstractmethod
from pydantic import BaseModel
from data_importer.enums import CompetencyType, Language, Provider
from data_importer.schemas import Competency

class MapperContract(ABC, BaseModel):
    provider: Provider
    competency_type: CompetencyType
    lang: Language

    @abstractmethod
    def to_competency(self) -> Competency:
        """Convert the raw data to a Competency object."""
        pass
```

### Output Schema: Competency

All mappers must produce a `Competency` object with this structure:

```python
class Competency(BaseModel):
    code: str                          # Unique identifier from source
    lang: Language                     # Language (EN, FR)
    type: CompetencyType               # Type (OCCUPATION, SKILL, CERTIFICATION)
    provider: Provider                 # Source (ESCO, ROME, FORMA, etc.)
    title: str                         # Main title
    url: str | None                    # URL to source
    category: str | None               # Category/domain
    description: str | None            # Detailed description
    keywords: list[str] | None         # Keywords/synonyms
    indexed_text: str | None           # Text for vector indexing
```

## Steps to Create a New Mapper

### 1. Add your provider to the enums

Modify `src/data_importer/enums.py`:

```python
class Provider(StrEnum):
    ESCO = "esco"
    ROME = "rome"
    FORMA = "forma"
    YOUR_PROVIDER = "your_provider"  # Add your provider here
```

### 2. Create your Mapper class

Create a new file `src/data_importer/mappers/your_provider.py`:

```python
from typing import override
from mappers.contract import MapperContract
from pydantic import Field
from data_importer.schemas import Competency

class YourProviderMapper(MapperContract):
    """Mapper for Your Provider data."""
    
    # Define fields specific to your data source
    # Use Field() with validation_alias if field names differ
    identifier: str = Field(validation_alias="id")
    name: str = Field(validation_alias="name")
    full_description: str = Field(validation_alias="fullDescription")
    keywords: list[str] | None = Field(None, validation_alias="keywords")
    
    @override
    def to_competency(self) -> Competency:
        """Convert data to a Competency object."""
        
        # Data cleaning and transformation
        cleaned_title = self.name.strip().capitalize()
        
        # Process keywords
        cleaned_keywords = []
        if self.keywords:
            cleaned_keywords = [
                kw.strip().capitalize() 
                for kw in self.keywords 
                if kw.strip()
            ]
        
        return Competency(
            code=self.identifier,
            lang=self.lang,
            type=self.competency_type,
            provider=self.provider,
            title=cleaned_title,
            url=f"https://your-provider.com/item/{self.identifier}",
            category=None,  # Adapt according to your data
            description=self.full_description,
            keywords=cleaned_keywords,
            indexed_text=cleaned_title,  # Or a combination of fields
        )
```

### 3. Register your mapper, for your provider 

Modify `src/data_importer/dependencies.py`:
```python
from .mappers.your_provider import YourProviderMapper

MAPPER_REGISTRY: dict[Provider, type[MapperContract]] = {
    Provider.ESCO: EscoMapper,
    Provider.ROME: RomeMapper,
    Provider.FORMA: FormaMapper,
    Provider.YOUR_PROVIDER: YourProviderMapper,
}
```

## Using the API to Import Data

Once you have created your mapper, you can use the Data Importer API to import data from JSON files. The API provides two endpoints:

1. `/import` - Import a single item
2. `/import/file` - Import multiple items from a JSON file

### Single Item Import

Use the `/import` endpoint to import individual competency records:

```bash
curl -X POST "http://localhost:8006/import" \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "esco",
    "competency_type": "occupation",
    "lang": "fr",
    "indexing_strategy": "field_duplication",
    "data": {
      "preferredLabel": "développeur web",
      "description": "Développe des applications web",
      "conceptUri": "http://data.europa.eu/esco/occupation/12345",
      "code": "2512.1",
      "category": "Développeurs logiciels"
    }
  }'
```

### Bulk Import from JSON File

Use the `/import/file` endpoint to import multiple items from a JSON file:

#### Example with ESCO data

```bash
curl -X POST "http://localhost:8006/import/file" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/data/esco/fr/cleaned_occupations.json" \
  -F "provider=esco" \
  -F "competency_type=occupation" \
  -F "lang=fr"
```

#### Example with ROME data

```bash
curl -X POST "http://localhost:8006/import/file" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/data/rome/cleaned.json" \
  -F "provider=rome" \
  -F "competency_type=occupation" \
  -F "lang=fr"
```

#### Example with Forma data

```bash
curl -X POST "http://localhost:8006/import/file" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@examples/data/forma/cleaned.json" \
  -F "provider=forma" \
  -F "competency_type=skill" \
  -F "lang=fr"
```
