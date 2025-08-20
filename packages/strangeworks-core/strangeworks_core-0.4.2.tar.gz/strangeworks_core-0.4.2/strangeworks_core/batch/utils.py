"""utils.py."""

import ast
import base64
import gzip
import inspect
import io
import json
import random
import string
import sys
import tempfile
import zipfile
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional

import dill
import requests

from strangeworks_core.errors.error import StrangeworksError
from strangeworks_core.platform.gql import API, APIInfo, Operation
from strangeworks_core.types.batch import Options
from strangeworks_core.types.func import Func
from strangeworks_core.types.machine import Accelerator, Machine

__supported_submit_operations = {
    APIInfo.SDK: Operation(
        query="""
            mutation batchJobFinalizeCreate(
                $final: FinalizeBatchJobCreateInput!
            ) {
                batchJobFinalizeCreate(
                    input: $final
                ) {
                    batchJobSlug
                }
            }
            """
    ),
}


def submit(
    api: API,
    batch_job_init_create: Operation,
    f: Func,
    machine: Optional[Machine] = None,
    accelerator: Optional[Accelerator] = None,
    options: Optional[Options] = None,
    **kwargs,
) -> str:
    """
    submit a batch job that runs a function.
    This packages the function's source file, requirements file, and arguments.
    It sends a request to platform to use
      the sw-py-3.10 docker image to run the function.

    Parameters
    ----------
    api : API
        API instance.
    batch_job_init_create : Operation
        Operation instance.
    f : Func
        Func instance.
        The function to be executed.
        This should hold the function, the function's arguments,
        the function's keyword arguments, and optionally the function's
        requirements file.
    machine : Optional[Machine], optional
        Machine instance, by default None
    accelerator : Optional[Accelerator], optional
        Accelerator instance, by default None
    options: Optional[Options], optional
        Options instance, by default None
    **kwargs
        Keyword arguments.

    Returns
    -------
    batch_job_slug : str
        Batch job slug.

    Raises
    ------
    StrangeworksError
        Unable to create a batch job for any reason.
    """

    op = __supported_submit_operations.get(api.info, None)
    if not op:
        raise StrangeworksError(f"{api.info} not supported for batch job creation")

    src_file = inspect.getsourcefile(f.func)
    if not src_file:
        func_name = f.func.__name__
        raise StrangeworksError(
            f"Cannot create batch job from function {func_name} without source file"
        )

    with tempfile.NamedTemporaryFile(mode="rb+") as tmp:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
            try:
                usr_exp = open(src_file, "rb")
            except IOError as e:
                raise StrangeworksError("Unable to open source file") from e
            else:
                with usr_exp:
                    with archive.open("user_experiment.py.gz", "w") as gz_file:
                        gzipped_content = gzip.compress(usr_exp.read())
                        gz_file.write(gzipped_content)

            with archive.open("input.pickle", "w") as input_file:
                input = {
                    "entry_point": f.func.__name__,
                    "module_name": f.func.__name__,
                    "args": f.fargs,
                    "kwargs": f.fkwargs,
                }
                i = base64.b64encode(dill.dumps(input))
                input_file.write(i)

            if f.requirements_path:
                try:
                    req_file = open(f.requirements_path, "rb")
                except IOError as e:
                    raise StrangeworksError("Unable to open requirements file") from e
                else:
                    with archive.open("requirements.txt", "w") as r:
                        with req_file:
                            r.write(req_file.read())

        tmp.seek(0)
        p = Path(tmp.name)
        stats = p.stat()
        meta_size = stats.st_size
        init = {
            "container": {
                "ImageURI": "us-central1-docker.pkg.dev/strangeworks/strangeworks-docker/sw-py-3.10:0.0.1",  # noqa E501
            },
            "fileName": "package.zip",
            "contentType": "application/zip",
            "metaFileType": "zip",
            "metaFileSize": meta_size,
        }
        initial_res = api.execute(batch_job_init_create, init=init, **kwargs)
        init_create = initial_res.get("batchJobInitiateCreate", None)
        if not init_create:
            raise StrangeworksError(
                "unable to create batch job: batchJobInitiateCreate missing in response"
            )

        batch_job_slug = init_create.get("batchJobSlug", None)
        signed_url = init_create.get("signedURL", None)

        if not batch_job_slug or not signed_url:
            raise StrangeworksError(
                """
                unable to create batch job:
                batchJobSlug or signedURL missing in response
                """
            )

        res = requests.put(
            signed_url, data=tmp, headers={"Content-Type": "application/zip"}
        )
        res.raise_for_status()

    if not machine:
        machine = Machine()

    if not options:
        options = Options()

    final = {
        "batchJobSlug": batch_job_slug,
        "machine": {
            "Type": machine.type,
            "CPU": machine.cpu,
            "Memory": machine.memory,
        },
        "options": {
            "MaxRetries": options.max_retries,
            "MaxDuration": options.max_duration,
        },
    }
    if accelerator:
        final["machineAccelerator"] = {
            "Type": accelerator.type,
            "Count": accelerator.count,
        }
    res = api.execute(
        op,
        final=final,
        **kwargs,
    )
    final_create = res.get("batchJobFinalizeCreate", None)
    if not final_create:
        raise StrangeworksError(
            "unable to finalize batch job: batchJobFinalizeCreate missing in response"
        )
    batch_job_slug = final_create.get("batchJobSlug", None)
    if not batch_job_slug:
        raise StrangeworksError("unable to finalize batch job: batchJobSlug missing")

    return batch_job_slug


