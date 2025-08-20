"""
Chroma DB required connection information
"""

from dataclasses import dataclass
from typing import Literal, TypedDict, Union


class HuggingFaceEFInputs(TypedDict):
    ef_type: Literal["hf"]
    api_key: str
    model_name: str


class OpenAIEFInputs(TypedDict):
    ef_type: Literal["openai"]
    api_key: str
    model_name: str


class OpenAIAzureEFInputs(TypedDict):
    ef_type: Literal["openai_azure"]
    api_key: str
    model_name: str
    api_base: str
    api_version: str


class SentenceTransformerEFInputs(TypedDict):
    ef_type: Literal["sentence_transformer"]
    model_name: str


@dataclass
class ChromaDB:
    """Class for storing chroma connection details"""

    def __post_init__(self):
        self.db_type = "chroma_db"

    host: str
    port: int
    collection: str
    ef_inputs: Union[
        HuggingFaceEFInputs, OpenAIEFInputs, OpenAIAzureEFInputs, SentenceTransformerEFInputs
    ]


@dataclass
class CustomRagDB:
    """Class for storing custom rag adapter connection details"""

    def __post_init__(self):
        self.db_type = "custom_rag_db"

    custom_rag_application_id: int


@dataclass
class LlamaIndexDB:
    """Class for storing llama index remote connection details for AWS S3"""

    def __post_init__(self):
        self.db_type = "llamaindex_db"
        if self.aws_key == "" or self.aws_secret == "":
            raise ValueError("appropriate AWS credentials required.")
        if self.s3_bucket_name == "":
            raise ValueError("valid s3 bucket name is required.")
        if self.index_id == "":
            raise ValueError("non-empty index_id is required.")

    aws_key: str
    aws_secret: str
    s3_bucket_name: str
    ef_inputs: Union[
        HuggingFaceEFInputs, OpenAIEFInputs, OpenAIAzureEFInputs, SentenceTransformerEFInputs
    ]
    index_id: Union[str, None] = None


@dataclass
class LlamaIndexWithChromaDB:
    """Class for storing chroma connection details used with llama index"""

    def __post_init__(self):
        self.db_type = "llamaindex+chroma_db"

    host: str
    port: int
    collection: str
    ef_inputs: Union[
        HuggingFaceEFInputs, OpenAIEFInputs, OpenAIAzureEFInputs, SentenceTransformerEFInputs
    ]


@dataclass
class PostgresVectorDB:
    """Class for storing postgres vector database details
    dbname – the database name (database is a deprecated alias)

    user – user name used to authenticate

    password – password used to authenticate

    host – database host address (defaults to UNIX socket if not provided)

    port – connection port number (defaults to 5432 if not provided)"""

    def __post_init__(self):
        self.db_type = "postgres"

    user: str
    password: str
    host: str
    port: int
    db_name: str
    table_name: str
    content_column: str
    id_column: str
    ef_inputs: Union[
        HuggingFaceEFInputs, OpenAIEFInputs, OpenAIAzureEFInputs, SentenceTransformerEFInputs
    ]


@dataclass
class DatabricksVectorSearch:
    """Class for storing Databricks vector search details"""

    def __post_init__(self):
        self.db_type = "databricks"

    host: str
    index_name: str
    token: str
    id_column: str
    content_column: str
