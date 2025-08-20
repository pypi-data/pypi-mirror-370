"""
main.py - QuickBot RAD Framework Main Application Module

Defines QuickBot, the main entry point for the QuickBot rapid application development (RAD) framework for Telegram bots.
Integrates FastAPI (HTTP API), Aiogram (Telegram bot logic), SQLModel (async DB), and i18n (internationalization).

Key Features:
- Dynamic registration of CRUD API endpoints for all entities
- Telegram bot command and webhook management
- Row-level security (RLS) and user management
- Middleware for authentication and localization
- Swagger UI with Telegram login integration
"""

from contextlib import asynccontextmanager
from inspect import iscoroutinefunction
from typing import Union
from typing import Annotated, Callable, Any, Generic, TypeVar
from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.telegram import TelegramAPIServer
from aiogram.client.default import DefaultBotProperties
from aiogram.types import Message, BotCommand as AiogramBotCommand
from aiogram.utils.callback_answer import CallbackAnswerMiddleware
from aiogram.utils.i18n import I18n
from fastapi import Depends, FastAPI, Request, Body, Path, HTTPException
from fastapi.applications import Lifespan, AppType
from fastapi.datastructures import State
from logging import getLogger
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.openapi.utils import get_openapi
from sqlmodel.ext.asyncio.session import AsyncSession

from quickbot.bot.handlers.user_handlers.main import command_handler
from quickbot.db import get_db
from quickbot.model.list_schema import ListSchema
from quickbot.plugin import Registerable
from quickbot.utils.main import clear_state
from quickbot.utils.navigation import save_navigation_context
from quickbot.model.crud_service import NotFoundError, ForbiddenError

from .config import Config
from .bot.handlers.forms.entity_form import entity_item
from .fsm.db_storage import DbStorage
from .middleware.telegram import AuthMiddleware, I18nMiddleware
from .model.bot_entity import BotEntity
from .model.user import UserBase
from .model.bot_metadata import BotMetadata
from .model.descriptors import (
    BotCommand,
    EntityDescriptor,
    ProcessDescriptor,
    BotContext,
)
from .model.crud_command import CrudCommand
from .bot.handlers.context import CallbackCommand, ContextData
from .router import Router
from .api_route.models import list_entity_items, get_me
from .api_route.depends import get_current_user


logger = getLogger(__name__)

UserType = TypeVar("UserType", bound=UserBase, default=UserBase)
ConfigType = TypeVar("ConfigType", bound=Config, default=Config)


@asynccontextmanager
async def default_lifespan(app: "QuickBot"):
    logger.debug("starting qbot app")

    if app.lifespan_bot_init:
        await app.bot_init()

    if app.lifespan_set_webhook:
        await app.set_webhook()

    app.config.TELEGRAM_BOT_USERNAME = (await app.bot.get_me()).username

    logger.info("qbot app started")

    if app.lifespan:
        async with app.lifespan(app) as state:
            yield state
    else:
        yield

    logger.info("qbot app stopped")