def send_batch_request(
    api: API,
    batch_job_init_create: Operation,
    decorator_name: str,
    func: Func,
    machine: Optional[Machine] = None,
    accelerator: Optional[Accelerator] = None,
    options: Optional[Options] = None,
    include_preamble: bool = False,
    **kwargs,
) -> str:
    """Send batch request.

    Sends an initiate request to the platform to create a batch job.
    Packages up the user program and any requirements
    and stores them where the platform needs them to be.
    Sends a finalize request to the platform to finalize the batch job.



    Parameters
    ----------
    api : API
        API instance.
    batch_job_init_create : Operation
        Operation instance.
    decorator_name : str
        Decorator name.
    func : Func
        Func instance.
    machine : Optional[Machine], optional
        Machine instance, by default None
    accelerator : Optional[Accelerator], optional
        Accelerator instance, by default None
    options: Optional[Options], optional
        Options instance, by default None
    **kwargs
        Keyword arguments.

    Returns
    -------
    batch_job_slug : str
        Batch job slug.

    Raises
    ------
    StrangeworksError
        Unable to create a batch job for any reason.
    """

    operations = {
        APIInfo.SDK: Operation(
            query="""
            mutation batchJobFinalizeCreate(
                $final: FinalizeBatchJobCreateInput!
            ) {
                batchJobFinalizeCreate(
                    input: $final
                ) {
                    batchJobSlug
                }
            }
            """
        ),
        APIInfo.PRODUCT: Operation(
            query="""
            mutation batchJobFinalizeCreate(
                $final: FinalizeBatchJobCreateInput!
                $resource_slug: String!
                $workspace_member_slug: String
            ){
                batchJobFinalizeCreate(
                    input: {
                        finalize: $final
                        resourceSlug: $resource_slug
                        workspaceMemberSlug: $workspace_member_slug
                    }
                ) {
                    batchJobSlug
                }
            }
            """
        ),
    }

    op = operations.get(api.info, None)
    if not op:
        raise StrangeworksError("api.info not supported for batch job creation")

    try:
        program = _get_user_program(decorator_name, func, include_preamble)
    except Exception as e:
        raise StrangeworksError("unable to get user program") from e

    with tempfile.NamedTemporaryFile(mode="rb+") as tmp:
        with zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as archive:
            with archive.open("program.json", "w") as f:
                p = json.dumps(program)
                f.write(p.encode("utf-8"))

            if func.requirements_path:
                try:
                    req_file = open(func.requirements_path, "rb")
                except IOError as e:
                    raise StrangeworksError(message=f"unable to open file: {str(e)}")
                else:
                    with archive.open("requirements.txt", "w") as r:
                        with req_file:
                            r.write(req_file.read())
        tmp.seek(0)
        p = Path(tmp.name)
        stats = p.stat()
        meta_size = stats.st_size
        init = {
            "program": {
                "EntryPoint": func.func.__name__,
                "Language": "python",
                "LanguageVersion": "3.10",
            },
            "fileName": "package.zip",
            "contentType": "application/zip",
            "metaFileType": "zip",
            "metaFileSize": meta_size,
        }

        initial_res = api.execute(batch_job_init_create, init=init, **kwargs)
        init_create = initial_res.get("batchJobInitiateCreate", None)
        if not init_create:
            raise StrangeworksError(
                "unable to create batch job: batchJobInitiateCreate missing in response"
            )

        batch_job_slug = init_create.get("batchJobSlug", None)
        signed_url = init_create.get("signedURL", None)

        if not batch_job_slug or not signed_url:
            raise StrangeworksError(
                """
                unable to create batch job:
                batchJobSlug or signedURL missing in response
                """
            )

        res = requests.put(
            signed_url, data=tmp, headers={"Content-Type": "application/zip"}
        )
        res.raise_for_status()

    if not machine:
        machine = Machine()

    if not options:
        options = Options()

    final = {
        "batchJobSlug": batch_job_slug,
        "machine": {
            "Type": machine.type,
            "CPU": machine.cpu,
            "Memory": machine.memory,
        },
        "options": {
            "MaxRetries": options.max_retries,
            "MaxDuration": options.max_duration,
        },
    }
    if accelerator:
        final["machineAccelerator"] = {
            "Type": accelerator.type,
            "Count": accelerator.count,
        }
    res = api.execute(
        op,
        final=final,
        **kwargs,
    )
    final_create = res.get("batchJobFinalizeCreate", None)
    if not final_create:
        raise StrangeworksError(
            "unable to finalize batch job: batchJobFinalizeCreate missing in response"
        )
    batch_job_slug = final_create.get("batchJobSlug", None)
    if not batch_job_slug:
        raise StrangeworksError("unable to finalize batch job: batchJobSlug missing")

    return batch_job_slug


