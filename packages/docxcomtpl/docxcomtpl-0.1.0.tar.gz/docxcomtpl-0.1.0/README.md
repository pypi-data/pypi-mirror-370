# docxcomtpl

**docxcomtpl** is a Python library for generating DOCX documents using templates.
It is based upon the [python-docx-template](https://github.com/elapouya/python-docx-template) library,
that generates DOCX documents using Jinja-like templating syntax.
It generates documents using pure Python code, which provides good performance and reliability, but limits the possibilities.

The `docxcomtpl` library extends the functionality of the original library by adding support for COM automation.

This allows you to generate more complex documents using the full range of Microsoft Word features.



---

## Features

- **Direct generation of DOCX documents with text and images** — provides good performance and reliability.
- **Jinja-like Placeholder Syntax** — easy-to-use templating for text and images.
- **COM Automation Support** — integrate COM calls to extend document generation capabilities, at the cost of performance.
- **MIT Licensed** — free and open-source with a permissive license.
---

## Template Syntax

See https://docxtpl.readthedocs.io/en/latest/#jinja2-like-syntax for the detailed documentation of the template syntax.

## DOCX generation with COM Automation

To generate a document, create an instance of `DocxComTemplate` class, passing the path to the template DOCX file.
Then call the `generate` method with the data dictionary and the output file path.

To insert data using COM, put *inserter fucntion* instead of the value in the data. Inserter functions
take single argument which is Word.Range object, and insert desired data into it.

Module `docxcomtpl.com_utilities` provides some useful inserters.

```python
from docxcomtpl import DocxComTemplate
from docxcomtpl.com_utilities import table_inserter

# Load the template
template = DocxComTemplate("template.docx")

# Define the data for the template
data = {
    "header": "My Document",
    "table": table_inserter([["Col1", "Col2"], ["Row1", "Row2"]])
}
# Render the template with data
template.generate(data, "output.docx")
```
The template and the resulting document are shown below:

![COM Template and result](/doc/template_com.png)

### Complete list of inserter functions, available in `docxcomtpl.com_utilities` module:
| Function                               | Description                                                                                  |
|----------------------------------------|----------------------------------------------------------------------------------------------|
| `table_inserter(data:List[List[str]])  | Inserts a table with the given data. Each sublist represents a row.                          |
| `image_inserter(picture_path:str)`     | Inserts an image from the specified path using COM. Supports more formats than the DOCX mode |
| `document_inserter(document_path:str)` | Inserts content of another document, can be DOCX, RTF or anything supported by Word.       |
| `anchor_inserter(text:str, anchor:str)` | Inserts an anchor with the given text and name.                                           |
| `heading_inserter(text:str, level:int=1)` | Inserts a heading with the given text and level. Level 1 is the highest level.             |

### COM Post-Processing

WHen generating documents using COM-assisted mode (`DocxComTemplate`), you can use post-processing to modify the document after it has been generated.
To do this, specify the `postprocess` argument when calling the `DocxComTemplate.generate` method.
Library `docxcomtpl.com_utilities` provides an example post-processing function that updates document creation date and table of content:

```python
from docxcomtpl.docxcom_template import DocxComTemplate
from docxcomtpl.com_utilities import update_document_toc

template = DocxComTemplate("template.docx")
data = ...
template.generate(
    data,
    "output.docx",
    postprocess=update_document_toc
)
```

Post-processing function must take single argument which is the Word.Document object.

## Requirements
- Python 3.7 or higher
- `pywin32` package for COM automation
- Microsoft Word installed (optional, for DOCX + COM mode)

## Installation

You can install Pymsword using pip:

```bash
pip install docxcomtpl
```

## License
This project is licensed under the MIT License - see the [LICENSE.MIT](LICENSE.MIT) file for details.
