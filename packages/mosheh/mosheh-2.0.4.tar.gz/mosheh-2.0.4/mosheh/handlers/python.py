"""
This file's role is process the source python codebase.

By calling `handle_std_nodes` with an `ast.AST` node, it's going to parse the node type
and call the right handle func. The defined nodes are `ast.Import`, `ast.ImportFrom`,
`ast.Assign`, `ast.AnnAssign`, `ast.FunctionDef`, `ast.AsyncFunctionDef`, `ast.ClassDef`
and `ast.Assert`; if more nodes inside them, `_handle_node` is called to process the new
one.
"""

import ast
from collections import defaultdict
from logging import Logger, getLogger
from os import sep
from typing import Any, Final

from mosheh.constants import (
    ACCEPTABLE_LOWER_CONSTANTS,
    BUILTIN_DUNDER_METHODS,
    BUILTIN_MODULES,
)
from mosheh.types.basic import (
    Annotation,
    Args,
    AssertionMessage,
    AssertionTest,
    CodeSnippet,
    Decorator,
    DefaultValue,
    Docstring,
    FilePath,
    ImportedIdentifier,
    Inheritance,
    Kwargs,
    ModulePath,
    StandardReturn,
    Token,
    Value,
)
from mosheh.types.contracts import (
    AnnAssignContract,
    AssertContract,
    AssignContract,
    AsyncFunctionDefContract,
    ClassDefContract,
    FunctionDefContract,
    ImportContract,
    ImportFromContract,
)
from mosheh.types.enums import (
    FileRole,
    FunctionType,
    ImportType,
    Statement,
)
from mosheh.utils import (
    add_to_nested_defaultdict,
    bin,
    get_import_type,
    standard_struct,
)


logger: Logger = getLogger('mosheh')


def handle_python_file(
    codebase: defaultdict[Any, Any], file: FilePath
) -> defaultdict[Any, Any]:
    """
    Processes the .py file and returns it's data.

    By receiving the codebase datastructure, empty or not, and a file_path, first
    parses the code, then defines the file metadata, such as role (from
    `types.enums.FileRole`), navigates into it's AST nodes (statements) and calls the
    `handle_std_nodes` function for dealing with the default observed statements.

    :param codebase: Nested defaultdict with the codebase data, empty or not.
    :type codebase: defaultdict[Any, Any]
    :param file: Path for the Python file to be documented.
    :type file: FilePath
    :return: The same codebase data struct, with the parsed file.
    :rtype: defaultdict[Any, Any]
    """

    with open(file, encoding='utf-8') as f:
        code: str = f.read()

    tree: ast.AST = ast.parse(code, filename=file)
    logger.debug('\tCode tree parsed')

    statements: list[StandardReturn] = []

    __meta__: StandardReturn = {
        '__role__': (
            FileRole.PythonSourceCode
            if file.endswith('.py')
            else FileRole.PythonStubFile
        ),
        '__docstring__': 'No file docstring provided.',
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Module) and (__docstring__ := ast.get_docstring(node)):
            __meta__['__docstring__'] = __docstring__
        elif isinstance(node, ast.ClassDef):
            _mark_methods(node)
        elif isinstance(node, ast.FunctionDef) and getattr(node, 'parent', None):
            continue

        data: list[StandardReturn] = _handle_std_nodes(node)

        if data:
            statements.extend(data)
            logger.debug("\tNode inserted into file's structure")

    statements.insert(0, __meta__)

    add_to_nested_defaultdict(codebase, file.split(sep), statements)
    logger.debug(f'\t{file} parsing successfully done')

    return codebase


