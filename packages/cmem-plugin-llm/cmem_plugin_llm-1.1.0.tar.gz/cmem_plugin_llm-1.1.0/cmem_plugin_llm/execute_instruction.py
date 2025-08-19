"""Execute Instructions Plugin"""

import json
from collections.abc import Generator, Sequence
from enum import Enum
from typing import Any

from cmem_plugin_base.dataintegration.context import (
    ExecutionContext,
    ExecutionReport,
)
from cmem_plugin_base.dataintegration.description import Icon, Plugin, PluginParameter
from cmem_plugin_base.dataintegration.entity import (
    Entities,
    Entity,
    EntityPath,
    EntitySchema,
)
from cmem_plugin_base.dataintegration.parameter.code import JinjaCode, JsonCode, PythonCode
from cmem_plugin_base.dataintegration.parameter.password import Password, PasswordParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import (
    FixedNumberOfInputs,
    FixedSchemaPort,
    FlexibleSchemaPort,
    Port,
)
from cmem_plugin_base.dataintegration.types import EnumParameterType
from jinja2 import Template, UndefinedError
from openai import NotGiven, OpenAI
from pydantic import BaseModel

from cmem_plugin_llm.commons import (
    OpenAPIModel,
    SamePathError,
    extract_variables_from_template,
    parameter_link,
)

MESSAGES_TEMPLATE_EXAMPLE = JsonCode("""[
    {
        "role": "developer",
        "content": "You are a helpful assistant."
    },
    {
        "role": "user",
        "content": "{{ instruction_prompt }}"
    }
]""")


PYDANTIC_SCHEMA_EXAMPLE = PythonCode("""from pydantic import BaseModel

class StructuredOutput(BaseModel):
    title: str
    abstract: str
    keywords: list[str]
""")


class OutputFormat(Enum):
    """The output format"""

    TEXT = 1
    STRUCTURED_OUTPUT = 2
    JSON_MODE = 3


class Params:
    """Plugin parameters"""

    base_url: PluginParameter = PluginParameter(
        name="base_url",
        label="Base URL",
        description="The base URL of the OpenAI compatible API (without endpoint path).",
        default_value="https://api.openai.com/v1",
    )
    api_key = PluginParameter(
        name="api_key",
        label="API key",
        param_type=PasswordParameterType(),
        description="An optional OpenAI API key.",
    )
    model = PluginParameter(
        name="model",
        label="Instruct Model",
        description="The instruct model to use (e.g., gpt-4o). "
        "When using Anthropic API, no model autocompletion is available! "
        "Just create a custom entry with a model name from [Anthropics model overview](https://docs.anthropic.com/en/docs/about-claude/models/overview).",
        default_value="gpt-4o-mini",
        param_type=OpenAPIModel(),
    )
    instruct_prompt_template = PluginParameter(
        name="instruct_prompt_template",
        label="Instruction Prompt Template",
        description="The instruction prompt template.",
        default_value=JinjaCode("""Write a paragraph about this entity: {{ entity }}"""),
    )
    temperature = PluginParameter(
        name="temperature",
        label="Temperature (between 0 and 2)",
        description="Higher values like 0.8 will make the output more random,"
        "while lower values like 0.2 will make it more focused and deterministic.",
        default_value=1.0,
        advanced=True,
    )
    timeout = PluginParameter(
        name="timeout",
        label="Timeout for a single API call",
        description="The timeout of a single request in seconds.",
        advanced=True,
        default_value=300,
    )
    instruction_output_path = PluginParameter(
        name="instruction_output_path",
        label="Instruction Output Path",
        description="The entity path where the instruction result will be provided.",
        advanced=True,
        default_value="_instruction_output",
    )
    messages_template = PluginParameter(
        name="messages_template",
        label="Messages Template",
        description="""A list of messages comprising the conversation compatible with OpenAI
        chat completion API message object.""",
        advanced=True,
        default_value=MESSAGES_TEMPLATE_EXAMPLE,
    )
    consume_all_entities = PluginParameter(
        name="consume_all_entities",
        label="Consume all entities from additional input ports",
        description="""If true, all entities from additional input ports will be consumed.
        Otherwise, only the first entity of the additional ports will be used.""",
        advanced=True,
        default_value=False,
    )
    output_format = PluginParameter(
        name="output_format",
        label="Output Format",
        description="Specifying the format that the model must output.",
        param_type=EnumParameterType(enum_type=OutputFormat),
        default_value=OutputFormat.TEXT,
        advanced=True,
    )
    pydantic_schema = PluginParameter(
        name="pydantic_schema",
        label="Pydantic Schema definition the model is using in the response.",
        description="""The Pydantic schema definition with a mandatory class named
        `StructuredOutput(BaseModel)`.""",
        default_value=PYDANTIC_SCHEMA_EXAMPLE,
        advanced=True,
    )

    def as_list(self) -> list[PluginParameter]:
        """Provide all parameters as list"""
        return [
            getattr(self, attr)
            for attr in dir(self)
            if not callable(getattr(self, attr)) and not attr.startswith("__")
        ]