class QuickBot(Generic[UserType, ConfigType], FastAPI):
    """
    Main application class for QuickBot RAD framework.

    Integrates FastAPI, Aiogram, SQLModel, and i18n for rapid Telegram bot development.
    Handles bot initialization, API registration, command routing, and RLS.

    Args:
        config: App configuration (see quickbot/config.py)
        user_class: User model class (subclass of UserBase)
        bot_start: Optional custom bot start handler
        lifespan: Optional FastAPI lifespan context
        lifespan_bot_init: Whether to run bot init on startup
        lifespan_set_webhook: Whether to set webhook on startup
        webhook_handler: Optional custom webhook handler
        allowed_updates: List of Telegram update types to allow
    """

    def __init__(
        self,
        config: ConfigType = Config(),
        user_class: type[UserType] = None,
        bot_start: Callable[
            [
                Callable[[Message, Any], tuple[UserType, bool]],
                Message,
                Any,
            ],
            None,
        ] = None,
        lifespan: Lifespan[AppType] | None = None,
        lifespan_bot_init: bool = True,
        lifespan_set_webhook: bool = True,
        webhook_handler: Callable[["QuickBot", Request], Any] = None,
        allowed_updates: list[str] | None = None,
        **kwargs,
    ):
        # --- Initialize default user class if not provided ---
        if user_class is None:
            from .model.default_user import DefaultUser

            user_class = DefaultUser

        self.allowed_updates = list(
            (set(allowed_updates or [])).union({"message", "callback_query"})
        )

        self.user_class = user_class
        self.bot_metadata: BotMetadata = user_class.bot_metadata
        self.bot_metadata.app = self
        self.config = config
        self.lifespan = lifespan
        # --- Setup Telegram API server and session ---
        api_server = TelegramAPIServer.from_base(
            self.config.TELEGRAM_BOT_SERVER,
            is_local=self.config.TELEGRAM_BOT_SERVER_IS_LOCAL,
        )
        session = AiohttpSession(api=api_server)

        # --- Initialize Telegram Bot instance ---
        self.bot = Bot(
            token=self.config.TELEGRAM_BOT_TOKEN,
            session=session,
            default=DefaultBotProperties(
                parse_mode="HTML", link_preview_is_disabled=True
            ),
        )

        # --- Setup Aiogram dispatcher with DB storage for FSM ---
        dp = Dispatcher(storage=DbStorage())

        # --- Setup i18n and middleware ---
        self.i18n = I18n(path="locales", default_locale="en", domain="messages")
        i18n_middleware = I18nMiddleware(user_class=user_class, i18n=self.i18n)
        i18n_middleware.setup(dp)
        dp.callback_query.middleware(CallbackAnswerMiddleware())

        # --- Register core routers (start, main menu) ---
        from .bot.handlers.start import router as start_router

        dp.include_router(start_router)
        from .bot.handlers.menu.main import router as main_menu_router

        # Register authentication middleware for menu routers
        self.auth = AuthMiddleware(user_class=user_class)
        main_menu_router.message.middleware.register(self.auth)
        main_menu_router.callback_query.middleware.register(self.auth)
        dp.include_router(main_menu_router)

        self.dp = dp

        # --- Extension points for custom bot start and webhook handlers ---
        self.start_handler = bot_start
        self.webhook_handler = webhook_handler
        self.bot_commands = dict[str, BotCommand]()

        self.lifespan_bot_init = lifespan_bot_init
        self.lifespan_set_webhook = lifespan_set_webhook

        # --- Initialize FastAPI with custom lifespan and no default docs ---
        super().__init__(lifespan=default_lifespan, docs_url=None, **kwargs)

        self.bot_metadata.app_state = self.state

        # --- Initialize plugins ---
        self.plugins = dict[str, Any]()

        # --- Register Telegram API router for /telegram endpoints (for webhook and auth) ---
        from .api_route.telegram import router as telegram_router

        self.include_router(telegram_router, prefix="/telegram", tags=["telegram"])
        self.root_router = Router()
        self.root_router._commands = self.bot_commands
        self.command = self.root_router.command

        # --- Register all entity CRUD endpoints dynamically (for models API) ---
        self.register_models_api()
        # --- Register custom Swagger UI with Telegram login (for docs) ---
        self.register_swagger_ui_html()

    def register_plugin(self, plugin: Any):
        self.plugins[type(plugin).__name__] = plugin
        if isinstance(plugin, Registerable):
            plugin.register(self)

    def register_swagger_ui_html(self):
        """
        Register a custom /docs endpoint with Telegram login widget and JWT support for Swagger UI.
        """

        def swagger_ui_html():
            return HTMLResponse(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="utf-8" />
                    <meta name="viewport" content="width=device-width, initial-scale=1" />
                    <meta name="description" content="SwaggerUI" />
                    <title>QuickBot API</title>
                    <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5.26.2/swagger-ui.css" />
                </head>
                <body>
                    <div id="swagger-ui"></div>
                    <script src="https://unpkg.com/swagger-ui-dist@5.26.2/swagger-ui-bundle.js" crossorigin></script>
                    <script>
                        function logout() {{
                            localStorage.removeItem("jwt");
                            window.ui.preauthorizeApiKey("bearerAuth", "invalid.token");
                            //location.reload();
                        }}

                        function injectTelegramWidget(jwt) {{
                            const auth_wrapper = document.querySelector(".auth-wrapper");
                            if (!auth_wrapper) return;

                            const oldAuthBtn = auth_wrapper.querySelector(".authorize");
                            if (oldAuthBtn) oldAuthBtn.remove();

                            const authContainer = document.createElement("div");
                            authContainer.className = "auth-info";

                            /*if (jwt) {{
                                try {{
                                    console.log(jwt);
                                    const payload = JSON.parse(atob(jwt.split('.')[1]));
                                    const username = payload.username || payload.id;

                                    authContainer.innerHTML = `
                                        <span>👤 ${{username}}</span>
                                        <button class="logout-btn" onclick="logout()">Logout</button>
                                    `;
                                }} catch (e) {{
                                    authContainer.textContent = "JWT error";
                                }}
                            }} else {{*/
                                const script = document.createElement("script");
                                script.async = true;
                                script.src = "https://telegram.org/js/telegram-widget.js";
                                script.setAttribute("data-telegram-login", "{self.config.TELEGRAM_BOT_USERNAME}");
                                script.setAttribute("data-size", "large");
                                script.setAttribute("data-onauth", "handleTelegramAuth(user)");
                                script.setAttribute("data-request-access", "write");
                                authContainer.appendChild(script);
                            //}}

                            auth_wrapper.appendChild(authContainer);
                        }}

                        function waitForElement(selector, callback) {{
                            const el = document.querySelector(selector);
                            if (el) {{
                                callback(el);
                                return;
                            }}
                            const observer = new MutationObserver(() => {{
                                const el = document.querySelector(selector);
                                if (el) {{
                                    observer.disconnect();
                                    callback(el);
                                }}
                            }});
                            observer.observe(document.body, {{ childList: true, subtree: true }});
                        }}

                        function handleTelegramAuth(user) {{
                            fetch('/telegram/auth', {{
                                method: 'POST',
                                headers: {{ 'Content-Type': 'application/json' }},
                                body: JSON.stringify(user)
                            }})
                            .then(res => res.json())
                            .then(data => {{
                                localStorage.setItem("jwt", data.access_token);
                                window.ui.preauthorizeApiKey("bearerAuth", data.access_token);
                                //location.reload();
                            }})
                            .catch(() => alert("Authorization error"));
                        }}

                        window.handleTelegramAuth = handleTelegramAuth;

                        window.onload = function () {{
                            const jwt = localStorage.getItem("jwt", null);

                            window.ui = SwaggerUIBundle({{
                                url: '/openapi.json',
                                dom_id: '#swagger-ui',
                                onComplete: function () {{
                                    if (jwt) {{
                                        window.ui.preauthorizeApiKey("bearerAuth", jwt);
                                    }}
                                    waitForElement(".auth-wrapper", (el) => {{
                                        injectTelegramWidget(jwt);
                                    }});
                                }}
                            }});
                        }};
                    </script>
                </body>
                </html>
                """)

        self.router.add_api_route(
            path="/docs",
            include_in_schema=False,
            endpoint=swagger_ui_html,
            methods=["GET"],
            tags=["docs"],
        )

        def openapi_json():
            schema = get_openapi(
                title="FastAPI + Telegram OAuth",
                version="1.0.0",
                description="Swagger с Telegram Login",
                routes=self.routes,
            )
            schema["components"]["securitySchemes"] = {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "JWT",
                }
            }
            for path in schema["paths"].values():
                for op in path.values():
                    op.setdefault("security", [{"bearerAuth": []}])
            return JSONResponse(schema)

        self.router.add_api_route(
            path="/openapi.json",
            endpoint=openapi_json,
            methods=["GET"],
            tags=["docs"],
            include_in_schema=False,
        )

    def register_models_api(self):
        """
        Dynamically register CRUD API endpoints for all entities in the app's metadata.
        Endpoints: list, create, get by id, update, delete.
        Uses FastAPI dependency injection for database session and user authentication.
        """

        def make_create_api_endpoint(entity_descriptor: EntityDescriptor):
            async def create_entity(
                db_session: Annotated[AsyncSession, Depends(get_db)],
                request: Request,
                obj_in: entity_descriptor.crud.create_schema = Body(...),
                current_user=Depends(get_current_user),
            ):
                try:
                    ret_obj = await entity_descriptor.crud.create(
                        db_session=db_session,
                        user=current_user,
                        model=obj_in,
                    )
                except NotFoundError as e:
                    raise HTTPException(status_code=404, detail=e.args[0])
                except ForbiddenError as e:
                    raise HTTPException(status_code=403, detail=e.args[0])
                except Exception as e:
                    logger.error(f"Error creating entity: {e}")
                    raise HTTPException(status_code=500, detail="Internal server error")
                return ret_obj

            return create_entity

        def make_update_api_endpoint(entity_descriptor: EntityDescriptor):
            async def update_entity(
                db_session: Annotated[AsyncSession, Depends(get_db)],
                request: Request,
                id: int = Path(..., description="ID of the entity to update"),
                obj_in: entity_descriptor.crud.update_schema = Body(...),
                current_user=Depends(get_current_user),
            ):
                try:
                    entity = await entity_descriptor.crud.update(
                        db_session=db_session,
                        id=id,
                        model=obj_in,
                        user=current_user,
                    )
                except NotFoundError as e:
                    raise HTTPException(status_code=404, detail=e.args[0])
                except ForbiddenError as e:
                    raise HTTPException(status_code=403, detail=e.args[0])
                except Exception as e:
                    logger.error(f"Error updating entity: {e}")
                    raise HTTPException(status_code=500, detail="Internal server error")
                return entity

            return update_entity

        def make_delete_api_endpoint(entity_descriptor: EntityDescriptor):
            async def delete_entity(
                db_session: Annotated[AsyncSession, Depends(get_db)],
                request: Request,
                id: int = Path(..., description="ID of the entity to delete"),
                current_user=Depends(get_current_user),
            ):
                try:
                    entity = await entity_descriptor.crud.delete(
                        db_session=db_session,
                        id=id,
                        user=current_user,
                    )
                except NotFoundError as e:
                    raise HTTPException(status_code=404, detail=e.args[0])
                except ForbiddenError as e:
                    raise HTTPException(status_code=403, detail=e.args[0])
                except Exception as e:
                    logger.error(f"Error deleting entity: {e}")
                    raise HTTPException(status_code=500, detail="Internal server error")
                return entity

            return delete_entity

        def make_get_by_id_api_endpoint(entity_descriptor: EntityDescriptor):
            async def get_entity_by_id(
                db_session: Annotated[AsyncSession, Depends(get_db)],
                request: Request,
                id: int = Path(..., description="ID of the entity to get"),
                current_user=Depends(get_current_user),
            ):
                try:
                    entity = await entity_descriptor.type_.get(
                        session=db_session,
                        id=id,
                    )
                except NotFoundError as e:
                    raise HTTPException(status_code=404, detail=e.args[0])
                except ForbiddenError as e:
                    raise HTTPException(status_code=403, detail=e.args[0])
                except Exception as e:
                    logger.error(f"Error getting entity: {e}")
                    raise HTTPException(status_code=500, detail="Internal server error")
                return entity

            return get_entity_by_id

        def make_process_api_endpoint(process_descriptor: ProcessDescriptor):
            async def run_process(
                db_session: Annotated[AsyncSession, Depends(get_db)],
                current_user: Annotated[UserBase, Depends(get_current_user)],
                request: Request,
                obj_in: process_descriptor.input_schema = Body(...),
            ):
                for role in current_user.roles:
                    if role in process_descriptor.roles:
                        break
                else:
                    raise HTTPException(status_code=403, detail="Forbidden")

                run_func = process_descriptor.process_class.run
                bot_context = BotContext(
                    db_session=db_session,
                    app=current_user.bot_metadata.app,
                    app_state=current_user.bot_metadata.app_state,
                    user=current_user,
                )

                try:
                    if iscoroutinefunction(run_func):
                        result = await run_func(
                            context=bot_context,
                            parameters=obj_in,
                        )
                    else:
                        result = run_func(
                            context=bot_context,
                            parameters=obj_in,
                        )
                    return result
                except Exception as e:
                    logger.error(f"Error running process: {e}")
                    raise HTTPException(status_code=500, detail="Internal server error")

            return run_process

        for entity_descriptor in self.bot_metadata.entity_descriptors.values():
            if issubclass(entity_descriptor.type_, UserBase):
                self.router.add_api_route(
                    path=f"/models/{entity_descriptor.name}/me",
                    methods=["GET"],
                    endpoint=get_me,
                    response_model=entity_descriptor.crud.schema,
                    summary="Get current user",
                    description="Get current user",
                    tags=["models"],
                )

            if CrudCommand.LIST in entity_descriptor.crud.commands:
                self.router.add_api_route(
                    path=f"/models/{entity_descriptor.name}",
                    endpoint=list_entity_items,
                    methods=["GET"],
                    response_model=list[
                        Union[entity_descriptor.crud.schema, ListSchema]
                    ],
                    summary=f"List {entity_descriptor.name}",
                    description=f"List {entity_descriptor.name}",
                    tags=["models"],
                )

            if CrudCommand.CREATE in entity_descriptor.crud.commands:
                self.router.add_api_route(
                    path=f"/models/{entity_descriptor.name}",
                    methods=["POST"],
                    endpoint=make_create_api_endpoint(entity_descriptor),
                    response_model=entity_descriptor.crud.schema,
                    summary=f"Create {entity_descriptor.name}",
                    description=f"Create {entity_descriptor.name}",
                    tags=["models"],
                )

            if CrudCommand.GET_BY_ID in entity_descriptor.crud.commands:
                self.router.add_api_route(
                    path=f"/models/{entity_descriptor.name}/{{id}}",
                    methods=["GET"],
                    endpoint=make_get_by_id_api_endpoint(entity_descriptor),
                    response_model=entity_descriptor.crud.schema,
                    summary=f"Get {entity_descriptor.name} by id",
                    description=f"Get {entity_descriptor.name} by id",
                    tags=["models"],
                )

            if CrudCommand.UPDATE in entity_descriptor.crud.commands:
                self.router.add_api_route(
                    path=f"/models/{entity_descriptor.name}/{{id}}",
                    methods=["PATCH"],
                    endpoint=make_update_api_endpoint(entity_descriptor),
                    response_model=Union[entity_descriptor.crud.schema, ListSchema],
                    summary=f"Update {entity_descriptor.name}",
                    description=f"Update {entity_descriptor.name}",
                    tags=["models"],
                )

            if CrudCommand.DELETE in entity_descriptor.crud.commands:
                self.router.add_api_route(
                    path=f"/models/{entity_descriptor.name}/{{id}}",
                    methods=["DELETE"],
                    endpoint=make_delete_api_endpoint(entity_descriptor),
                    response_model=Union[entity_descriptor.crud.schema, ListSchema],
                    summary=f"Delete {entity_descriptor.name}",
                    description=f"Delete {entity_descriptor.name}",
                    tags=["models"],
                )

        for process_descriptor in self.bot_metadata.process_descriptors.values():
            self.router.add_api_route(
                path=f"/processes/{process_descriptor.name}",
                methods=["POST"],
                endpoint=make_process_api_endpoint(process_descriptor),
                response_model=process_descriptor.output_schema,
                summary=f"Run {process_descriptor.name}",
                description=process_descriptor.description,
                tags=["processes"],
            )

    def register_routers(self, *routers: Router):
        # Register additional routers and their commands with the application.
        # This allows modular extension of bot command sets and menu trees.
        for router in routers:
            for command_name, command in router._commands.items():
                self.bot_commands[command_name] = command

    async def bot_init(self):
        # --- Set up bot commands for all locales ---
        # This method collects all commands (with captions) that should be shown in the Telegram UI.
        # It supports localization by grouping commands by locale.
        commands_captions = dict[str, list[tuple[str, str]]]()

        for command_name, command in self.bot_commands.items():
            if command.show_in_bot_commands:
                if isinstance(command.caption, str) or command.caption is None:
                    # Default locale (or no caption provided)
                    if "default" not in commands_captions:
                        commands_captions["default"] = []
                    commands_captions["default"].append(
                        (command_name, command.caption or command_name)
                    )
                else:
                    # Localized captions per locale
                    for locale, description in command.caption.items():
                        locale = "default" if locale == "en" else locale
                        if locale not in commands_captions:
                            commands_captions[locale] = []
                        commands_captions[locale].append((command_name, description))

        # Register commands with Telegram for each locale
        for locale, commands in commands_captions.items():
            await self.bot.set_my_commands(
                [
                    AiogramBotCommand(command=command[0], description=command[1])
                    for command in commands
                ],
                language_code=None if locale == "default" else locale,
            )

    async def set_webhook(self):
        # --- Set Telegram webhook for receiving updates ---
        # This is called on startup if lifespan_set_webhook is True.
        await self.bot.set_webhook(
            url=f"{self.config.TELEGRAM_WEBHOOK_URL}/telegram/webhook",
            drop_pending_updates=True,
            allowed_updates=self.allowed_updates,
            secret_token=self.config.TELEGRAM_WEBHOOK_AUTH_KEY,
        )

    async def show_form(
        self,
        app_state: State,
        user_id: int,
        entity: type[BotEntity] | str,
        entity_id: int,
        db_session: AsyncSession,
        form_name: str = None,
        form_params: list[Any] = None,
    ):
        # --- Show a form for a specific entity instance to a user ---
        # Used for interactive entity editing or viewing in the Telegram bot UI.
        f_params = []

        if form_name:
            f_params.append(form_name)

        if form_params:
            f_params.extend([str(p) for p in form_params])

        # Allow passing entity as class or string name
        if isinstance(entity, type):
            entity = entity.bot_entity_descriptor.name

        # Prepare callback data for navigation stack
        callback_data = ContextData(
            command=CallbackCommand.ENTITY_ITEM,
            entity_name=entity,
            entity_id=entity_id,
            form_params="&".join(f_params),
        )

        # Get FSM state context for the user
        state = self.dp.fsm.get_context(bot=self.bot, chat_id=user_id, user_id=user_id)
        state_data = await state.get_data()
        clear_state(state_data=state_data)
        stack = save_navigation_context(
            callback_data=callback_data, state_data=state_data
        )
        await state.set_data(state_data)

        # Fetch user object for locale and permissions
        user = await self.user_class.get(
            session=db_session,
            id=user_id,
        )

        # Use i18n context for the user's language
        with self.i18n.context(), self.i18n.use_locale(user.lang.value):
            await entity_item(
                query=None,
                db_session=db_session,
                callback_data=callback_data,
                app=self,
                user=user,
                navigation_stack=stack,
                state=state,
                state_data=state_data,
                i18n=self.i18n,
                app_state=app_state,
            )

    async def execute_command(
        self,
        app_state: State,
        command: str,
        user_id: int,
        db_session: AsyncSession,
    ):
        # --- Execute a user command in the Telegram bot context ---
        # This is used for programmatically triggering bot commands (e.g., from API or callback).
        state = self.dp.fsm.get_context(bot=self.bot, chat_id=user_id, user_id=user_id)
        state_data = await state.get_data()
        callback_data = ContextData(
            command=CallbackCommand.USER_COMMAND,
            user_command=command,
        )
        command_name = command.split("&")[0]
        cmd = self.bot_commands.get(command_name)

        # Fetch user object for permissions and locale
        user = await self.user_class.get(
            session=db_session,
            id=user_id,
        )

        if cmd is None:
            # Command not found (could be a custom or unregistered command)
            return

        # Optionally clear navigation stack if command requires it
        if cmd.clear_navigation:
            state_data.pop("navigation_stack", None)
            state_data.pop("navigation_context", None)

        # Optionally register navigation context for this command
        if cmd.register_navigation:
            clear_state(state_data=state_data)
            save_navigation_context(callback_data=callback_data, state_data=state_data)

        # Use i18n context for the user's language
        with self.i18n.context(), self.i18n.use_locale(user.lang.value):
            await command_handler(
                message=None,
                cmd=cmd,
                db_session=db_session,
                callback_data=callback_data,
                app=self,
                user=user,
                state=state,
                state_data=state_data,
                i18n=self.i18n,
                app_state=app_state,
            )