def _handle_std_nodes(node: ast.AST) -> list[StandardReturn]:
    """
    Processes an abstract syntax tree (AST) node and returns a handler for the node.

    This function analyzes a given `ast.AST` node, determines its type, and processes
    it using the appropriate handler function. It supports a variety of node types such
    as imports, constants, functions, classes, and assertions, delegating the handling
    to specialized functions for each case.

    The function categorizes and handles nodes as follows:
    - Imports: `ast.Import | ast.ImportFrom`
    - Constants: `ast.Assign | ast.AnnAssign`
    - Functions: `ast.FunctionDef | ast.AsyncFunctionDef`
    - Classes: `ast.ClassDef`
    - Assertions: `ast.Assert`

    :param node: The AST node to process.
    :type node: ast.AST
    :return: An object containing information associated with the node.
    :rtype: list[StandardReturn]
    """

    data: list[StandardReturn] = []

    if not isinstance(
        node,
        ast.Import
        | ast.ImportFrom
        | ast.Assign
        | ast.AnnAssign
        | ast.FunctionDef
        | ast.AsyncFunctionDef
        | ast.ClassDef
        | ast.Assert,
    ):
        return data

    logger.debug(f'\tStd node found: {type(node)}')

    # -------------------------
    # Imports - ast.Import | ast.ImportFrom
    # -------------------------

    if isinstance(node, ast.Import):
        data = _handle_import(data, node)
    elif isinstance(node, ast.ImportFrom):
        data = _handle_import_from(data, node)

    # -------------------------
    # Constants - ast.Assign | ast.AnnAssign
    # -------------------------

    elif isinstance(node, ast.Assign):
        lst: list[str] = []
        for i in node.targets:
            lst.extend(_handle_node(i))

        if any(map(str.isupper, lst)) or any(
            map(lambda x: bin(x, ACCEPTABLE_LOWER_CONSTANTS), lst)
        ):
            data = _handle_assign(data, node)
    elif isinstance(node, ast.AnnAssign):
        if isinstance(node.target, ast.Name) and node.target.id.isupper():
            data = _handle_annassign(data, node)

    # -------------------------
    # Functions - ast.FunctionDef | ast.AsyncFunctionDef
    # -------------------------

    elif isinstance(node, ast.FunctionDef):
        data = _handle_function_def(data, node)
    elif isinstance(node, ast.AsyncFunctionDef):
        data = _handle_async_function_def(data, node)

    # -------------------------
    # Classes - ast.ClassDef
    # -------------------------

    elif isinstance(node, ast.ClassDef):
        data = _handle_class_def(data, node)

    # -------------------------
    # Assertions - ast.Assert
    # -------------------------

    else:
        data = _handle_assert(data, node)

    return data


def _handle_node(node: ast.AST) -> list[str]:
    """
    Converts an AST node back into its string representation.

    This function takes an AST node and uses `ast.unparse` to convert it
    into the equivalent source code. It returns the string inside a list
    to maintain a consistent return type with other handlers.

    Key concepts:
    - AST Parsing: The core concept is converting an AST object back to source code.
    - Null-Safe Handling: If the node is `None`, it returns `None` to avoid errors.

    :param node: The AST node to be processed.
    :type node: ast.AST
    :return: A list containing the unparsed source code, or 'None' if the node is None.
    :rtype: list[str]
    """

    return [ast.unparse(node)]


def __handle_import(imported_identifier: ImportedIdentifier) -> StandardReturn:
    """
    Constructs a standardized dictionary representation for an import statement.

    This function processes the given library name, determines its import category
    (local, native, or third-party), and builds a standardized dictionary structure
    representing the import statement. The resulting data includes information about
    the statement type, library name, import category, and the generated import code.

    Key concepts:
    - Import Categorization: Determines whether the library is native (built-in),
      third-party, or local.
    - Standardized Structure: Returns a dictionary conforming to the `StandardReturn`
      format, ensuring consistency across codebase documentation.
    - Dynamic Code Generation: Constructs the import statement dynamically based on
      the library name.

    Example:

    ```python
    data: StandardReturn = __handle_import('os')
    data
    # {
    #     'statement': Statement.Import,
    #     'name': 'os',
    #     'path': None,
    #     'category': ImportType.Native,
    #     'code': 'import os',
    # }
    ```

    :param imported_identifier: The name of the lib, mod or element imported.
    :type imported_identifier: ImportedIdentifier
    :return: A standardized dictionary representing the import statement.
    :rtype: list[StandardReturn]
    """

    statement: Final[Statement] = Statement.Import
    path: Final[None] = None
    category: ImportType = get_import_type(imported_identifier)

    contract: ImportContract = ImportContract(
        statement=statement,
        name=imported_identifier,
        path=path,
        category=category,
        code=f'import {imported_identifier}',
    )

    data: StandardReturn = standard_struct()

    data.update(contract._asdict())

    return data


