import functools
import warnings
from enum import Enum

WARNING_PREFIX = "\n\n    Warning:\n            "

MULTIPLE_EXPERIMENTAL_WARNING_MESSAGE = (
    "Multiple features are experimental and may behave unexpectedly:\n\n            * "
)
MULTIPLE_EXPERIMENTAL_WARNING_JOINER = "\n            * "


def _documentation_function_warning_decorator(
    func_or_message, default_message, warning_category
):
    """A general-purpose decorator for issuing function warnings. This function is
        designed to be used within other decorators to add warning functionality.

    Args:
        func_or_message (:obj:`str` :obj:`Nothing`): If a string is given, it will be
            used as a warning message. Else if nothing is given to the decorator
            (i.e. `@deprecated`), default_message will be used.
        default_message (str): Default warning message to be used if no custom message
            is provided.
        warning_category (class): The category of warning to be used.
            This should be a class derived from the Warning class,
            such as DeprecationWarning, FutureWarning, etc.

    """

    def _get_wrapper(func, warning_message):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            warnings.warn(warning_message, warning_category, stacklevel=2)
            return func(*args, **kwargs)

        doc_start, doc_separator, doc_end = func.__doc__.partition("\n\n")
        wrapper.__doc__ = (
            doc_start + WARNING_PREFIX + warning_message + doc_separator + doc_end
        )
        return wrapper

    if callable(func_or_message):  # No parameter is given
        func = func_or_message
        return _get_wrapper(func, default_message)
    else:  # A message is given
        warning_message = func_or_message
        return lambda func: _get_wrapper(func, warning_message)


class EXPERIMENTAL_VALUES(Enum):
    """Enumeration for experimental_parameters special values."""

    ALL = "ALL"
    STRING_CONTAINING = "STRING_CONTAINING"


def experimental(func_or_message):
    """Decorator to mark a function as experimental.

    Args:
        func_or_message (:obj:`str` :obj:`Nothing`): If a string is given, it will be
            used as a warning message. Else if nothing is given to the decorator
            (i.e. `@experimental`), a default warning message will be used.

    """
    DEFAULT_EXPERIMENTAL_WARNING_MESSAGE = (
        "This feature is experimental and may behave unexpectedly. "
        "It may also be removed or changed in the future."
    )
    return _documentation_function_warning_decorator(
        func_or_message, DEFAULT_EXPERIMENTAL_WARNING_MESSAGE, FutureWarning
    )


def experimental_parameters(parameters):
    """Decorator to mark only some parameters of a function as experimental.

    Args:
        parameters (dict): A dictionary of parameters to be marked as
            experimental. The keys are the names of the parameters and the
            values are dictionaries with the following structure:
            {
                "value1": {"message": "message1"},
                "value2": {"message": "message2"},
                EXPERIMENTAL_VALUES.ALL: {"message": "message3"},
                EXPERIMENTAL_VALUES.STRING_CONTAINING: {
                    message: "message4",
                    substring: ["substring1", "substring2"],
                }
            }
            where the keys are the values of the parameters and the values are
            the messages to be displayed when the parameter is used.
            You can also use the `EXPERIMENTAL_VALUES.ALL` key to mark all the
            values of a parameter as experimental or
            `EXPERIMENTAL_VALUES.STRING_CONTAINING` to mark all the values of a
            parameter containing a string as experimental. In the latter case,
            you need to provide a `message` and a `substring` key in the
            dictionary value. The `message` will be displayed when the
            parameter is used with a value containing one of the strings in the
            `substring` list.

    """

    def actual_decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for key, value in kwargs.items():
                if key in parameters:
                    if value in parameters[key]:
                        warnings.warn(
                            parameters[key][value]["message"],
                            FutureWarning,
                            stacklevel=2,
                        )
                    elif EXPERIMENTAL_VALUES.ALL in parameters[key]:
                        warnings.warn(
                            parameters[key][EXPERIMENTAL_VALUES.ALL]["message"],
                            FutureWarning,
                            stacklevel=2,
                        )
                    elif EXPERIMENTAL_VALUES.STRING_CONTAINING in parameters[key]:
                        if any(
                            substring in value
                            for substring in parameters[key][
                                EXPERIMENTAL_VALUES.STRING_CONTAINING
                            ]["substring"]
                        ):
                            warnings.warn(
                                parameters[key][EXPERIMENTAL_VALUES.STRING_CONTAINING][
                                    "message"
                                ],
                                FutureWarning,
                                stacklevel=2,
                            )
            return func(*args, **kwargs)

        message_list = [
            value["message"] for key in parameters for value in parameters[key].values()
        ]
        if len(message_list) > 1:
            warning_message = f"{MULTIPLE_EXPERIMENTAL_WARNING_MESSAGE}\
{MULTIPLE_EXPERIMENTAL_WARNING_JOINER.join(message_list)}"
        else:
            warning_message = message_list[0]
        doc_start, doc_separator, doc_end = func.__doc__.partition("\n\n")
        wrapper.__doc__ = (
            f"{doc_start}{WARNING_PREFIX}{warning_message}{doc_separator}{doc_end}"
        )
        return wrapper

    return actual_decorator


def deprecated(func_or_message):
    """Decorator to mark a function as deprecated.

    Args:
        func_or_message (:obj:`str` :obj:`Nothing`): If a string is given, it will be
            used as a warning message. Else if nothing is given to the decorator
            (i.e. `@deprecated`), a default deprecation warning message will be used.

    """
    DEFAULT_DEPRECATION_WARNING_MESSAGE = (
        "This function is deprecated and its usage is not supported."
    )

    return _documentation_function_warning_decorator(
        func_or_message, DEFAULT_DEPRECATION_WARNING_MESSAGE, DeprecationWarning
    )
