import os

from dotenv import load_dotenv
from litestar import Litestar
from litestar.config.compression import CompressionConfig
from litestar.config.cors import CORSConfig
from litestar.config.csrf import CSRFConfig
from litestar.stores.redis import RedisStore

from .assistants import assistants as assistant_registry
from .assistants.models import Assistant
from .db.init import init_db
from .routes.assistants import AssistantController
from .routes.knowledge import KnowledgeController
from .routes.security.auth import session_auth, session_backend_config
from .routes.security.csrf import csrf_token
from .routes.tasks import TaskController
from .shared import getenv
from .shared.pg import dispose_engine

# env variables auto loaded in docker compose
if os.getenv("REDIS_URL") is None:
    load_dotenv()


def create_app(assistants: list[Assistant] = []) -> Litestar:
    for assistant in assistants:
        assistant_registry.register(assistant)

    redis_store = RedisStore.with_client(url=getenv("REDIS_URL"))

    return Litestar(
        route_handlers=[
            csrf_token,
            AssistantController,
            TaskController,
            KnowledgeController,
            *assistant_registry.get_api_routes(),
        ],
        stores={
            session_backend_config.store: redis_store.with_namespace("sessions"),
        },
        lifespan=[*assistant_registry.get_callbacks("lifespan")],
        on_app_init=[
            session_auth.on_app_init,
            *assistant_registry.get_callbacks("on_app_init"),
        ],
        on_startup=[init_db, *assistant_registry.get_callbacks("on_startup")],
        on_shutdown=[dispose_engine, *assistant_registry.get_callbacks("on_shutdown")],
        csrf_config=CSRFConfig(
            secret=getenv("CSRF_SECRET"),
        ),
        cors_config=CORSConfig(
            allow_origins=[url.strip() for url in getenv("CLIENT_URL", "*").split(",")],
            allow_credentials=True,
        ),
        compression_config=CompressionConfig(backend="gzip"),
        openapi_config=None,
        debug=getenv("DEBUG", "false") == "true",
    )
