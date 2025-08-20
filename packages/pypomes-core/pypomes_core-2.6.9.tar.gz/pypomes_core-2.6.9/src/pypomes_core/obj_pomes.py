import inspect
import json
import os
import traceback
from contextlib import suppress
from types import FrameType, TracebackType
from typing import Any


def obj_is_serializable(obj: Any) -> bool:
    """
    Determine if *obj* is serializable.

    :param obj: the reference object
    :return: *True* if serializable, *False* otherwise
    """
    # initialize the return variable
    result: bool = True

    # verify the object
    try:
        json.dumps(obj)
    except (TypeError, OverflowError):
        result = False

    return result


def obj_to_dict(obj: Any,
                omit_private: bool = True) -> dict[str, Any] | list[Any] | Any:
    """
    Convert the generic object *obj* to a *dict*.

    The conversion is done recursively. Attributes for which exceptions are raised on attempt
    to access them are silently omited.

    :param obj: the object to be converted
    :param omit_private: whether to omit private attributes (defaults to *True*)
    :return: the dict obtained from *obj*
    """
    # declare the return variable
    result: dict[str, Any] | list[Any] | Any

    if isinstance(obj, dict):
        result = {str(k): obj_to_dict(obj=v,
                                      omit_private=omit_private) for k, v in obj.items()}
    elif isinstance(obj, list | tuple | set):
        result = [obj_to_dict(obj=item,
                              omit_private=omit_private) for item in obj]
    elif hasattr(obj, "__dict__") or not isinstance(obj, str | int | float | bool | type(None)):
        result = {}
        for attr in dir(obj):
            if not (omit_private and attr.startswith("_")):
                with suppress(Exception):
                    value: Any = getattr(obj, attr)
                    if not callable(value):
                        result[attr] = obj_to_dict(obj=value,
                                                   omit_private=omit_private)
    else:
        result = obj

    return result


def exc_format(exc: Exception,
               exc_info: tuple[type[BaseException], BaseException, TracebackType]) -> str:
    """
    Format the error message resulting from the exception raised in execution time.

    The format to use: <python_module>, <line_number>: <exc_class> - <exc_text>

    :param exc: the exception raised
    :param exc_info: information associated with the exception
    :return: the formatted message
    """
    tback: TracebackType = exc_info[2]
    cls: str = str(exc.__class__)

    # retrieve the execution point where the exception was raised (bottom of the stack)
    tlast: traceback = tback
    while tlast.tb_next:
        tlast = tlast.tb_next

    # retrieve the module name and the line number within the module
    try:
        fname: str = os.path.split(p=tlast.tb_frame.f_code.co_filename)[1]
    except Exception:
        fname: str = "<unknow module>"
    fline: int = tlast.tb_lineno

    return f"{fname}, {fline}, {cls[8:-2]} - {exc}"


def func_get_passed_args(include_defaults: bool = False) -> dict[str, Any]:
    """
    Retrieve the arguments passed to the invoking function, as *key-value* pairs.

    *include_defaults* determines whether to include parameters that were not actually passed,
    but has default values defined.

    :param include_defaults: whether to include parameters with default values that were not actually passed
    :return: a *dict* with the passed parameters as *key-value* pairs
    """
    # get the caller's frame
    frame: FrameType = inspect.currentframe().f_back

    # Get the function object
    func: Any = frame.f_globals[frame.f_code.co_name]

    args_info: inspect.ArgInfo = inspect.getargvalues(frame=frame)
    sig: inspect.Signature = inspect.signature(func)

    bound_args: inspect.BoundArguments
    if include_defaults:
        # bind all arguments, filling in defaults
        bound_args = sig.bind(**args_info.locals)
        bound_args.apply_defaults()
    else:
        # bind only explicitly passed arguments
        bound_args = sig.bind_partial(**args_info.locals)

    return dict(bound_args.arguments)
