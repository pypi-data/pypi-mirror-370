# 🔍 search_text

Search for a text query in all files within one or more directories or file paths and return matching lines or counts. Respects `.gitignore`.

## Signature

```python
search_text(
    paths: str,
    query: str,
    use_regex: bool = False,
    case_sensitive: bool = False,
    max_depth: int = 0,
    max_results: int = 100,
    count_only: bool = False,
) -> str
```

## Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `paths` | `str` | required | Space-separated list of file or directory paths to search in. |
| `query` | `str` | required | Text or regular expression to search for. Must not be empty. |
| `use_regex` | `bool` | `False` | If `True`, treat `query` as a regular expression. If `False`, treat as plain text. |
| `case_sensitive` | `bool` | `False` | If `False`, perform a case-insensitive search. |
| `max_depth` | `int` | `0` | Maximum directory depth to search. `0` = unlimited recursion. `1` = top-level only. |
| `max_results` | `int` | `100` | Maximum number of matching lines to return. `0` = no limit. |
| `count_only` | `bool` | `False` | If `True`, return only match counts instead of the actual lines. |

## Returns

- **Lines mode** (`count_only=False`): newline-separated list of matches, each formatted as:
  ```
  filepath:lineno: line content
  ```
- **Count mode** (`count_only=True`): summary of matches per file plus a total.

## Examples

### Plain-text search
```bash
search_text(paths="src", query="TODO")
```

### Regex search
```bash
search_text(paths="src tests", query=r"def\s+\w+", use_regex=True)
```

### Case-insensitive count
```bash
search_text(paths="docs", query="janito", case_sensitive=False, count_only=True)
```

### Limit depth
```bash
search_text(paths=".", query="import", max_depth=1)
```

### Unlimited results
```bash
search_text(paths=".", query="print", max_results=0)
```