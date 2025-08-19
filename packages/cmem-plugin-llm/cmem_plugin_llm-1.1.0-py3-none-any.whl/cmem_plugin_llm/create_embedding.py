"""Create Embeddings via OpenAI embeddings API endpoint"""

from collections.abc import Generator, Sequence

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
from cmem_plugin_base.dataintegration.parameter.password import Password, PasswordParameterType
from cmem_plugin_base.dataintegration.plugins import WorkflowPlugin
from cmem_plugin_base.dataintegration.ports import (
    FixedNumberOfInputs,
    FixedSchemaPort,
    FlexibleSchemaPort,
    UnknownSchemaPort,
)
from langchain_core.utils.utils import convert_to_secret_str
from langchain_openai import OpenAIEmbeddings

from cmem_plugin_llm.commons import OpenAPIModel, SamePathError, input_paths_to_list

DEFAULT_EMBEDDING_PATH = "_embedding"
DEFAULT_EMBEDDING_SOURCE_PATH = "_embedding_source"
MODEL_EXAMPLE = "text-embedding-3-small"


@Plugin(
    label="Create Embeddings",
    plugin_id="cmem_plugin_llm-CreateEmbeddings",
    icon=Icon(package=__package__, file_name="create_embedding.svg"),
    description="Fetch and output LLM created embeddings from input entities.",
    documentation="""
This plugin creates vector embeddings from text data using OpenAI's embeddings API.
It processes input entities containing text data and generates high-dimensional vector
representations that capture semantic meaning.

## Features

- Supports OpenAI embeddings models (e.g., text-embedding-3-small)
- Batch processing for efficient API usage
- Configurable input/output paths
- Automatic schema generation based on configuration
- Built-in error handling and workflow cancellation support

## Configuration

- **URL**: OpenAI API endpoint (default: https://api.openai.com/v1)
- **API Key**: Your OpenAI API key for authentication
- **Model**: The embedding model to use (e.g., text-embedding-3-small)
- **Timeout**: Request timeout in milliseconds (default: 10000)
- **Buffer Size**: Number of texts to process per batch (default: 100)
- **Input Paths**: Comma-separated list of entity paths to embed (default: "text")
- **Output Paths**: Configurable paths for embedding vectors and source text

## Input/Output

- **Input**: Entities with text data in specified paths
- **Output**: Original entities enhanced with embedding vectors and source text
- Embedding vectors are stored as string representations of float arrays
- Source text used for embedding is preserved for reference

## Use Cases

- Semantic search and similarity matching
- Text clustering and classification
- Recommendation systems
- Natural language processing pipelines""",
    parameters=[
        PluginParameter(
            name="base_url",
            label="Base URL",
            description="URL of the OpenAI API (without endpoint path and without trailing slash)",
            default_value="https://api.openai.com/v1",
        ),
        PluginParameter(
            name="api_key",
            label="The OpenAI API key",
            param_type=PasswordParameterType(),
            description="Fill the OpenAI API key if needed "
            "(or give a dummy value in case you access an unsecured endpoint).",
        ),
        PluginParameter(
            name="model",
            label=f"The embeddings model, e.g. {MODEL_EXAMPLE}",
            description="The embeddings model to use (e.g., text-embedding-3-small).",
            param_type=OpenAPIModel(),
        ),
        PluginParameter(
            name="embedding_paths",
            label="Embedding entity paths (comma-separated list)",
            description="Changing this value will change, which input paths are used by the "
            "workflow task to calculate embeddings. A blank value means, all paths are used.",
            default_value="text",
        ),
        PluginParameter(
            name="forward_paths",
            label="Forward entity paths (comma-separated list)",
            description="Paths from input entities to forward to output without modification. "
            "These paths will be passed through unchanged alongside embeddings.",
            default_value="",
        ),
        PluginParameter(
            name="timout_single_request",
            label="Timeout (Single Request, in Milliseconds)",
            advanced=True,
            default_value=10000,
        ),
        PluginParameter(
            name="entries_processing_buffer",
            label="Entries Processing Buffer",
            description="How many input values do you want to send per request?",
            advanced=True,
            default_value=100,
        ),
        PluginParameter(
            name="embedding_output_path",
            label="Entity Embedding path (output)",
            description=f"Changing this value will change the output schema accordingly. "
            f"Default: {DEFAULT_EMBEDDING_PATH}",
            advanced=True,
            default_value=DEFAULT_EMBEDDING_PATH,
        ),
        PluginParameter(
            name="embedding_output_text",
            label="Entity Embedding text (output)",
            description=f"Changing this value will change the output schema accordingly. "
            f"Default: {DEFAULT_EMBEDDING_SOURCE_PATH}",
            advanced=True,
            default_value=DEFAULT_EMBEDDING_SOURCE_PATH,
        ),
    ],
)
class CreateEmbeddings(WorkflowPlugin):
    """Fetch embeddings from OpenAI embeddings API endpoint"""

    execution_context: ExecutionContext
    embeddings: OpenAIEmbeddings
    entries_processing_buffer: int
    embedding_output_text: str
    embedding_output_path: str
    embedding_paths: list[str]
    forward_paths: list[str]
    embedding_report: ExecutionReport

    def __init__(  # noqa: PLR0913
        self,
        base_url: str,
        api_key: Password | str = "",
        model: str = MODEL_EXAMPLE,
        timout_single_request: int = 10000,
        entries_processing_buffer: int = 100,
        embedding_paths: str = "",
        embedding_output_text: str = DEFAULT_EMBEDDING_SOURCE_PATH,
        embedding_output_path: str = DEFAULT_EMBEDDING_PATH,
        forward_paths: str = "",
    ) -> None:
        self.base_url = base_url
        self.timout_single_request = timout_single_request
        self.api_key = api_key if isinstance(api_key, str) else api_key.decrypt()
        if self.api_key == "":
            self.api_key = "dummy-key"
        self.embeddings = OpenAIEmbeddings(
            base_url=base_url,
            api_key=convert_to_secret_str(self.api_key),
            model=model,
            timeout=timout_single_request,
        )
        self.entries_processing_buffer = entries_processing_buffer
        self.embedding_output_text = embedding_output_text
        self.embedding_output_path = embedding_output_path
        self.embedding_paths = input_paths_to_list(embedding_paths)
        self.forward_paths = input_paths_to_list(forward_paths)
        self.embedding_report = ExecutionReport()
        self.embedding_report.operation = "create"
        self.embedding_report.operation_desc = "embeddings created"
        self._setup_ports()
        if self.embedding_output_text in self.embedding_paths:
            raise SamePathError(self.embedding_output_text)
        if self.embedding_output_path in self.embedding_paths:
            raise SamePathError(self.embedding_output_path)

    def _setup_ports(self) -> None:
        """Configure input and output ports depending on the configuration"""
        if len(self.embedding_paths) == 0:
            self.input_ports = FixedNumberOfInputs([FlexibleSchemaPort()])
            self.output_port = UnknownSchemaPort()
            return

        input_paths = [EntityPath(path=_) for _ in [*self.embedding_paths, *self.forward_paths]]
        input_schema = EntitySchema(type_uri="entity", paths=input_paths)
        self.input_ports = FixedNumberOfInputs(ports=[FixedSchemaPort(schema=input_schema)])

        output_paths = [
            EntityPath(path=_)
            for _ in [
                *self.embedding_paths,
                *self.forward_paths,
                self.embedding_output_path,
                self.embedding_output_text,
            ]
        ]
        output_schema = EntitySchema(type_uri="entity", paths=output_paths)
        self.output_port = FixedSchemaPort(schema=output_schema)

    def _generate_output_schema(self, input_schema: EntitySchema) -> EntitySchema:
        """Get output schema"""
        paths = list(input_schema.paths).copy()
        # Add forward paths that aren't already in the schema
        for forward_path in self.forward_paths:
            if not any(path.path == forward_path for path in paths):
                paths.append(EntityPath(forward_path))
        paths.append(EntityPath(self.embedding_output_path))
        paths.append(EntityPath(self.embedding_output_text))
        return EntitySchema(type_uri=input_schema.type_uri, paths=paths)

    def workflow_canceling(self) -> bool:
        """Check if the workflow is canceling / cancelled"""
        try:
            if self.execution_context.workflow.status() == "Canceling":
                self.log.info("End task (Cancelled Workflow).")
                return True
        except AttributeError:
            pass
        return False

    def _embedding_report_update(self, n: int) -> None:
        if hasattr(self.execution_context, "report"):
            self.embedding_report.entity_count += n
            self.execution_context.report.update(self.embedding_report)

    @staticmethod
    def chunker(seq: Sequence, size: int) -> Generator[Sequence]:
        """Split a sequence into chunks"""
        chunk = []
        for entry in seq:
            chunk.append(entry)
            if len(chunk) == size:
                yield chunk.copy()
                chunk.clear()
        if len(chunk) > 0:
            yield chunk.copy()

    @staticmethod
    def _select_keys(original_dict: dict[str, list[str]], keys: list[str]) -> dict[str, list[str]]:
        """Select specific keys from a dictionary"""
        return {k: v for k, v in original_dict.items() if k in keys}

    @staticmethod
    def _entity_to_dict(paths: Sequence[EntityPath], entity: Entity) -> dict[str, list[str]]:
        """Create a dict representation of an entity"""
        entity_dic = {}
        for key, value in zip(paths, entity.values, strict=False):
            entity_dic[key.path] = list(value)
        return entity_dic

    def _generate_embedding_source(
        self, entity: Entity, entity_dict: dict[str, list[str]], embedding_paths: list[str]
    ) -> str:
        """Generate embedding source text from entity"""
        entity_embedding_dict = self._select_keys(original_dict=entity_dict, keys=embedding_paths)

        if len(entity.values) == 1 and len(entity.values[0]) == 1:
            # if there is only a single value -> no JSON
            return str(entity.values[0][0])
        if len(embedding_paths) == 1 and len(entity_dict.get(embedding_paths[0], [])) == 1:
            # if only one path is selected (and it contains only one value) -> no JSON
            return entity_dict.get(embedding_paths[0], [])[0]
        return str(entity_embedding_dict)

    def _add_forward_paths_to_entity_dict(
        self,
        entity_dict: dict[str, list[str]],
        original_entity: Entity,
        entities_schema_paths: Sequence[EntityPath],
    ) -> None:
        """Add forward paths from original entity to entity dict"""
        original_entity_dict = self._entity_to_dict(
            paths=entities_schema_paths, entity=original_entity
        )
        for forward_path in self.forward_paths:
            if forward_path in original_entity_dict:
                entity_dict[forward_path] = original_entity_dict[forward_path]
            elif forward_path not in entity_dict:
                # If forward path doesn't exist in original entity, add empty list
                entity_dict[forward_path] = []

    def _process_entities(self, entities: Entities) -> Generator[Entity]:
        """Process an entity list (chunked), yielding new entity objects"""
        self._embedding_report_update(0)
        for entity_chunk in self.chunker(entities.entities, self.entries_processing_buffer):
            embeddings_sources: list[str] = []  # a list of embedding source texts
            entity_dicts: list[dict[str, list[str]]] = []  # a list of entity dictionaries
            entity: Entity
            if self.workflow_canceling():
                break
            embedding_paths: list[str] = [_.path for _ in entities.schema.paths]
            if len(self.embedding_paths) > 0:
                embedding_paths = self.embedding_paths
            for entity in entity_chunk:
                entity_dict = self._entity_to_dict(paths=entities.schema.paths, entity=entity)
                entity_dicts.append(entity_dict)
                embedding_source = self._generate_embedding_source(
                    entity=entity, entity_dict=entity_dict, embedding_paths=embedding_paths
                )
                embeddings_sources.append(embedding_source)
            embeddings: list[list[float]] = self.embeddings.embed_documents(
                texts=embeddings_sources
            )
            self._embedding_report_update(len(embeddings_sources))

            # looping over list of embeddings, entity dicts, sources and entities
            for (
                entity_embedding,
                entity_dict,
                embedding_source,
                original_entity,
            ) in zip(
                embeddings,
                entity_dicts,
                embeddings_sources,
                entity_chunk,
                strict=False,
            ):
                # add string repr of the embedding as a single value list
                entity_dict[self.embedding_output_path] = [str(entity_embedding)]
                # add string repr of the embedding source as a single value list
                entity_dict[self.embedding_output_text] = [embedding_source]

                # add forward paths from original entity
                self._add_forward_paths_to_entity_dict(
                    entity_dict=entity_dict,
                    original_entity=original_entity,
                    entities_schema_paths=entities.schema.paths,
                )

                values = list(entity_dict.values())
                yield Entity(uri=original_entity.uri, values=values)

    def execute(
        self,
        inputs: Sequence[Entities],
        context: ExecutionContext,
    ) -> Entities:
        """Run the workflow operator."""
        self.log.info("Start")
        self.execution_context = context
        first_input: Entities = inputs[0]
        for input_path in [_.path for _ in first_input.schema.paths]:
            if input_path in [self.embedding_output_path, self.embedding_output_text]:
                raise SamePathError(input_path)
        entities = self._process_entities(entities=first_input)
        schema = self._generate_output_schema(input_schema=first_input.schema)
        self.log.info("End")
        return Entities(entities=entities, schema=schema)
