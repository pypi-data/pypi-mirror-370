from dotenv import load_dotenv

load_dotenv()


from fastapi.responses import RedirectResponse
from fastapi import FastAPI
from .routes.chat import router as chat_router
from ..utils.clear_console import clear_console
from ..config.llm_config import ConfigGPT, ConfigLLM
from .settings import FastappSettings
from ..utils.clear_console import clear_console


class FastApp:
    def __init__(
        self,
        extra_reponse_system_prompts: list[str] = [],
        extra_selection_system_prompts: list[str] = [],
        len_context: int = ConfigLLM.DEFAULT_HISTORY_LEN,
        middleware=None,
    ):
        # clear_console()
        FastappSettings.update(
            extra_reponse_system_prompts,
            extra_selection_system_prompts,
            len_context,
        )

    @property
    def app(self) -> FastAPI:
        app: FastAPI = FastAPI()
        # app.openapi = lambda: CustomOpenAPI(app)()
        # app.add_middleware(AccessTokenMiddleware)

        @app.get("/")
        async def root():
            return RedirectResponse(url="/docs")

        @app.get("/healt")
        async def healt():
            return {"status": "healtly"}

        app.include_router(chat_router)
        return app

    def run(self, host: str, port: int):
        clear_console()
        pass
