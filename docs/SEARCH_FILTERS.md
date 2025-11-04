# Search Filters Reference

## Overview

Filters narrow search results based on specific criteria. They work with all search types (semantic, sparse, hybrid).

---

## Filter Operators

| Operator | API Value | Use With | Description |
|----------|-----------|----------|-------------|
| **Equal** | `eq` | Strings, numbers, booleans | Exact match |
| **Not Equal** | `neq` | Strings, numbers, booleans | Exclude match |
| **In** | `in` | Arrays of values | Match any value in list |
| **Not In** | `nin` | Arrays of values | Exclude all values in list |
| **Greater Than** | `gt` | Numbers | Value > threshold |
| **Greater or Equal** | `gte` | Numbers | Value >= threshold |
| **Less Than** | `lt` | Numbers | Value < threshold |
| **Less or Equal** | `lte` | Numbers | Value <= threshold |

---

## Filter Structure

```json
{
  "text": "your search query",
  "search_type": "hybrid",
  "top": 10,
  "filters": [
    {
      "field": "field_name",
      "operator": "eq",
      "value": "field_value"
    }
  ]
}
```

---

## Available Fields

Fields you can filter on from the Competency model:

| Field | Type | Example Values | Nullable |
|-------|------|----------------|----------|
| `code` | string | "ESCO-S123", "ROME-001" | No |
| `lang` | string | "en", "fr" | No |
| `type` | string | "skill", "occupation", "certification" | No |
| `provider` | string | "esco", "rome", "forma", and more | No |
| `title` | string | "Python Programming" | No |
| `url` | string | "https://example.com/" | Yes |
| `category` | string | "Information Technology" | Yes |
| `description` | string | Long text | Yes |
| `keywords` | array | ["programming", "coding"] | Yes |
| `metadata.*` | any | Custom nested fields | Yes |

---

## Examples

### Basic Example: Single Filter

Filter by language:

```bash
curl -X POST "http://search-engine.localhost/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "software development",
    "search_type": "hybrid",
    "top": 10,
    "filters": [
      {"field": "lang", "operator": "eq", "value": "en"}
    ]
  }'
```

---

### Advanced Example: Multiple Filters

Combine multiple criteria (AND logic):

```bash
curl -X POST "http://search-engine.localhost/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "data analysis",
    "search_type": "hybrid",
    "top": 10,
    "filters": [
      {"field": "lang", "operator": "eq", "value": "en"},
      {"field": "type", "operator": "in", "value": ["skill", "occupation"]},
      {"field": "provider", "operator": "eq", "value": "esco"}
    ]
  }'
```

---

### Real-World Use Case: Job Board

Find English technical skills from verified sources:

```bash
curl -X POST "http://search-engine.localhost/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "cloud computing AWS",
    "search_type": "hybrid",
    "top": 20,
    "filters": [
      {"field": "lang", "operator": "eq", "value": "en"},
      {"field": "type", "operator": "eq", "value": "skill"},
      {"field": "category", "operator": "eq", "value": "Information and Communication Technologies"},
      {"field": "provider", "operator": "in", "value": ["esco", "forma"]}
    ]
  }'
```

---

## Filtering on Nested Metadata

Use **dot notation** to filter on nested fields in the `metadata` object:

```bash
curl -X POST "http://search-engine.localhost/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "advanced programming",
    "search_type": "hybrid",
    "top": 10,
    "filters": [
      {"field": "metadata.difficulty_level", "operator": "gte", "value": 7},
      {"field": "metadata.verified", "operator": "eq", "value": true}
    ]
  }'
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| **No results** | Remove filters one by one to identify overly restrictive criteria |
| **Filter not applied** | Check for typos in field names (case-sensitive) |
| **Numeric comparison fails** | Ensure value type matches (number vs string) |
| **Null value confusion** | Use `eq null` for missing/null, `neq null` for exists |