def _handle_import(
    struct: list[StandardReturn], node: ast.Import
) -> list[StandardReturn]:
    """
    Updates a standard structure with information from an import statement node.

    This function processes an AST import node, extracts the library names being
    imported, and updates the given `StandardReturn` structure with details about
    each library. It leverages the `__handle_import` function to standardize the data
    for each imported library.

    Key concepts:
    - AST Parsing: Processes Python's AST nodes for import statements.
    - Data Standardization: Utilizes `__handle_import` to format each import into a
      consistent structure.
    - Structure Update: Modifies the provided `struct` in-place with import data.

    Example:

    ```python
    import ast

    node: ast.AST = ast.parse('import os, sys').body[0]
    updated_struct: list[StandardReturn] = _handle_import([], node)
    updated_struct
    # Outputs standardized data for `os` and `sys` imports.
    ```

    :param struct: The structure to be updated with statement details.
    :type struct: list[StandardReturn]
    :param node: The AST node representing an import statement.
    :type node: ast.Import
    :return: The updated structure with information about the imported libraries.
    :rtype: list[StandardReturn]
    """

    for lib in [i.name for i in node.names]:
        struct.append(__handle_import(lib))

    return struct


def _handle_import_from(
    struct: list[StandardReturn], node: ast.ImportFrom
) -> list[StandardReturn]:
    """
    Processes an `ast.ImportFrom` node and returns its data.

    This function iterates over the imported module names within an `ast.ImportFrom`
    node, classifying each module into one of the following categorys, as
    `handle_import`:
    - Native: The module is a built-in Python module.
    - Third-Party: The module is installed via external libraries.
    - Local: The module is neither built-in nor a third-party library, problably local.

    Each module's data includes its path and category, stored in a structured dict.

    Example:

    ```python
    import ast

    node: ast.AST = ast.parse('from os import environ').body[0]
    updated_struct: list[StandardReturn] = _handle_import_from([], node)
    updated_struct
    # Outputs standardized data for `environ` with `os` as path.
    ```

    :param struct: The structure to be updated with statement details.
    :type struct: list[StandardReturn]
    :param node: The AST node representing an import statement.
    :type node: ast.ImportFrom
    :return: A dict containing the statement type and categorized module information.
    :rtype: list[StandardReturn]
    """

    statement: Final[Statement] = Statement.ImportFrom
    names: Final[list[ImportedIdentifier]] = [i.name for i in node.names]
    path: Final[ModulePath | None] = node.module
    category: ImportType = ImportType.Local
    code: Final[CodeSnippet] = ast.unparse(node)

    if bin(
        f'{path}.'.split('.')[0],
        BUILTIN_MODULES,
    ):
        category = ImportType.Native
    elif get_import_type(str(path)):
        category = ImportType.TrdParty

    for i in names:
        contract: ImportFromContract = ImportFromContract(
            statement=statement,
            name=i,
            path=path,
            category=category,
            code=code,
        )
        data: StandardReturn = standard_struct()
        data.update(contract._asdict())

        struct.append(data)

    return struct


