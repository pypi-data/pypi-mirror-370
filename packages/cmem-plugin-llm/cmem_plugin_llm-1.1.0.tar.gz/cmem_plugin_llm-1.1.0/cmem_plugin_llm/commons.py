"""LLM Commons"""

import re
from typing import TYPE_CHECKING, Any, ClassVar

from cmem_plugin_base.dataintegration.context import (
    PluginContext,
)
from cmem_plugin_base.dataintegration.description import PluginParameter
from cmem_plugin_base.dataintegration.types import Autocompletion, StringParameterType
from jinja2 import Environment, meta

if TYPE_CHECKING:
    from jinja2.nodes import Template
from openai import AuthenticationError, OpenAI

JINJA_PATTERN = r"{{\s*([a-zA-Z_][a-zA-Z0-9_]*(?:\.[a-zA-Z_][a-zA-Z0-9_]*)*)\s*}}"
ANTHROPIC_BASE_URL = "https://api.anthropic.com/v1/"


def extract_variables_from_template(template_string: str) -> tuple[set[str], list[str]]:
    """Extract variables from a Jinja template.

    Args:
        template_string: The string of the Jinja template.

    Returns:
        A tuple of a set and a list:
        - Undeclared variables (from meta.find_undeclared_variables) as set.
        - Explicit variables with regex pattern as list.

    """
    # create Jinja environment
    env = Environment(autoescape=True)
    # parse the template
    parsed_content: Template = env.parse(template_string)
    # find undeclared variables
    undeclared_vars: set[str] = meta.find_undeclared_variables(parsed_content)

    # find explicit variables with regex pattern
    explicit_vars: list[str] = re.findall(JINJA_PATTERN, template_string)

    return undeclared_vars, explicit_vars


class SamePathError(ValueError):
    """Same Path Exception"""

    def __init__(self, path: str):
        super().__init__(f"Path '{path}' can not be input AND output path.")


def input_paths_to_list(paths: str) -> list[str]:
    """Convert a comma-separated list of strings to a python list of strings."""
    return [] if paths == "" else [_.strip() for _ in paths.split(",")]


class OpenAPIModel(StringParameterType):
    """OpenAPI Model Type"""

    autocompletion_depends_on_parameters: ClassVar[list[str]] = ["base_url", "api_key"]

    # auto complete for values
    allow_only_autocompleted_values: bool = False
    # auto complete for labels
    autocomplete_value_with_labels: bool = True

    def autocomplete(
        self,
        query_terms: list[str],
        depend_on_parameter_values: list[Any],
        context: PluginContext,
    ) -> list[Autocompletion]:
        """Return all results that match ALL provided query terms."""
        _ = context
        url = depend_on_parameter_values[0]
        api_key = depend_on_parameter_values[1]
        api_key = api_key if isinstance(api_key, str) else api_key.decrypt()
        result = []
        try:
            api = OpenAI(api_key=api_key, base_url=url)
            models = api.models.list()
            filtered_models = set()
            if query_terms:
                for term in query_terms:
                    for model in models:
                        if term in model.id:
                            filtered_models.add(model.id)
            else:
                filtered_models = {_.id for _ in models}
            result = [Autocompletion(value=f"{_}", label=f"{_}") for _ in filtered_models]
        except AuthenticationError as error:
            if url == ANTHROPIC_BASE_URL:
                result = []
            else:
                raise ValueError(
                    "Failed to authenticate with OpenAI API, Please check URL and API key."
                ) from error

        result.sort(key=lambda x: x.label)
        return result


def parameter_link(parameter: PluginParameter, text: str = "") -> str:
    """Return a parameter Markdown link"""
    if text == "":
        advanced_note = " - Advanced Parameter" if parameter.advanced else ""
        text = f"{parameter.label} {advanced_note}"
    return f'<a id="parameter_doc_{parameter.name}">{text}</a>'
