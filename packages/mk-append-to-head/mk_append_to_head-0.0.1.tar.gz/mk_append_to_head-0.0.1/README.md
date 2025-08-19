# mk-append-to-head
Append some string to a MkDocs page's &lt;head>.

## Installation

```bash
pip install mk-append-to-head
```

## Configuration

In MkDocs configuration file:

```yaml title="mkdocs.yml"
plugins:
- mk-append-to-head:
    append_str: <script>console.log(1)</script>
    pages: ['Home'] # optional
```

Leaving `pages` empty will append the `append_str` to all pages.