def _handle_assign(
    struct: list[StandardReturn], node: ast.Assign
) -> list[StandardReturn]:
    """
    Processes an `ast.Assign` node and returns its data.

    This function analyzes the components of an assignment, including the target vars
    and the assigned value, returning a structured dict with the extracted details.

    Key elements of the returned data:
    - tokens: A list of string repr for all target variables in the assignment.
    - value: A string repr of the value being assigned.

    Example:

    ```python
    import ast

    node: ast.AST = ast.parse('num = 33').body[0]
    updated_struct: list[StandardReturn] = _handle_assign([], node)
    updated_struct
    # Outputs standardized data for `num` definition.
    ```

    :param struct: The structure to be updated with statement details.
    :type struct: list[StandardReturn]
    :param node: The AST node representing the node statement.
    :type node: ast.Assign
    :return: A dict containing the statement type, target variables, and assigned value.
    :rtype: list[StandardReturn]
    """

    statement: Final[Statement] = Statement.Assign
    tokens: Final[list[Token]] = [_handle_node(i)[0] for i in node.targets]
    value: Final[Value] = _handle_node(node.value)[0]
    code: Final[CodeSnippet] = ast.unparse(node)

    contract: AssignContract = AssignContract(
        statement=statement,
        tokens=tokens,
        value=value,
        code=code,
    )

    data: StandardReturn = standard_struct()

    data.update(contract._asdict())

    struct.append(data)

    return struct


def _handle_annassign(
    struct: list[StandardReturn], node: ast.AnnAssign
) -> list[StandardReturn]:
    """
    Processes an `ast.AnnAssign` node and returns its data.

    This function analyzes the components of an assignment, including the target var
    and the assigned value, plus the typing annotation, returning a structured dict with
    the extracted details.

    Key elements of the returned data:
    - token: A string repr for the target var in the assignment.
    - value: A string repr of the value being assigned.
    - annot: The type hint for the assignment.

    Example:

    ```python
    import ast

    node: ast.AST = ast.parse('num: int = 33').body[0]
    updated_struct: list[StandardReturn] = _handle_anassign([], node)
    updated_struct
    # Outputs standardized data for `num` definition with `int` annotation.
    ```

    :param struct: The structure to be updated with statement details.
    :type struct: list[StandardReturn]
    :param node: The AST node representing the node statement.
    :type node: ast.AnnAssign
    :return: A dict with the statement type, target var, type hint and assigned value.
    :rtype: list[StandardReturn]
    """

    statement: Statement = Statement.AnnAssign
    name: Token = _handle_node(node.target)[0]
    annot: Annotation = _handle_node(node.annotation)[0]
    value: Value = _handle_node(node.value)[0] if node.value else ''
    code: CodeSnippet = ast.unparse(node)

    contract: AnnAssignContract = AnnAssignContract(
        statement=statement,
        name=name,
        annot=annot,
        value=value,
        code=code,
    )

    data: StandardReturn = standard_struct()

    data.update(contract._asdict())

    struct.append(data)

    return struct


def __format_arg(
    name: Token, annotation: Annotation | None, default: DefaultValue | None
) -> Args:
    """
    Formats a function argument into a string repr with optional type annotations and
    default values.

    This function constructs a f-string representing a function argument, including its
    name, optional type annotation, and default value. It ensures consistent formatting
    for use in function signatures or documentation.

    Key concepts:
    - Type Annotations: Adds type annotations if provided.
    - Default Values: Appends default values where applicable.
    - Fallback Handling: If neither an annotation nor a default value is present, it
      defaults to 'Unknown'.

    Example:

    ```python
    formatted: Args = __format_arg('param', 'int', '42')
    formatted
    # "param: int = 42"
    ```

    :param name: The name of the argument.
    :type name: Token
    :param annotation: The type annotation for the argument, if any.
    :type annotation: Annotation | None
    :param default: The default value of the argument, if any.
    :type default: DefaultValue | None
    :return: A formatted string representing the argument.
    :rtype: Args
    """

    if annotation and default:
        return f'{name}: {annotation} = {default}'
    elif annotation:
        return f'{name}: {annotation}'
    elif default:
        return f'{name} = {default}'
    else:
        return f'{name}: Unknown'