def _get_user_program(
    decorator_name: str,
    f: Func,
    include_preamble: bool,
) -> dict[str, Any]:
    """Create a dictionary of the user program that the batch job recognizes.

    Parameters
    ----------
    decorator_name: str
        The name of the strangeworks decorator to remove from func.
    f: Func
        The function to create a batch job package for.
    include_preamble: bool
        Whether or not to include the preamble in the source code.

    Returns
    -------
    program: dic[str, Any]
        The user program that defines:
        * the entry point
        * the imports
        * the source code
        * the user defined functions
        * the inputs
        * an optional preamble

    Raises
    ------
    StrangeworksError
        If the source file for the function cannot be found.

    """

    file_path = inspect.getsourcefile(f.func)
    if not file_path:
        raise StrangeworksError("Unable to find source file for function.")

    imports = _get_imports(file_path)
    source = _get_source(f.func, decorator_name)
    preamble_fn_name, preamble = _get_preamble(
        include_preamble, source, inspect.getmodule(f.func)
    )
    inputs = _package_fargs_and_fkwargs(*f.fargs, **f.fkwargs)
    user_defined_helper_fns = _user_defined_functions_in_file(
        f.func.__module__, file_path, source
    )
    entry_point = f.func.__name__

    program = {
        "entry_point": entry_point,
        "imports": base64.b64encode(dill.dumps(imports)).decode(),
        "source": base64.b64encode(dill.dumps(source)).decode(),
        "user_defined_functions": base64.b64encode(
            dill.dumps(user_defined_helper_fns)
        ).decode(),
        "inputs": inputs,
        "custom_requirements": f.requirements_path is not None,
    }

    if preamble_fn_name and preamble:
        program["preamble_fn_name"] = preamble_fn_name
        program["preamble"] = base64.b64encode(dill.dumps(preamble)).decode()

    return program


