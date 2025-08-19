## Jupyter Tools Action

This action provides a comprehensive set of tools for manipulating Jupyter notebooks in your project.

### Features

The Jupyter Tools action adds the following capabilities to your project:

#### Scripts Available

1. **py_to_notebook.py** - Convert Python files to Jupyter notebooks
   - Handles cell markers and tags
   - Preserves markdown links
   - Supports jupytext format

2. **execute_notebook.py** - Execute Jupyter notebooks
   - Runs notebooks with proper error handling
   - Updates execution metadata
   - Supports parameterized execution

3. **notebook_to_html.py** - Convert notebooks to HTML
   - Creates standalone HTML files
   - Includes CSS styling
   - Preserves code highlighting

4. **notebook_to_pdf.py** - Convert notebooks to PDF
   - Uses nbconvert with LaTeX backend
   - Supports custom templates
   - Handles complex formatting

5. **main.py** - Main CLI interface
   - Process entire directories
   - Complete pipeline from Python to HTML
   - Batch processing capabilities

#### Dependencies Added

The following dependencies are automatically added to your project's dev group:

- `jupytext` - For Python to notebook conversion
- `nbconvert` - For notebook format conversion
- `weasyprint` - For PDF generation
- `pandoc` - For document conversion

### Usage

After running this action, you'll have a `tools/` directory in your project with all the scripts ready to use:

```bash
## Convert a Python file to notebook
python tools/py_to_notebook.py input.py output.ipynb

## Execute a notebook
python tools/execute_notebook.py notebook.ipynb

## Convert notebook to HTML
python tools/notebook_to_html.py notebook.ipynb output.html

## Convert notebook to PDF
python tools/notebook_to_pdf.py notebook.ipynb output.pdf

## Process all Python files in a directory
python tools/main.py notebooks/
```

### Integration

This action integrates seamlessly with the Jupyter action, providing additional tools for notebook manipulation beyond the basic Jupyter setup.

### Requirements

- Requires the `core` and `jupyter` actions to be run first
- Poetry project structure
- Python 3.7+