def __process_function_args(node_args: ast.arguments) -> str:
    """
    Processes and formats positional arguments from a function definition.

    This function extracts positional arguments from an `ast.arguments` node,
    including their names, optional type annotations, and default values.
    It formats them into a single, comma-separated string repr suitable
    for documentation or code generation.

    Key concepts:
    - Positional Argsuments: Handles arguments that can be passed by position.
    - Type Annotations: Extracts and formats type annotations, if present.
    - Default Values: Aligns each argument with its default value, if provided.

    Example:

    ```python
    import ast

    source: str = "def example(a: int, b: str = 'default'): pass"
    node: ast.AST = ast.parse(source).body[0]
    formatted: str = __process_function_args(node.args)
    formatted
    # "a: int, b: str = 'default'"
    ```

    :param node_args: The `arguments` node from an AST function definition.
    :type node_args: ast.arguments
    :return: A comma-separated string of formatted positional arguments.
    :rtype: str
    """

    formatted_args: list[Args] = []

    for i, arg in enumerate(node_args.args):
        name: Token = arg.arg
        annotation: Annotation | None = (
            _handle_node(arg.annotation)[0] if arg.annotation else None
        )

        default: DefaultValue | None = None

        if i < len(node_args.kw_defaults):
            default_node = node_args.kw_defaults[i]
            if default_node:
                default = _handle_node(default_node)[0]

        formatted_args.append(__format_arg(name, annotation, default))

    return ', '.join(formatted_args)


def __process_function_kwargs(node_args: ast.arguments) -> str:
    """
    Processes and formats keyword-only arguments from a function definition.

    This function extracts keyword-only arguments from an `ast.arguments` node,
    including their names, optional type annotations, and default values. It formats
    them into a single, comma-separated string repr suitable for documentation
    or code generation.

    Key concepts:
    - Keyword-only Argsuments: Processes arguments that must be passed by keyword.
    - Type Annotations: Extracts and formats type annotations if present.
    - Default Values: Handles default values, aligning them with their own arguments.

    Example:

    ```python
    import ast

    source: str = 'def example(*, debug: bool = True): pass'
    node: ast.AST = ast.parse(source).body[0]
    formatted: str = __process_function_kwargs(node.args)
    formatted
    # "debug: bool = True"
    ```

    :param node_args: The `arguments` node from an AST function definition.
    :type node_args: ast.arguments
    :return: A comma-separated string of formatted keyword-only arguments.
    :rtype: str
    """

    formatted_kwargs: list[str] = []

    for i, arg in enumerate(node_args.kwonlyargs):
        name: Kwargs = arg.arg
        annotation: Annotation | None = (
            _handle_node(arg.annotation)[0] if arg.annotation else None
        )

        default: DefaultValue | None = None

        if i < len(node_args.kw_defaults):
            default_node = node_args.kw_defaults[i]
            if default_node:
                default = _handle_node(default_node)[0]

        formatted_kwargs.append(__format_arg(name, annotation, default))

    return ', '.join(formatted_kwargs)


def __process_function_type(node: ast.FunctionDef, is_from_class: bool) -> FunctionType:
    """
    Determines the type of a function based on its context and structure.

    This function identifies whether a given function node from the AST is a method,
    a generator, or a regular function.

    - If is within a class or matches a dunder method name, it returns a `Method`.
    - Elif contains a `yield` type statements, it returns a `Generator`.
    - Otherwise, it returns a `Function`.

    :param node: The AST node representing the function.
    :type node: ast.FunctionDef
    :param is_from_class: Indicates if the function is defined within a class.
    :type is_from_class: bool
    :return: The type of the function (`Method`, `Generator`, or `Function`).
    :rtype: FunctionType
    """

    if is_from_class or bin(node.name, BUILTIN_DUNDER_METHODS):
        return FunctionType.Method

    elif any(isinstance(n, ast.Yield | ast.YieldFrom) for n in ast.walk(node)):
        return FunctionType.Generator

    return FunctionType.Function