def _get_imports(file_path: str) -> list[str]:
    """Get a list of the imports in a file.

    Parse imports using ast (https://docs.python.org/3/library/ast.html)
    in order to properly handle most if not all import cases such as:
    ```python
    import module
    import module as m
    from module import name
    from module import name as n
    from module import (
        name1,
        name2,
        name3,
        name4 as n4,
    )
    ```

    Parameters
    ----------
    file_path: str
        The path to the file of the function.

    Returns
    -------
    imports: list[str]
        A list of the imports in the file.
    """
    with open(file_path, "r") as file:
        tree = ast.parse(file.read())

    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(
                [
                    f"import {name.name}"
                    if not name.asname
                    else f"import {name.name} as {name.asname}"
                    for name in node.names
                ]
            )
        elif isinstance(node, ast.ImportFrom):
            module = node.module if node.module else ""
            imports.extend(
                [
                    f"from {module} import {alias.name}"
                    if not alias.asname
                    else f"from {module} import {alias.name} as {alias.asname}"
                    for alias in node.names
                ]
            )
    return imports


def _get_source(f: Callable[..., Any], decorator_name: str) -> str:
    """Get the source code of a function, removing the decorator.

    Parameters
    ----------
    f: Callable[..., Any]
        The function to get the source code of.
    decorator_name: str
        The name of the strangeworks decorator to remove from f.

    Returns
    -------
    source_code: str
        The source code of f with the strangeworks batch job decorator removed.

    """

    def _remove_sw_decorator(
        func_name: str, func_source: str, decorator_name: str
    ) -> str:
        """Remove the strangeworks decorator from a function.

        Parameters
        ----------
        func_name: str
            The name of the function that is going to run as a batch job.
        func_source: str
            The source code of the function that is going to run as a batch job.
        decorator_name: str
            The name of the strangeworks decorator to remove from func_source.

        Returns
        -------
        source_code: str
            The source code of the function
            with the strangeworks batch job decorator removed.
        """
        parsed = ast.parse(func_source)
        for node in ast.iter_child_nodes(parsed):
            if isinstance(node, ast.FunctionDef) and node.name == func_name:
                decorator_index = None
                for index, decorator in enumerate(node.decorator_list):
                    id = None
                    if isinstance(decorator, ast.Call):
                        f = decorator.func
                        if isinstance(f, ast.Name):
                            id = f.id
                        elif isinstance(f, ast.Attribute):
                            id = f.attr
                    elif isinstance(decorator, ast.Name):
                        id = decorator.id

                    if id and id == decorator_name:
                        decorator_index = index
                        break
                if decorator_index is not None:
                    node.decorator_list.pop(decorator_index)

                break
        return ast.unparse(parsed)

    return _remove_sw_decorator(f.__name__, inspect.getsource(f), decorator_name)


def _package_fargs_and_fkwargs(*fargs, **fkwargs) -> dict[str, str]:
    """Package the fargs and fkwargs into a dictionary.

    Parameters
    ----------
    *fargs: Any
        The positional arguments to the function.
    **fkwargs: Any
        The keyword arguments to the function.

    Returns
    -------
    fargs_and_fkwargs: dict[str, str]
        keys: "fargs" and "fkwargs"
        values: The base64 encoded dill pickled values of the arguments.

    """
    return {
        "fargs": base64.b64encode(dill.dumps(fargs)).decode(),
        "fkwargs": {
            key: base64.b64encode(dill.dumps(value)).decode()
            for key, value in fkwargs.items()
        },
    }


