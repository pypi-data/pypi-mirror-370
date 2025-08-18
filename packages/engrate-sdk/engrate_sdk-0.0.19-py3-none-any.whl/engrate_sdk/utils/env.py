"""Environment variable parsing, validation, and logging utilities for the engrate_sdk.

This module defines EnvVarSpec for environment variable specification,
custom exceptions for unset, parse, and validation errors, and functions
to parse and validate environment variables with logging support.
"""

import os
from typing import Any, Callable

import pydantic
from pydantic import (
    BaseModel,
    create_model,
    validate_call,
)

from engrate_sdk.types.exceptions import ParseError, UnsetError, ValidationError
from engrate_sdk.utils import log

#### Types ####


class EnvVarSpec(BaseModel):
    """Specification for an environment variable.

    Attributes:
    ----------
    id : str
        The environment variable name.
    type : Any
        The expected type of the variable.
    default : str, optional
        The default value if the variable is not set.
    parse : Callable[[str], Any], optional
        A function to parse the variable's value.
    is_optional : bool
        Whether the variable is optional.
    is_secret : bool
        Whether the variable contains sensitive information.
    """

    id: str
    type: Any = (str, ...)
    default: str | None = None
    parse: Callable[[str], Any] | None = None
    is_optional: bool = False
    is_secret: bool = False


#### State ####

_is_validated: bool = False

#### API ####


def check(label: str, value: Any, t: Any) -> BaseModel:
    """Validate a value against a given type using a dynamically created Pydantic model.

    Parameters
    ----------
    label : str
        The label or name for the model.
    value : Any
        The value to validate.
    t : Any
        The expected type for the value.

    Returns:
    -------
    BaseModel
        An instance of the dynamically created model with the validated value.

    Raises:
    ------
    pydantic.ValidationError
        If the value does not conform to the expected type.
    """
    m = create_model(label, x=t)
    result = m(**{"x": value})
    return result


@validate_call
def parse(var: EnvVarSpec):
    """Parse and validate an environment variable according to its specification.

    Parameters
    ----------
    var : EnvVarSpec
        The specification for the environment variable to parse.

    Returns:
    -------
    Any
        The parsed and validated value of the environment variable.

    Raises:
    ------
    UnsetError
        If the required environment variable is unset.
    ParseError
        If parsing the environment variable fails.
    ValidationError
        If validation of the environment variable fails.
    """
    value = os.environ.get(var.id, var.default)
    if value is not None:
        if parse := var.parse:
            try:
                value = parse(value)
            except Exception as e:
                raise ParseError(f"Failed to parse {var.id}: {e!s}", value=value) from e
        try:
            check(var.id, value, var.type)
        except pydantic.ValidationError as e:
            raise ValidationError(
                f"Failed to validate {var.id}: {e!s}", value=value
            ) from e
        return value
    elif var.is_optional:
        return None
    elif var.default:
        return var.default
    else:
        raise UnsetError(f"{var.id} is unset")


def validate(env_vars: list[EnvVarSpec], should_log: bool = False) -> bool:
    """Validate and log the status of a list of environment variables.

    Parameters
    ----------
    env_vars : list[EnvVarSpec]
        List of environment variable specifications to validate.

    Returns:
    -------
    bool
        True if all environment variables are valid, False otherwise.
    """
    logger = None
    if should_log:
        from engrate_sdk.utils.log import get_logger

        logger = get_logger(__name__)
    ok = True
    for var in env_vars:
        try:
            value = parse(var)
            if logger:
                logger.info(
                    "Env var %s is set to %s",
                    log.blue(var.id),
                    log.cyan("<REDACTED>") if var.is_secret else value,
                )
        except UnsetError:
            if logger:
                logger.error(f"Env var {log.blue(var.id)} is {log.red('unset')}")
            ok = False
        except ParseError as e:
            if logger:
                logger.error(
                    "Env var %s (set to %s) failed to parse:\n%s",
                    log.blue(var.id),
                    log.cyan("<REDACTED>") if var.is_secret else e,
                    log.red(str(e)),
                )
            ok = False
        except ValidationError as e:
            if logger:
                logger.error(
                    "Env var %s (set to %s) is invalid:\n%s",
                    log.blue(var.id),
                    log.cyan("<REDACTED>") if var.is_secret else e,
                    log.red(str(e)),
                )
            ok = False
    return ok