def _handle_function_def(
    struct: list[StandardReturn], node: ast.FunctionDef, is_from_class: bool = False
) -> list[StandardReturn]:
    """
    Processes an `ast.FunctionDef` node and returns its data.

    This function analyzes the components of a func def, mapping the name, decorators,
    arguments (name, type, default value), return type and even the type of function it
    is:
    - Function: a base function, simply defined using `def` keyword.
    - Method: also base function, but defined inside a class (e.g. `def __init__():`).
    - Generator: process an iterable object at a time, on demand, with `yield` inside.

    Example:

    ```python
    import ast

    node: ast.AST = ast.parse('def foo(*args: Any): pass').body[0]
    updated_struct: list[StandardReturn] = _handle_function_def([], node)
    updated_struct
    # Outputs standardized data for `foo` definition.
    ```

    :param struct: The structure to be updated with statement details.
    :type struct: list[StandardReturn]
    :param node: The AST node representing a func def statement.
    :type node: ast.FunctionDef
    :param is_from_class: The arg who tells if shoud be directly defined as a Method.
    :type is_from_class: bool = False
    :return: A dict containing the statement type and the data listed before.
    :rtype: list[StandardReturn]
    """

    statement: Final[Statement] = Statement.FunctionDef
    name: Final[Token] = node.name
    docstring: Final[Docstring | None] = ast.get_docstring(node)
    decos: Final[list[Decorator]] = [_handle_node(i)[0] for i in node.decorator_list]
    rtype: Final[Annotation | None] = (
        _handle_node(node.returns)[0] if node.returns else None
    )
    code: Final[CodeSnippet] = ast.unparse(node)

    args_str: Final[Args] = __process_function_args(node.args)
    kwargs_str: Final[Kwargs] = __process_function_kwargs(node.args)

    category: Final[FunctionType] = __process_function_type(node, is_from_class)

    contract: FunctionDefContract = FunctionDefContract(
        statement=statement,
        name=name,
        category=category,
        docstring=docstring,
        decorators=decos,
        rtype=rtype,
        args=args_str,
        kwargs=kwargs_str,
        code=code,
    )

    data: StandardReturn = standard_struct()

    data.update(contract._asdict())

    struct.append(data)

    return struct


def _handle_async_function_def(
    struct: list[StandardReturn], node: ast.AsyncFunctionDef
) -> list[StandardReturn]:
    """
    Processes an `ast.AsyncFunctionDef` node and returns its data.

    This function analyzes the components of a func def, mapping the name, decorators,
    arguments (name, type, default value), return type and even the type of function it
    is, which in this case can be only one:
    - Coroutine: An async func, defined with `async def` syntax...

    Example:

    ```python
    import ast

    node: ast.AST = ast.parse('async def foo(*args: Any): pass').body[0]
    updated_struct: list[StandardReturn] = _handle_assign([], node)
    updated_struct
    # Outputs standardized data for async `foo` definition.
    ```

    :param struct: The structure to be updated with statement details.
    :type struct: list[StandardReturn]
    :param node: The AST node representing a func def statement.
    :type node: ast.AsyncFunctionDef
    :return: A dict containing the statement type and the data listed before.
    :rtype: list[StandardReturn]
    """

    statement: Final[Statement] = Statement.AsyncFunctionDef
    name: Final[Token] = node.name
    docstring: Final[Docstring | None] = ast.get_docstring(node)
    decos: Final[list[Decorator]] = [_handle_node(i)[0] for i in node.decorator_list]
    rtype: Final[Annotation | None] = (
        _handle_node(node.returns)[0] if node.returns else None
    )
    code: Final[CodeSnippet] = ast.unparse(node)

    args_str: Final[Args] = __process_function_args(node.args)
    kwargs_str: Final[Kwargs] = __process_function_kwargs(node.args)

    contract: AsyncFunctionDefContract = AsyncFunctionDefContract(
        statement=statement,
        name=name,
        category=FunctionType.Coroutine,
        docstring=docstring,
        decorators=decos,
        rtype=rtype,
        args=args_str,
        kwargs=kwargs_str,
        code=code,
    )

    data: StandardReturn = standard_struct()

    data.update(contract._asdict())

    struct.append(data)

    return struct


