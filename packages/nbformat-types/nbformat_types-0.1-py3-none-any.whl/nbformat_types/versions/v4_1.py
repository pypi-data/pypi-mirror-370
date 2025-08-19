from typing import Any, Literal, Required, TypedDict, Union


class Document(TypedDict, total=False):
    """ IPython Notebook v4.1 JSON schema. """

    metadata: Required["_DocumentMetadata"]
    """
    Notebook root-level metadata.

    Required property
    """

    nbformat_minor: Required[int]
    """
    Notebook format (minor number). Incremented for backward compatible changes to the notebook format.

    minimum: 1

    Required property
    """

    nbformat: Required[int]
    """
    Notebook format (major number). Incremented between backwards incompatible changes to the notebook format.

    minimum: 4
    maximum: 4

    Required property
    """

    cells: Required[list["_Cell"]]
    """
    Array of cells of the current notebook.

    Required property
    """



_Cell = Union["_RawCell", "_MarkdownCell", "_CodeCell"]
""" Aggregation type: oneOf """



class _CodeCell(TypedDict, total=False):
    """ Notebook code cell. """

    cell_type: Required["_CodeCellCellType"]
    """
    String identifying the type of cell.

    Required property
    """

    metadata: Required["_CodeCellMetadata"]
    """
    Cell-level metadata.

    Required property
    """

    source: Required["_MiscMultilineString"]
    """
    Aggregation type: oneOf

    Required property
    """

    outputs: Required[list["_Output"]]
    """
    Execution, display, or stream outputs.

    Required property
    """

    execution_count: Required[int | None]
    """
    The code cell's prompt number. Will be null if the cell has not been run.

    minimum: 0

    Required property
    """



_CodeCellCellType = Literal['code']
""" String identifying the type of cell. """
_CODECELLCELLTYPE_CODE: Literal['code'] = "code"
"""The values for the 'String identifying the type of cell' enum"""



class _CodeCellMetadata(TypedDict, total=False):
    """ Cell-level metadata. """

    collapsed: bool
    """ Whether the cell is collapsed/expanded. """

    scrolled: "_CodeCellMetadataScrolled"
    """ Whether the cell's output is scrolled, unscrolled, or autoscrolled. """

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



_CodeCellMetadataScrolled = Literal[True] | Literal[False] | Literal['auto']
""" Whether the cell's output is scrolled, unscrolled, or autoscrolled. """
_CODECELLMETADATASCROLLED_TRUE: Literal[True] = True
"""The values for the 'Whether the cell's output is scrolled, unscrolled, or autoscrolled' enum"""
_CODECELLMETADATASCROLLED_FALSE: Literal[False] = False
"""The values for the 'Whether the cell's output is scrolled, unscrolled, or autoscrolled' enum"""
_CODECELLMETADATASCROLLED_AUTO: Literal['auto'] = "auto"
"""The values for the 'Whether the cell's output is scrolled, unscrolled, or autoscrolled' enum"""



class _DisplayData(TypedDict, total=False):
    """ Data displayed as a result of code cell execution. """

    output_type: Required["_DisplayDataOutputType"]
    """
    Type of cell output.

    Required property
    """

    data: Required["_MiscMimebundle"]
    """
    A mime-type keyed dictionary of data

    patternProperties:
      ^application/(.*\\+)?json$:
        description: Mimetypes with JSON output, can be any type

    Required property
    """

    metadata: Required["_MiscOutputMetadata"]
    """
    Cell output metadata.

    Required property
    """



_DisplayDataOutputType = Literal['display_data']
""" Type of cell output. """
_DISPLAYDATAOUTPUTTYPE_DISPLAY_DATA: Literal['display_data'] = "display_data"
"""The values for the 'Type of cell output' enum"""



class _DocumentMetadata(TypedDict, total=False):
    """ Notebook root-level metadata. """

    kernelspec: "_DocumentMetadataKernelspec"
    """ Kernel information. """

    language_info: "_DocumentMetadataLanguageInfo"
    """ Kernel information. """

    orig_nbformat: int
    """
    Original notebook format (major number) before converting the notebook between versions. This should never be written to a file.

    minimum: 1
    """



