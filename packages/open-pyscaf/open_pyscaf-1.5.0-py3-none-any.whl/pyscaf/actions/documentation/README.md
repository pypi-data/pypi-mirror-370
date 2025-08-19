## Documentation

This action uses [pdoc](https://pdoc.dev/) to generate and serve documentation for your Python project.

### Configuration

The documentation configuration is managed in your `pyproject.toml` file:

```toml
[tool.pyscaf.documentation]
output_path = "docs"

[tool.pyscaf.documentation.pdoc]
# pdoc arguments are automatically converted to CLI arguments
# Boolean values: true -> --flag, false -> --no-flag
# Lists: ["value1", "value2"] -> --flag value1 --flag value2
# Strings: "value" -> --flag value
```

### Scripts

Two scripts are available to manage documentation. Both scripts use the configuration defined in the `[tool.pyscaf.documentation.pdoc]`:

#### `gen-doc`

Generates static documentation files to the directory specified in `tool.pyscaf.documentation.output_path`.

```bash
poetry run gen-doc
```

#### `serve-doc`

Starts a local documentation server for interactive browsing.

```bash
poetry run serve-doc
```

### pdoc Arguments

All arguments in the `[tool.pyscaf.documentation.pdoc]` section are automatically converted to pdoc CLI arguments:

- Boolean values: `true` becomes `--flag`, `false` becomes `--no-flag`
- Lists: `["value1", "value2"]` becomes `--flag value1 --flag value2`
- Strings: `"value"` becomes `--flag value`

`output` argument is droped, as the behaviour to write instead of serve depends on the script use.

For example:
```toml
[tool.pyscaf.documentation.pdoc]
html = true
show_source = false
template_directory = "custom_templates"
external_links = ["https://example.com"]
```

Becomes:
```bash
pdoc --html --no-show-source --template-directory custom_templates --external-links https://example.com
``` 