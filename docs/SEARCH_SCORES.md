# Search Scores and Similarity Ranking

## Overview

The search engine supports three search types, each with different scoring mechanisms. All results are **sorted by descending score** (highest = most relevant).

---

## Score Types

### 1. Cosine Similarity (Semantic Search)

**Used by**: `search_type: "semantic"`

**Score Range**: `-1.0` to `1.0`

**Interpretation**:
- `0.85 - 1.0`: Excellent semantic match
- `0.70 - 0.85`: Good relevance
- `0.50 - 0.70`: Fair relevance
- `< 0.50`: Low relevance

**Best for**: Natural language queries, understanding intent, finding synonyms and related concepts.

---

### 2. BM25 Scores (Sparse Search)

**Used by**: `search_type: "sparse"`

**Score Range**: Variable (not normalized, typically `0` to `20+`)

**Interpretation**:
- `10+`: Strong keyword match
- `5 - 10`: Good match
- `2 - 5`: Moderate match
- `< 2`: Weak match

**Note**: Scores vary based on query length and term rarity. Focus on **relative ranking** within results, not absolute values.

**Best for**: Exact keyword matching, technical terms, codes, and acronyms.

---

### 3. RRF Scores (Hybrid Search)

**Used by**: `search_type: "hybrid"`

**Score Range**: `0.0` to `1.0` (normalized after Reciprocal Rank Fusion)

**Interpretation**:
- `0.70 - 1.0`: Excellent match (high rank in both semantic and sparse results)
- `0.50 - 0.70`: Very good match
- `0.30 - 0.50`: Good match
- `< 0.30`: Lower relevance

**How it works**: Combines semantic and sparse search results using Reciprocal Rank Fusion (RRF), which ranks results based on their position in both result lists. Results ranking high in both searches score highest.

**Best for**: General-purpose searches (recommended default), balancing semantic understanding with keyword precision.

---

## When to Use Each Search Type

| Search Type | Use When | Avoid When |
|-------------|----------|------------|
| **Semantic** | Natural language queries, finding related concepts | Exact code/ID lookups, specific keyword requirements |
| **Sparse** | Exact keyword/phrase matching, technical terms | Understanding query intent with different wording |
| **Hybrid** | General searches, uncertain query types (recommended) | Specialized use cases requiring pure semantic or keyword matching |

---

## Quick Example

```bash
# Hybrid search with filters
curl -X POST "http://search-engine.localhost/search/text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "web development skills",
    "search_type": "hybrid",
    "top": 10,
    "filters": [
      {"field": "lang", "operator": "eq", "value": "en"}
    ]
  }'
```

---

## Best Practices

1. **Use hybrid search as default** for best results
2. **Compare scores within a result set**, not across different searches
3. **Combine with filters** (see [SEARCH_FILTERS.md](./SEARCH_FILTERS.md)) to narrow search space