def _user_defined_functions_in_file(
    func_module: str, func_src_file_path: str, func_source: str
) -> set[str]:
    """Get the source code of all
    user-defined functions in the same file that func_source lives in.

    Parameters
    ----------
    func_module: str
        The name of the module that func_source lives in.
    func_src_file_path: str
        The path to the file that func_source lives in.
    func_source: str
        The source code of the function to get the user-defined functions for.

    Returns
    -------
    user_defined_functions: set[str]
        The source code of all user-defined functions
        in the same file that func_source lives in.

    """
    members = inspect.getmembers(sys.modules[func_module])
    source_for_members_in_user_file = {
        name: inspect.getsource(obj)
        for name, obj in members
        if inspect.isfunction(obj) and inspect.getsourcefile(obj) == func_src_file_path
    }

    visited = set()
    queue = []
    queue.append(func_source)
    visited.add(func_source)

    while queue:
        fn_source = queue.pop(0)
        tree = ast.parse(fn_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                src_mem = source_for_members_in_user_file.get(node.func.id, None)
                if src_mem and src_mem not in visited:
                    queue.append(src_mem)
                    visited.add(src_mem)

    visited.remove(func_source)
    return visited


def _get_preamble(
    include_preamble: bool, func_source: str, module: Optional[ModuleType]
) -> tuple[Optional[str], Optional[str]]:
    """Get the preamble for the batch job.
    A preamble contains preparatory statements.
    These preparatory statements are meant to be executed before the function.
    They are executed indepenedntly than the function.
    The main use case for a preamble is so that a user of strangeworks python
      sdk does not have to authenticate more than once.
    Here's an example:
    ```python
    import strangeworks as sw

    api_key = "anWorkspaceApiKey"
    sw.authenticate(api_key)

    sw.experiment()
    def an_experiment():
      res = sw.execute_post(...)
      return {"lemon": res["lemon"] * 9, "juice": res["juice"] * 9}

    ```

    The `an_experiment` function is executed in a remote environment.
    The function also uses the strangeworks python sdk to execute a post request.
    For this post request to be succesful the user must authenticate.
    The preamble is used to get
    ast.Assign (https://docs.python.org/3/library/ast.html#ast.Assign)
    and ast.Expr (https://docs.python.org/3/library/ast.html#ast.Expr)
    statements from the module that the function lives in.
    In this particular example,
    the preamble would prepare the remote environment by authenticating the user.
    Thus this eliminates the need
    for the user to write
    `sw.authenticate(api_key)` in the `an_experiment` function again.


    Parameters
    ----------
    include_preamble: bool
        Whether or not to include the preamble in the source code.
    func_source: str
        The source code of the function to get the preamble for.

    Returns
    -------
    preamble: Optional[str]
        The preamble for the batch job.

    """
    if not include_preamble or not module:
        return (None, None)

    module_source = inspect.getsource(module)

    module_ast = ast.parse(module_source)
    preamble_types_supported = {ast.Assign, ast.Expr}

    preamble = io.StringIO()
    sw_id = "".join(
        random.choice(string.ascii_uppercase + string.digits) for _ in range(9)
    )
    preamble_fn_name = f"sw_preamble_{sw_id}"
    preamble.write(f"def {preamble_fn_name}():\n")

    stmts = []
    for node in module_ast.body:  # focus on the body of the module
        if isinstance(node, tuple(preamble_types_supported)):
            unparsed = ast.unparse(node)
            if unparsed not in func_source:
                # add '\t' to indent the statement inside the function
                unparsed = "\t" + unparsed.replace("\n", "\n\t")
                stmts.append(unparsed)

    if len(stmts) != 0:
        preamble.write("\n".join(stmts))
    else:
        preamble.write("\tpass\n")

    preamble.write("\n")
    program = preamble.getvalue()
    preamble.close()
    return (preamble_fn_name, program)