@Plugin(
    label="Execute Instructions",
    plugin_id="cmem_plugin_llm-ExecuteInstructions",
    icon=Icon(package=__package__, file_name="execute_instruction.svg"),
    parameters=Params().as_list(),
    description="Send instructions (prompt) to an LLM and process the result.",
    documentation=f"""
## Introduction

This plugin allows to execute an LLM instruction over a given list of entities.

After being processed, each entity receives one additional path (`_instruction_output`).
This path contains the output of the executed instruction over the entity.

## Parameters

### {parameter_link(Params.base_url)}

- {Params.base_url.description}
- Default: `{Params.base_url.default_value}`

### {parameter_link(Params.api_key)}

- {Params.api_key.description}
- Default: blank

### {parameter_link(Params.model)}

- {Params.model.description}
- Example: `{Params.model.default_value}`

### {parameter_link(Params.instruct_prompt_template)}

- {Params.instruct_prompt_template.description} Please have look at
  [Text generation and prompting](https://platform.openai.com/docs/guides/text?api-mode=chat)
  to learn how to prompt a model to generate text.
- You can add Jinja placeholder to the template text, which will be replaced with data from
  incoming entities:
    - A placeholder such as `{{{{ variable }}}}` will be replaced with the whole incoming entity
      as a JSON string.
    - A placeholder which includes a path (`{{{{ variable.name }}}}`) will be replaced with the
      `name` property of an incoming entity.
- If you use Jinja placeholders in the template text, input and output ports of this task are
  configured as follows:
    - For each different placeholder object, an additional input port is added to the task.
    - If you do not insert any placeholders, there will be no input ports.
    - Variables are sorted alphabetically, so `{{{{ variable_a }}}}` will be replaced with entity
      data from the first input port, while `{{{{ variable_b }}}}` will be replaced with entity
      data from the second input port.
    - During execution, the task iterates over the entities from the first input port.
    - Entities from all other input ports will be consumed when the execution starts. Then, in
      each iteration, their data will inserted to the prompt `{{{{ variable }}}}` accordingly.
    - You can configure how those additional input ports will be consumed with the parameter
      {parameter_link(Params.consume_all_entities, Params.consume_all_entities.name)}.
    - It is recommended to only use known entity paths from the connected input tasks, such as
      `{{{{ variable.path }}}}`, so the ports can be configured with a FixedSchema.
      This avoids the need for additional transformation tasks on the output port.
- Your instruct prompt template is inserted as a user message in
  the {parameter_link(Params.messages_template, Params.messages_template.name)}.
- Default template:
``` jinja2
{Params.instruct_prompt_template.default_value!s}
```

<details>
<summary>Advanced Parameter</summary>

### {parameter_link(Params.temperature)}

- {Params.temperature.description}
- Default: `{Params.temperature.default_value}`

### {parameter_link(Params.timeout)}

- {Params.timeout.description}
- Default: `{Params.timeout.default_value}`

### {parameter_link(Params.instruction_output_path)}

- {Params.instruction_output_path.description}
- Default: `{Params.instruction_output_path.default_value}`

### {parameter_link(Params.messages_template)}

- {Params.messages_template.description}
- Have look at [Message roles and instruction following](https://platform.openai.com/docs/guides/text#message-roles-and-instruction-following)
  to learn about different levels of priority to messages with different roles.
- Default messages template:
``` json
{MESSAGES_TEMPLATE_EXAMPLE}
```

### {parameter_link(Params.consume_all_entities)}

- {Params.consume_all_entities.description}
- Be aware that all entities are loaded in memory.
- Default: `{Params.consume_all_entities.default_value}`

### {parameter_link(Params.output_format)}

- {Params.output_format.description}
- Possible values:
    - TEXT: Standard text output.
    - STRUCTURED_OUTPUT: Structured output following a given schema. Add your schema as Pydantic
      model here: {parameter_link(Params.pydantic_schema, Params.pydantic_schema.name)}
    - JSON_MODE: JSON mode is a more basic version of the Structured Outputs feature.
      While JSON mode ensures that model output is valid JSON, Structured Outputs
      reliably matches the model's output to the schema you specify. If you want to request
      a specified structure, you can add it to
      {parameter_link(Params.instruct_prompt_template, Params.instruct_prompt_template.name)}
- Default: `{Params.output_format.default_value}`

### {parameter_link(Params.pydantic_schema)}

- {Params.pydantic_schema.description}
- This field is only used when {parameter_link(Params.output_format, Params.output_format.name)}
  is set to `STRUCTURED_OUTPUT`.
- A schema may have up to 100 object properties total, with up to 5 levels of nesting.
- The total string length of all property names, definition names, enum values,
  and const values cannot exceed 15,000 characters.
- Default:
``` python
{PYDANTIC_SCHEMA_EXAMPLE}
```
</details>
""",  # noqa: S608
)
class ExecuteInstruction(WorkflowPlugin):
    """Execute Instructions from OpenAI completion API endpoint over entities"""

    execution_context: ExecutionContext
    instruction_output_path: str
    execution_report: ExecutionReport
    messages_template: str
    instruct_prompt_template: str
    client: OpenAI
    model: str
    output_format: OutputFormat
    pydantic_schema: str

    def __init__(  # noqa: PLR0913
        self,
        base_url: str,
        api_key: Password | str = "",
        model: str = Params.model.default_value,
        temperature: float = Params.temperature.default_value,
        timeout: float = Params.timeout.default_value,
        instruction_output_path: str = Params.instruction_output_path.default_value,
        messages_template: JsonCode = MESSAGES_TEMPLATE_EXAMPLE,
        instruct_prompt_template: JinjaCode = Params.instruct_prompt_template.default_value,
        consume_all_entities: bool = Params.consume_all_entities.default_value,
        output_format: OutputFormat = Params.output_format.default_value,
        pydantic_schema: PythonCode = Params.pydantic_schema.default_value,
    ) -> None:
        self.base_url = base_url
        self.api_key = api_key if isinstance(api_key, str) else api_key.decrypt()
        if self.api_key == "":
            self.api_key = "dummy-key"
        self.temperature = temperature
        self.timeout = timeout
        self.client = OpenAI(base_url=self.base_url, api_key=self.api_key, timeout=self.timeout)
        self.instruction_output_path = instruction_output_path
        self.messages_template = str(messages_template)
        self.instruct_prompt_template = str(instruct_prompt_template)
        self.consume_all_entities = consume_all_entities
        self.model = model
        self.output_format = output_format
        self.pydantic_schema = str(pydantic_schema)
        self.execution_report = ExecutionReport()
        self.execution_report.operation = "executing"
        self.execution_report.operation_desc = "instructions executed"
        self.undeclared_template_variables, self.explicit_template_variables = (
            extract_variables_from_template(self.instruct_prompt_template)
        )
        self.sorted_template_variables = self._get_sorted_template_variables()
        self._setup_ports()

    def _get_sorted_template_variables(self) -> dict[str, list[str]]:
        """Get all variables from template as sorted dict"""
        variables: dict[str, list[str]] = {}
        for var in self.undeclared_template_variables:
            variables[var] = []
            for explicit_var in self.explicit_template_variables:
                if explicit_var.startswith(f"{var}."):
                    variables[var].append(explicit_var[explicit_var.find(".") + 1 :])
        return {key: variables[key] for key in sorted(variables)}

    def _setup_ports(self) -> None:
        """Configure input and output ports depending on the configuration"""
        instruct_output_path = EntityPath(path=self.instruction_output_path)
        if not self.undeclared_template_variables:
            # no input data used, so input port closed and output port minimal schema
            self.input_ports = FixedNumberOfInputs([])
            output_schema = EntitySchema(type_uri="entity", paths=[instruct_output_path])
            self.output_port = FixedSchemaPort(schema=output_schema)
        else:
            # derive input ports from template variables
            _input_ports: list[Port] = []
            for port_name, paths in self.sorted_template_variables.items():
                if paths:
                    if port_name in self.explicit_template_variables:
                        # if port name is explicitly named in template, we use flexible schema port
                        _input_ports.append(FlexibleSchemaPort())
                        continue
                    # if only paths for a port are given in template, we use fixed schema port
                    _paths = [EntityPath(path=path) for path in paths]
                    input_schema = EntitySchema(type_uri=port_name, paths=_paths)
                    _input_ports.append(FixedSchemaPort(schema=input_schema))
                else:
                    # if no paths are named in schema, we use flexible schema port
                    _input_ports.append(FlexibleSchemaPort())

            # always use fixed number of input ports based on the number of undeclared vars
            self.input_ports = FixedNumberOfInputs(_input_ports)

            if isinstance(_input_ports[0], FixedSchemaPort):
                # if first input port uses a fixed schema, we use the same schema for the output
                # port (together with the llm output as instruct_output_path)
                output_paths = []
                first_input_paths = next(iter(self.sorted_template_variables.values()))
                if first_input_paths:
                    output_paths = [EntityPath(path=path) for path in first_input_paths]
                output_paths.append(instruct_output_path)
                output_schema = EntitySchema(type_uri="entity", paths=output_paths)
                self.output_port = FixedSchemaPort(schema=output_schema)
            else:
                # if first input uses a flexible schema, the output schema is also flexible
                self.output_port = FlexibleSchemaPort()

    def _cancel_workflow(self) -> bool:
        """Cancel workflow"""
        try:
            if self.execution_context.workflow.status() == "Canceling":
                self.log.info("End task (Cancelled Workflow).")
                return True
        except AttributeError:
            pass
        return False

    def _instruct_report_update(self, n: int) -> None:
        """Update report"""
        if hasattr(self.execution_context, "report"):
            self.execution_report.entity_count += n
            self.execution_context.report.update(self.execution_report)

    @staticmethod
    def _entity_to_dict(paths: Sequence[EntityPath], entity: Entity) -> dict[str, list[str]]:
        """Create a dict representation of an entity"""
        entity_dic: dict[str, list[str]] = {}
        for key, value in zip(paths, entity.values, strict=False):
            entity_dic[key.path] = list(value)
        return entity_dic

    @staticmethod
    def _entities_to_dict(
        paths: Sequence[EntityPath], entities: list[Entity]
    ) -> dict[str, list[str]]:
        """Create a dict representation of a list of entities"""
        entity_dic: dict[str, list[str]] = {}
        for entity in entities:
            for key, value in zip(paths, entity.values, strict=False):
                entity_dic.setdefault(key.path, []).append(" ".join(value))
        return entity_dic

    @staticmethod
    def _render_messages_template(template: str, instruction_prompt: str) -> str:
        """Fill jinja template with string"""
        if "instruction_prompt" not in template:
            raise KeyError("instruction_prompt key not found in template")
        try:
            return Template(template).render(instruction_prompt=instruction_prompt)
        except UndefinedError as error:
            raise KeyError("Could not render jinja template") from error

    @staticmethod
    def _fill_jinja_template(template: str, mapping: dict[str, dict[str, list[str]]]) -> str:
        """Fill jinja template"""
        try:
            return Template(template).render(mapping)
        except UndefinedError as error:
            raise KeyError("Could not render jinja template") from error

    def validate_template_mapping(self, mapping: dict[str, dict[str, list[str]]]) -> None:
        """Validate template mapping"""
        for base_var in self.undeclared_template_variables:
            if base_var not in mapping:
                raise KeyError(f"Variable {base_var} has no mapping")
            for sub_var in self.explicit_template_variables:
                if (
                    sub_var.startswith(f"{base_var}.")
                    and sub_var.split(".")[1] not in mapping[base_var]
                ):
                    raise KeyError(f"Variable {sub_var} has no mapping")

    def _update_developer_message(self, messages: dict) -> None:
        """Update developer message"""
        messages[0]["content"] += "\nReturn as JSON"

    def _process_entities(
        self, entities: Entities, mapping: dict[str, dict[str, list[str]]]
    ) -> Generator[Entity]:
        """Process the entities, yielding new entity objects"""
        entity: Entity
        self._instruct_report_update(0)
        for entity in entities.entities:
            entity_dict = self._entity_to_dict(entities.schema.paths, entity)
            instruct: str = self.instruct_prompt_template
            if self.undeclared_template_variables:
                mapping[next(iter(self.sorted_template_variables.keys()))] = entity_dict
                self.validate_template_mapping(mapping)
                instruct = self._fill_jinja_template(self.instruct_prompt_template, mapping)
            try:
                messages = json.loads(self.messages_template)
            except json.decoder.JSONDecodeError as error:
                raise ValueError("Could not decode messages object") from error
            user_message = messages[1]["content"]
            user_message_rendered: str = self._render_messages_template(user_message, instruct)
            messages[1]["content"] = user_message_rendered
            # create completion based on output format
            match self.output_format.name:
                case OutputFormat.TEXT.name:
                    completion = self.client.chat.completions.create(
                        model=self.model, messages=messages, temperature=self.temperature
                    )
                    entity_dict[self.instruction_output_path] = [
                        completion.choices[0].message.content or ""
                    ]
                case OutputFormat.JSON_MODE.name:
                    self._update_developer_message(messages)
                    completion = self.client.chat.completions.create(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        response_format={"type": "json_object"},  # type: ignore[call-overload]
                    )
                    entity_dict[self.instruction_output_path] = [
                        completion.choices[0].message.content or ""
                    ]
                case OutputFormat.STRUCTURED_OUTPUT.name:
                    namespace: dict[str, Any] = {}
                    exec(self.pydantic_schema, namespace)  # noqa: S102
                    pydantic_classes = {
                        name: cls
                        for name, cls in namespace.items()
                        if isinstance(cls, type)
                        and issubclass(cls, namespace.get("BaseModel", BaseModel))
                        and cls is not namespace["BaseModel"]
                    }
                    structured_output_cls = pydantic_classes.get("StructuredOutput")
                    response_format = (
                        structured_output_cls if structured_output_cls is not None else NotGiven
                    )
                    completion = self.client.beta.chat.completions.parse(
                        model=self.model,
                        messages=messages,
                        temperature=self.temperature,
                        response_format=response_format,
                    )
                    structured_output = completion.choices[0].message.parsed
                    if structured_output is not None:
                        entity_dict[self.instruction_output_path] = [
                            structured_output.model_dump_json()
                        ]
                case _:
                    raise ValueError(f"Unknown output format: {self.output_format}")
            values = list(entity_dict.values())
            self._instruct_report_update(1)
            if self._cancel_workflow():
                break
            yield Entity(uri=entity.uri, values=values)

    def _consume_additional_inputs(
        self, inputs: Sequence[Entities]
    ) -> dict[str, dict[str, list[str]]]:
        """Consume additional inputs and create a mapping for template keys and entities."""
        mapping = {}
        input_keys = list(self.sorted_template_variables.keys())
        if len(inputs) > 1:
            for index, _input in enumerate(inputs[1:]):
                if self.consume_all_entities:
                    mapping[input_keys[index + 1]] = self._entities_to_dict(
                        _input.schema.paths, list(_input.entities)
                    )
                else:
                    mapping[input_keys[index + 1]] = self._entity_to_dict(
                        _input.schema.paths, next(_input.entities)
                    )
        return mapping

    def _generate_output_schema(self, input_schema: EntitySchema) -> EntitySchema:
        """Get output schema"""
        paths = list(input_schema.paths).copy()
        paths.append(EntityPath(self.instruction_output_path))
        return EntitySchema(type_uri=input_schema.type_uri, paths=paths)

    def execute(
        self,
        inputs: Sequence[Entities],
        context: ExecutionContext,
    ) -> Entities:
        """Run the workflow operator."""
        self.log.info("Start")
        self.execution_context = context
        try:
            first_input: Entities = inputs[0]
        except IndexError:
            # if we have no input, we create a single input with a Null entity
            first_input = Entities(
                entities=iter([Entity(uri="urn:x-ecc:null", values=[])]),
                schema=EntitySchema(type_uri="urn:x-ecc:null-type", paths=[]),
            )
        if self.instruction_output_path in [_.path for _ in first_input.schema.paths]:
            raise SamePathError(self.instruction_output_path)
        additional_input_mapping = self._consume_additional_inputs(inputs)
        entities = self._process_entities(first_input, mapping=additional_input_mapping)
        schema = self._generate_output_schema(first_input.schema)
        self.log.info("End")
        return Entities(entities=entities, schema=schema)
