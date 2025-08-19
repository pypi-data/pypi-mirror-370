from typing import Any, Literal, Required, TypedDict, Union


class Document(TypedDict, total=False):
    """ IPython Notebook v3.0 JSON schema. """

    metadata: Required["_DocumentMetadata"]
    """
    Notebook root-level metadata.

    Required property
    """

    nbformat_minor: Required[int]
    """
    Notebook format (minor number). Incremented for backward compatible changes to the notebook format.

    minimum: 0

    Required property
    """

    nbformat: Required[int]
    """
    Notebook format (major number). Incremented between backwards incompatible changes to the notebook format.

    minimum: 3
    maximum: 3

    Required property
    """

    orig_nbformat: int
    """
    Original notebook format (major number) before converting the notebook between versions.

    minimum: 1
    """

    orig_nbformat_minor: int
    """
    Original notebook format (minor number) before converting the notebook between versions.

    minimum: 0
    """

    worksheets: Required[list["_Worksheet0"]]
    """
    Array of worksheets

    Required property
    """



class _CodeCell(TypedDict, total=False):
    """ Notebook code cell. """

    cell_type: Required["_CodeCellCellType"]
    """
    String identifying the type of cell.

    Required property
    """

    language: Required[str]
    """
    The cell's language (always Python)

    Required property
    """

    collapsed: bool
    """ Whether the cell is collapsed/expanded. """

    metadata: dict[str, Any]
    """ Cell-level metadata. """

    input: Required["_MiscMultilineString"]
    """
    Aggregation type: oneOf

    Required property
    """

    outputs: Required[list["_Output"]]
    """
    Execution, display, or stream outputs.

    Required property
    """

    prompt_number: int | None
    """
    The code cell's prompt number. Will be null if the cell has not been run.

    minimum: 0
    """



_CodeCellCellType = Literal['code']
""" String identifying the type of cell. """
_CODECELLCELLTYPE_CODE: Literal['code'] = "code"
"""The values for the 'String identifying the type of cell' enum"""



_DisplayData = Union[dict[str, "_MiscMultilineString"], "_DisplayDataTyped"]
"""
Data displayed as a result of code cell execution.


WARNING: Normally the types should be a mix of each other instead of Union.
See: https://github.com/camptocamp/jsonschema-gentypes/issues/7
"""



_DisplayDataOutputType = Literal['display_data']
""" Type of cell output. """
_DISPLAYDATAOUTPUTTYPE_DISPLAY_DATA: Literal['display_data'] = "display_data"
"""The values for the 'Type of cell output' enum"""



class _DisplayDataTyped(TypedDict, total=False):
    output_type: Required["_DisplayDataOutputType"]
    """
    Type of cell output.

    Required property
    """

    text: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    latex: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    png: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    jpeg: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    svg: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    html: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    javascript: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    json: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    pdf: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    metadata: "_MiscOutputMetadata"
    """ Cell output metadata. """



class _DocumentMetadata(TypedDict, total=False):
    """ Notebook root-level metadata. """

    kernel_info: "_DocumentMetadataKernelInfo"
    """ Kernel information. """

    signature: str
    """ Hash of the notebook. """



class _DocumentMetadataKernelInfo(TypedDict, total=False):
    """ Kernel information. """

    name: Required[str]
    """
    Name of the kernel specification.

    Required property
    """

    language: Required[str]
    """
    The programming language which this kernel runs.

    Required property
    """

    codemirror_mode: str
    """ The codemirror mode to use for code in this language. """



class _HeadingCell(TypedDict, total=False):
    """ Notebook heading cell. """

    cell_type: Required["_HeadingCellCellType"]
    """
    String identifying the type of cell.

    Required property
    """

    metadata: dict[str, Any]
    """ Cell-level metadata. """

    source: Required["_MiscMultilineString"]
    """
    Aggregation type: oneOf

    Required property
    """

    level: Required[int]
    """
    Level of heading cells.

    minimum: 1

    Required property
    """



_HeadingCellCellType = Literal['heading']
""" String identifying the type of cell. """
_HEADINGCELLCELLTYPE_HEADING: Literal['heading'] = "heading"
"""The values for the 'String identifying the type of cell' enum"""



class _MarkdownCell(TypedDict, total=False):
    """ Notebook markdown cell. """

    cell_type: Required["_MarkdownCellCellType"]
    """
    String identifying the type of cell.

    Required property
    """

    metadata: "_MarkdownCellMetadata"
    """ Cell-level metadata. """

    source: Required["_MiscMultilineString"]
    """
    Aggregation type: oneOf

    Required property
    """



_MarkdownCellCellType = Literal['markdown'] | Literal['html']
""" String identifying the type of cell. """
_MARKDOWNCELLCELLTYPE_MARKDOWN: Literal['markdown'] = "markdown"
"""The values for the 'String identifying the type of cell' enum"""
_MARKDOWNCELLCELLTYPE_HTML: Literal['html'] = "html"
"""The values for the 'String identifying the type of cell' enum"""



