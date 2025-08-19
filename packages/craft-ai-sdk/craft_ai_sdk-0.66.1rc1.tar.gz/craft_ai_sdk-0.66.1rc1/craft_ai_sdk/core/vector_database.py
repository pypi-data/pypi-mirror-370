from typing import TypedDict

from craft_ai_sdk.shared.environments import get_environment_id

from ..sdk import BaseCraftAiSdk
from ..shared.logger import log_action, log_func_result


class VectorDatabaseCredentials(TypedDict):
    vector_database_url: str
    vector_database_token: str


def get_vector_database_credentials(sdk: BaseCraftAiSdk) -> VectorDatabaseCredentials:
    """Get the credentials of the vector database.

    Returns:
        :obj:`dict`: The vector database credentials, with the following keys:
            * ``"vector_database_url"`` (:obj:`str`): URL of the vector database.
            * ``"vector_database_token"`` (:obj:`str`): Token to connect to the vector
              database.
    """
    environment_id = get_environment_id(sdk)

    vector_database_url = (
        f"{sdk.base_control_api_url}/environments/{environment_id}/vector-database"
    )

    return sdk._get(vector_database_url)


@log_func_result("Connecting to Weaviate")
def get_weaviate_client(sdk: BaseCraftAiSdk):
    """Get the Weaviate client.

    Returns:
        :obj:`weaviate.WeaviateClient`: The Weaviate client.
    """
    try:
        import weaviate
    except ModuleNotFoundError:
        raise ModuleNotFoundError(
            "The 'weaviate' package is required to use the vector database. "
            "You can install it with 'pip install weaviate-client'."
        ) from None
    credentials = get_vector_database_credentials(sdk)

    is_secure = credentials["vector_database_url"].startswith("https://")

    vector_database_url = (
        credentials["vector_database_url"]
        .replace("http://", "")
        .replace("https://", "")
    ).rstrip("/")

    log_action(sdk, "Connecting to Weaviate")

    weaviate_client = weaviate.connect_to_custom(
        http_host=vector_database_url,
        http_port=8080,
        grpc_host=vector_database_url,
        grpc_port=8082,
        http_secure=is_secure,
        grpc_secure=is_secure,
        headers={
            "craft-vector-database-token": credentials["vector_database_token"],
            "craft-vector-database-url": credentials["vector_database_url"],
        },
        auth_credentials=None,
    )

    log_action(
        sdk,
        f"Connected to Weaviate, using version {weaviate.__version__}",
    )

    return weaviate_client