class _DocumentMetadataKernelspec(TypedDict, total=False):
    """ Kernel information. """

    name: Required[str]
    """
    Name of the kernel specification.

    Required property
    """

    display_name: Required[str]
    """
    Name to display in UI.

    Required property
    """



class _DocumentMetadataLanguageInfo(TypedDict, total=False):
    """ Kernel information. """

    name: Required[str]
    """
    The programming language which this kernel runs.

    Required property
    """

    codemirror_mode: str | dict[str, Any]
    """
    The codemirror mode to use for code in this language.

    Aggregation type: oneOf
    """

    file_extension: str
    """ The file extension for files in this language. """

    mimetype: str
    """ The mimetype corresponding to files in this language. """

    pygments_lexer: str
    """ The pygments lexer to use for code in this language. """



class _Error(TypedDict, total=False):
    """ Output of an error that occurred during code cell execution. """

    output_type: Required["_ErrorOutputType"]
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



_ErrorOutputType = Literal['error']
""" Type of cell output. """
_ERROROUTPUTTYPE_ERROR: Literal['error'] = "error"
"""The values for the 'Type of cell output' enum"""



class _ExecuteResult(TypedDict, total=False):
    """ Result of executing a code cell. """

    output_type: Required["_ExecuteResultOutputType"]
    """
    Type of cell output.

    Required property
    """

    execution_count: Required[int | None]
    """
    A result's prompt number.

    minimum: 0

    Required property
    """

    data: Required["_MiscMimebundle"]
    """
    A mime-type keyed dictionary of data

    patternProperties:
      ^application/(.*\\+)?json$:
        description: Mimetypes with JSON output, can be any type

    Required property
    """

    metadata: Required["_MiscOutputMetadata"]
    """
    Cell output metadata.

    Required property
    """



_ExecuteResultOutputType = Literal['execute_result']
""" Type of cell output. """
_EXECUTERESULTOUTPUTTYPE_EXECUTE_RESULT: Literal['execute_result'] = "execute_result"
"""The values for the 'Type of cell output' enum"""



class _MarkdownCell(TypedDict, total=False):
    """ Notebook markdown cell. """

    cell_type: Required["_MarkdownCellCellType"]
    """
    String identifying the type of cell.

    Required property
    """

    metadata: Required["_MarkdownCellMetadata"]
    """
    Cell-level metadata.

    Required property
    """

    attachments: "_MiscAttachments"
    """ Media attachments (e.g. inline images), stored as mimebundle keyed by filename. """

    source: Required["_MiscMultilineString"]
    """
    Aggregation type: oneOf

    Required property
    """



_MarkdownCellCellType = Literal['markdown']
""" String identifying the type of cell. """
_MARKDOWNCELLCELLTYPE_MARKDOWN: Literal['markdown'] = "markdown"
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



_MiscAttachments = dict[str, "_MiscMimebundle"]
""" Media attachments (e.g. inline images), stored as mimebundle keyed by filename. """



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



_MiscMimebundle = dict[str, "_MiscMultilineString"]
"""
A mime-type keyed dictionary of data

patternProperties:
  ^application/(.*\\+)?json$:
    description: Mimetypes with JSON output, can be any type
"""



_MiscMultilineString = str | list[str]
""" Aggregation type: oneOf """



_MiscOutputMetadata = dict[str, Any]
""" Cell output metadata. """



_Output = Union["_ExecuteResult", "_DisplayData", "_Stream", "_Error"]
""" Aggregation type: oneOf """



class _RawCell(TypedDict, total=False):
    """ Notebook raw nbconvert cell. """

    cell_type: Required["_RawCellCellType"]
    """
    String identifying the type of cell.

    Required property
    """

    metadata: Required["_RawCellMetadata"]
    """
    Cell-level metadata.

    Required property
    """

    attachments: "_MiscAttachments"
    """ Media attachments (e.g. inline images), stored as mimebundle keyed by filename. """

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

    name: Required[str]
    """
    The name of the stream (stdout, stderr).

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