class _MarkdownCellMetadata(TypedDict, total=False):
    """ Cell-level metadata. """

    name: "_MiscMetadataName"
    """
    The cell's name. If present, must be a non-empty string.

    pattern: ^.+$
    """

    tags: "_MiscMetadataTags"
    """
    The cell's tags. Tags must be unique, and must not contain commas.

    uniqueItems: True
    """



_MiscMetadataName = str
"""
The cell's name. If present, must be a non-empty string.

pattern: ^.+$
"""



_MiscMetadataTags = list["_MiscMetadataTagsItem"]
"""
The cell's tags. Tags must be unique, and must not contain commas.

uniqueItems: True
"""



_MiscMetadataTagsItem = str
""" pattern: ^[^,]+$ """



_MiscMultilineString = str | list[str]
""" Aggregation type: oneOf """



_MiscOutputMetadata = dict[str, Any]
""" Cell output metadata. """



_Output = Union["_Pyout", "_DisplayData", "_Stream", "_Pyerr"]
""" Aggregation type: oneOf """



class _Pyerr(TypedDict, total=False):
    """ Output of an error that occurred during code cell execution. """

    output_type: Required["_PyerrOutputType"]
    """
    Type of cell output.

    Required property
    """

    ename: Required[str]
    """
    The name of the error.

    Required property
    """

    evalue: Required[str]
    """
    The value, or message, of the error.

    Required property
    """

    traceback: Required[list[str]]
    """
    The error's traceback, represented as an array of strings.

    Required property
    """



_PyerrOutputType = Literal['pyerr']
""" Type of cell output. """
_PYERROUTPUTTYPE_PYERR: Literal['pyerr'] = "pyerr"
"""The values for the 'Type of cell output' enum"""



_Pyout = Union[dict[str, "_MiscMultilineString"], "_PyoutTyped"]
"""
Result of executing a code cell.


WARNING: Normally the types should be a mix of each other instead of Union.
See: https://github.com/camptocamp/jsonschema-gentypes/issues/7
"""



_PyoutOutputType = Literal['pyout']
""" Type of cell output. """
_PYOUTOUTPUTTYPE_PYOUT: Literal['pyout'] = "pyout"
"""The values for the 'Type of cell output' enum"""



class _PyoutTyped(TypedDict, total=False):
    output_type: Required["_PyoutOutputType"]
    """
    Type of cell output.

    Required property
    """

    prompt_number: Required[int]
    """
    A result's prompt number.

    minimum: 0

    Required property
    """

    text: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    latex: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    png: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    jpeg: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    svg: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    html: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    javascript: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    json: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    pdf: "_MiscMultilineString"
    """ Aggregation type: oneOf """

    metadata: "_MiscOutputMetadata"
    """ Cell output metadata. """



class _RawCell(TypedDict, total=False):
    """ Notebook raw nbconvert cell. """

    cell_type: Required["_RawCellCellType"]
    """
    String identifying the type of cell.

    Required property
    """

    metadata: "_RawCellMetadata"
    """ Cell-level metadata. """

    source: Required["_MiscMultilineString"]
    """
    Aggregation type: oneOf

    Required property
    """



_RawCellCellType = Literal['raw']
""" String identifying the type of cell. """
_RAWCELLCELLTYPE_RAW: Literal['raw'] = "raw"
"""The values for the 'String identifying the type of cell' enum"""



class _RawCellMetadata(TypedDict, total=False):
    """ Cell-level metadata. """

    format: str
    """ Raw cell metadata format for nbconvert. """

    name: "_MiscMetadataName"
    """
    The cell's name. If present, must be a non-empty string.

    pattern: ^.+$
    """

    tags: "_MiscMetadataTags"
    """
    The cell's tags. Tags must be unique, and must not contain commas.

    uniqueItems: True
    """



class _Stream(TypedDict, total=False):
    """ Stream output from a code cell. """

    output_type: Required["_StreamOutputType"]
    """
    Type of cell output.

    Required property
    """

    stream: Required[str]
    """
    The stream type/destination.

    Required property
    """

    text: Required["_MiscMultilineString"]
    """
    Aggregation type: oneOf

    Required property
    """



_StreamOutputType = Literal['stream']
""" Type of cell output. """
_STREAMOUTPUTTYPE_STREAM: Literal['stream'] = "stream"
"""The values for the 'Type of cell output' enum"""



_Worksheet0 = Union[str, int | float, "_WorksheetObject", list[Any], bool, None]
""" additionalProperties: False """



class _WorksheetObject(TypedDict, total=False):
    cells: Required[list["_WorksheetObjectCellsItem"]]
    """
    Array of cells of the current notebook.

    Required property
    """

    metadata: dict[str, Any]
    """ metadata of the current worksheet """



_WorksheetObjectCellsItem = Union["_RawCell", "_MarkdownCell", "_HeadingCell", "_CodeCell"]
""" Aggregation type: oneOf """

