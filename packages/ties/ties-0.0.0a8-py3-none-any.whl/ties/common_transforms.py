"""A set of common tie transforms."""

import os
import re


def embed_environ(*args: str) -> str:
    """
    Embed environment variables in files.

    The script will look for substrings of the form ${env:<VARIABLE NAME>}
    and replace them with the appropriate environment variable.
    """
    contents = "".join(args)

    # Define the pattern to find ${env:VARIABLE_NAME}
    # \w+ matches one or more word characters (letters, numbers, underscore)
    pattern = r"\$\{env:(\w+)\}"

    # Define a replacer function that looks up the environment variable
    # m.group(1) will contain the captured variable name (e.g., "HOME")
    # os.environ.get() safely gets the variable, returning '' if not found.
    def replacer(m: re.Match[str]) -> str:
        return os.environ.get(m.group(1), "")

    # Substitute all occurrences of the pattern in the contents
    return re.sub(pattern, replacer, contents)