def __format_class_kwarg(name: str | None, value: ast.expr) -> str:
    """
    Formats a kwarg from a class definition into a string repr.

    This function converts an AST kwarg into a string, representing it in the format
    `name=value`. If the keyword has no name (e.g., for positional arguments), only the
    value is returned.

    Key concepts:
    - AST Unparsing: Uses `ast.unparse` to convert an AST expression into its
      corresponding Python code as a string.
    - Conditional Formatting: Handles named and unnamed (positional) keyword arguments.

    Example:

    ```python
    import ast

    kwarg: ast.keyword = ast.keyword(arg='debug', value=ast.Constant(value=True))
    formatted: str = __format_class_kwarg(kwarg.arg, kwarg.value)
    formatted
    # "debug = True"
    ```

    :param name: The name of the kwarg (can be `None` for positional arguments).
    :type name: str | None
    :param value: The AST expression representing the value of the keyword argument.
    :type value: ast.expr
    :return: A formatted string representing the keyword argument.
    :rtype: str
    """

    value_str: str = ast.unparse(value)

    if name:
        return f'{name} = {value_str}'

    return value_str


def __process_class_kwargs(keywords: list[ast.keyword]) -> str:
    """
    Processes and formats keyword arguments from a class definition.

    This function takes a list of keyword arguments (from an AST node) and formats
    them into a single, comma-separated string. Each keyword is processed using
    the `__format_class_kwarg` function to ensure consistent repr.

    Key concepts:
    - Keyword Formatting: Converts each kwarg into a string repr
      of the form `key=value`.
    - List Processing: Aggregates and joins all formatted keyword arguments into a
      single string for use in documentation or code generation.

    Example:

    ```python
    import ast

    keywords: list[ast.keyword] = [
        ast.keyword(arg='name', value=ast.Constant(value='MyClass'))
    ]
    formatted: str = __process_class_kwargs(keywords)
    formatted
    # "name='MyClass'"
    ```

    :param keywords: A list of AST keyword arguments.
    :type keywords: list[ast.keyword]
    :return: A comma-separated string of formatted keyword arguments.
    :rtype: str
    """

    formatted_kwargs: list[str] = [
        __format_class_kwarg(kw.arg, kw.value) for kw in keywords
    ]

    return ', '.join(formatted_kwargs)


def _handle_class_def(
    struct: list[StandardReturn], node: ast.ClassDef
) -> list[StandardReturn]:
    """
    Processes an `ast.ClassDef` node and returns its data.

    This function analyzes the components of a class definition, including its name,
    base classes, decorators, and keyword arguments, returning a structured dict with
    the extracted details.

    Key elements of the returned data:
    - name: The name of the class as a string.
    - parents: A list of string reprs for the base classes of the class.
    - decos: A list of string reprs for all decorators applied to the class.
    - kwargs: A list of tuples, in `(name, value)` style.

    Example:

    ```python
    import ast

    node: ast.AST = ast.parse('class Foo: pass').body[0]
    updated_struct: list[StandardReturn] = _handle_class_def([], node)
    updated_struct
    # Outputs standardized data for `Foo` definition.
    ```

    :param struct: The structure to be updated with statement details.
    :type struct: list[StandardReturn]
    :param node: The AST node representing a class definition.
    :type node: ast.ClassDef
    :return: A dict with the statement type, name, base classes, decorators, and kwargs.
    :rtype: list[StandardReturn]
    """

    statement: Final[Statement] = Statement.ClassDef
    name: Final[Token] = node.name
    docstring: Final[Docstring | None] = ast.get_docstring(node)
    inheritance: Final[list[Inheritance]] = [
        _handle_node(i)[0] for i in node.bases if isinstance(i, ast.Name)
    ]
    decos: Final[list[Decorator]] = [_handle_node(i)[0] for i in node.decorator_list]
    kwargs_str: Kwargs = __process_class_kwargs(node.keywords)
    code: Final[CodeSnippet] = ast.unparse(node)

    contract: ClassDefContract = ClassDefContract(
        statement=statement,
        name=name,
        docstring=docstring,
        inheritance=inheritance,
        decorators=decos,
        kwargs=kwargs_str,
        code=code,
    )

    data: StandardReturn = standard_struct()

    data.update(contract._asdict())

    struct.append(data)

    for child in node.body:
        if isinstance(child, ast.FunctionDef):
            function_data: StandardReturn = standard_struct()
            function_data.update(_handle_function_def([], child, is_from_class=True)[0])
            struct.append(function_data)

    return struct


def _handle_assert(
    struct: list[StandardReturn], node: ast.Assert
) -> list[StandardReturn]:
    """
    Processes an `ast.Assert` node and returns its data.

    This function analyzes the components of an assertion, including the expression of
    the test and the optional message, returning a structured dict with the extracted
    details.

    Key elements of the returned data:
    - statement: The type of statement, identified as `Statement.Assert`.
    - test: A repr of the test expression being asserted.
    - msg: A string repr of the optional message, `None` if no message is provided.

    :param struct: The structure to be updated with statement details.
    :type struct: list[StandardReturn]
    :param node: The AST node representing an assertion statement.
    :type node: ast.Assert
    :return: A dict with the statement type, test expression, and optional message.
    :rtype: list[StandardReturn]
    """

    statement: Final[Statement] = Statement.Assert
    test: Final[AssertionTest] = _handle_node(node.test)[0]
    msg: Final[AssertionMessage | None] = (
        _handle_node(node.msg)[0] if node.msg else None
    )
    code: Final[CodeSnippet] = ast.unparse(node)

    contract: AssertContract = AssertContract(
        statement=statement,
        test=test,
        msg=msg,
        code=code,
    )

    data: StandardReturn = standard_struct()

    data.update(contract._asdict())

    struct.append(data)

    return struct


def _mark_methods(node: ast.ClassDef) -> None:
    """
    Marks all functions within a given `ClassDef` node as methods.

    This function iterates over the child nodes of the provided class node, and
    for each method (a `FunctionDef`), it assigns the class type (`ast.ClassDef`)
    to the `parent` attribute of the method node.

    :param node: The class definition node containing methods to be marked.
    :type node: ast.ClassDef
    :return: None
    :rtype: None
    """

    for child_node in ast.iter_child_nodes(node):
        if isinstance(child_node, ast.FunctionDef):
            setattr(child_node, 'parent', ast.ClassDef)


def wrapped_mark_methods_for_testing(node: ast.ClassDef) -> None:
    """
    Just encapsulates `_mark_methods` function, just for unittesting.

    :param node: The class definition node containing methods to be marked.
    :type node: ast.ClassDef
    :return: None
    :rtype: None
    """

    return _mark_methods(node)


def wrapped_handle_std_nodes_for_testing(node: ast.AST) -> list[StandardReturn]:
    """
    Just encapsulates `_handle_std_nodes` function, just for unittesting.

    :param node: The class definition node containing methods to be marked.
    :type node: ast.AST
    :return: An object containing information associated with the node.
    :rtype: list[StandardReturn]
    """

    return _handle_std_nodes(node)
