"""
FastAPI Server for United LLM
HTTP API endpoints for structured LLM generation with search capabilities.
"""

import time
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import secrets
from starlette.middleware.sessions import SessionMiddleware
from pathlib import Path

# Import our modules
from ..client import LLMClient
from ..config import setup_united_llm_environment, get_config
from ..utils.database import LLMDatabase
from ..utils.model_manager import ModelManager

# Import schema utilities from string-schema package
import string_schema
from string_schema import json_schema_to_pydantic

# Define SchemaConversionError for backward compatibility
class SchemaConversionError(Exception):
    """Raised when schema conversion fails"""
    pass

# Import compatibility functions from main package
from .. import validate_json_schema, create_example_from_schema


from .schemas import (
    DictGenerationRequest,
    DictGenerationResponse,
    UnifiedGenerationRequest,
    ModelInfo,
    ModelsResponse,
    GroupedModelsResponse,
    HealthResponse,
    SchemaValidationRequest,
    SchemaValidationResponse,
    StringSchemaValidationRequest,
    StringSchemaValidationResponse,
    ErrorResponse,
    SearchTestRequest,
    SearchTestResponse,
    StatsResponse,
    SearchType,
)
from .admin import AdminInterface

# Initialize configuration at module level
setup_united_llm_environment()

# Setup Jinja2 templates
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


# Add custom filters for templates
def number_format(value):
    """Format numbers with commas"""
    if value is None:
        return "0"
    try:
        return f"{int(value):,}"
    except (ValueError, TypeError):
        return str(value)


templates.env.filters["number_format"] = number_format

# Global variables
llm_client: LLMClient = None
db: LLMDatabase = None
admin_interface = None
app_stats: Dict[str, Any] = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "response_times": [],
    "models_usage": {},
    "search_usage": {},
    "start_time": time.time(),
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup - Bootstrap already initialized at module level
    global llm_client, db, admin_interface

    # Create LLM client - it will get config from zero-config automatically
    # Server forces log_calls=True for all requests
    llm_client = LLMClient(config={"log_calls": True})

    # Initialize database if logging is enabled
    config = get_config()
    if config.get("log_to_db"):
        db_path = config.get_db_path()
        db = LLMDatabase(str(db_path))

    # Add admin interface initialization after the db initialization
    admin_interface = AdminInterface(db) if db else None

    logger = logging.getLogger(__name__)
    logger.info("United LLM API Server starting up...")
    logger.info("Zero-config loaded successfully")
    logger.info(f"Database path: {config.get_db_path()}")

    yield

    # Shutdown
    logger.info("United LLM API Server shutting down...")


# Create FastAPI app
app = FastAPI(
    title="United LLM API",
    description="United interface for LLM providers with search capabilities and structured outputs",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add session middleware for login
app.add_middleware(SessionMiddleware, secret_key=secrets.token_urlsafe(32))


def determine_search_type(
    enable_web_search: bool, model: str, legacy_search_type: Optional[SearchType] = None
) -> SearchType:
    """
    Determine the appropriate search type based on the enable_web_search flag and model.

    Args:
        enable_web_search: Boolean flag indicating if web search should be enabled
        model: The model name to determine the best search method
        legacy_search_type: Legacy search_type for backward compatibility

    Returns:
        SearchType enum value
    """
    # Handle legacy search_type for backward compatibility
    if legacy_search_type is not None:
        return legacy_search_type

    # If web search is disabled, return NONE
    if not enable_web_search:
        return SearchType.NONE

    # If web search is enabled, choose the best method based on model
    if model and (model.startswith("claude") or model.startswith("anthropic")):
        return SearchType.ANTHROPIC
    else:
        return SearchType.DUCKDUCKGO


def update_stats(success: bool, response_time: float, model: str = None, search_type: str = None):
    """Update application statistics"""
    app_stats["total_requests"] += 1
    if success:
        app_stats["successful_requests"] += 1
    else:
        app_stats["failed_requests"] += 1

    app_stats["response_times"].append(response_time)
    # Keep only last 1000 response times
    if len(app_stats["response_times"]) > 1000:
        app_stats["response_times"] = app_stats["response_times"][-1000:]

    if model:
        app_stats["models_usage"][model] = app_stats["models_usage"].get(model, 0) + 1

    if search_type:
        app_stats["search_usage"][search_type] = app_stats["search_usage"].get(search_type, 0) + 1


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger = logging.getLogger(__name__)
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)

    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="InternalServerError",
            message="An unexpected error occurred",
            details={"exception_type": type(exc).__name__},
        ).model_dump(),
    )


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    try:
        available_models = llm_client.get_available_models()

        # Get configured providers using model manager
        config = get_config()
        model_manager = ModelManager(config.to_dict())
        configured_providers = model_manager.get_configured_providers()

        return HealthResponse(
            status="healthy",
            version="1.0.0",
            timestamp=datetime.now(),
            configured_providers=configured_providers,
            available_models_count=len(available_models),
        )
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/dev/reload-status")
async def reload_status():
    """Development endpoint to check if server has reloaded"""
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat(),
        "reload_id": id(app),  # Changes when app reloads
    }


@app.get("/models", response_model=ModelsResponse)
async def get_models():
    """Get available models and their information"""
    try:
        available_models = llm_client.get_available_models()
        model_infos = []

        for model in available_models:
            if "ollama" in model.lower() and "dynamic models" in model.lower():
                # This is the fallback placeholder - get actual Ollama models
                ollama_models = llm_client.get_ollama_models()
                for ollama_model in ollama_models:
                    model_infos.append(
                        ModelInfo(
                            model_name=ollama_model,
                            provider="ollama",
                            configured=True,
                            supports_anthropic_web_search=False,
                            supports_duckduckgo_search=True,
                        )
                    )
            else:
                # Use model manager to detect provider safely
                try:
                    config = get_config()
                    model_manager = ModelManager(config.to_dict())
                    provider = model_manager.detect_model_provider(model)
                    if provider in ["openai", "anthropic", "google"]:
                        info = llm_client.get_model_info(model)
                        model_infos.append(
                            ModelInfo(
                                model_name=info["model_name"],
                                provider=info["provider"],
                                configured=info["configured"],
                                supports_anthropic_web_search=info.get("supports_anthropic_web_search", False),
                                supports_duckduckgo_search=info.get("supports_duckduckgo_search", True),
                                error=info.get("error"),
                            )
                        )
                    else:
                        # This is an Ollama model
                        model_infos.append(
                            ModelInfo(
                                model_name=model,
                                provider="ollama",
                                configured=True,
                                supports_anthropic_web_search=False,
                                supports_duckduckgo_search=True,
                            )
                        )
                except Exception as e:
                    # If provider detection fails, assume it's an Ollama model
                    model_infos.append(
                        ModelInfo(
                            model_name=model,
                            provider="ollama",
                            configured=True,
                            supports_anthropic_web_search=False,
                            supports_duckduckgo_search=True,
                        )
                    )

        # Get configured providers using model manager
        config = get_config()
        model_manager = ModelManager(config.to_dict())
        configured_providers = model_manager.get_configured_providers()

        return ModelsResponse(
            models=model_infos, default_model=config.get("default_model"), configured_providers=configured_providers
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@app.get("/models/grouped", response_model=GroupedModelsResponse)
async def get_models_grouped():
    """Get models grouped by provider with alphabetical sorting"""
    try:
        # Ensure client is initialized
        if llm_client is None:
            raise HTTPException(status_code=503, detail="LLM client not initialized")

        # Get models grouped by provider
        grouped_models = llm_client.get_models_grouped_by_provider()

        # Get configured providers using model manager
        config = get_config()
        model_manager = ModelManager(config.to_dict())
        configured_providers = model_manager.get_configured_providers()

        return GroupedModelsResponse(
            grouped_models=grouped_models,
            default_model=config.get("default_model"),
            configured_providers=configured_providers,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get grouped models: {str(e)}")


@app.post("/schema/validate", response_model=SchemaValidationResponse)
async def validate_schema(request: SchemaValidationRequest):
    """Validate a JSON schema and return validation results"""
    try:
        errors = validate_json_schema(request.json_schema)
        valid = len(errors) == 0

        example = None
        if valid:
            try:
                example = create_example_from_schema(request.json_schema)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to create example: {e}")

        return SchemaValidationResponse(valid=valid, errors=errors, example=example)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Schema validation failed: {str(e)}")


@app.post("/schema/validate-string", response_model=StringSchemaValidationResponse)
async def validate_string_schema_endpoint(request: StringSchemaValidationRequest):
    """Validate a string schema and return validation results with optimization"""
    try:
        validation = string_schema.validate_string_schema(request.schema_definition)

        # Generate the actual schema that would be used
        # Note: string-schema automatically handles arrays with [] syntax, no is_list flag needed
        actual_schema = None
        if validation["valid"]:
            try:
                # Handle array format if is_list is requested but not in schema
                schema_def = request.schema_definition
                if request.is_list and not schema_def.strip().startswith("["):
                    schema_def = f"[{schema_def}]"
                actual_schema = string_schema.parse_string_schema(schema_def)
            except Exception as e:
                logger = logging.getLogger(__name__)
                logger.warning(f"Failed to generate actual schema: {e}")

        # For optimization, just return the original string (string-schema doesn't have optimize function)
        optimized = request.schema_definition if validation["valid"] else None

        return StringSchemaValidationResponse(
            valid=validation["valid"],
            errors=validation["errors"] + validation.get("warnings", []),  # Include warnings as errors for UI
            parsed_fields=validation["parsed_fields"],
            generated_schema=actual_schema or validation["generated_schema"],
            optimized_string=optimized,
        )
    except Exception as e:
        return StringSchemaValidationResponse(valid=False, errors=[f"Validation failed: {str(e)}"])


@app.post("/schema/generate-code")
async def generate_pydantic_code(request: dict):
    """Generate Pydantic model code from string schema"""
    try:
        schema_definition = request.get("schema_definition", "")
        model_name = request.get("model_name", "GeneratedModel")

        if not schema_definition:
            raise HTTPException(status_code=400, detail="schema_definition is required")

        # Validate schema first
        validation = string_schema.validate_string_schema(schema_definition)
        if not validation["valid"]:
            raise HTTPException(status_code=400, detail=f"Invalid schema: {', '.join(validation['errors'])}")

        # Generate Pydantic code
        pydantic_code = string_schema.string_to_pydantic_code(schema_definition, model_name)

        # Also generate OpenAPI schema for reference
        openapi_schema = string_schema.string_to_openapi(schema_definition)

        return {
            "success": True,
            "pydantic_code": pydantic_code,
            "openapi_schema": openapi_schema,
            "features_used": validation["features_used"],
            "model_name": model_name,
        }

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/schema/convert")
async def convert_schema(request: dict):
    """Convert between string schema and JSON schema formats"""
    try:
        schema_input = request.get("schema", "")
        target_format = request.get("target_format", "")  # "string" or "json"

        if not schema_input:
            raise HTTPException(status_code=400, detail="schema is required")

        if target_format not in ["string", "json"]:
            raise HTTPException(status_code=400, detail="target_format must be 'string' or 'json'")

        if target_format == "json":
            # Convert string schema to JSON schema
            try:
                json_schema = string_schema.parse_string_schema(schema_input)
                return {
                    "success": True,
                    "converted_schema": json_schema,
                    "original_format": "string",
                    "target_format": "json"
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid string schema: {str(e)}")

        else:  # target_format == "string"
            # Convert JSON schema to string schema
            try:
                # Parse JSON if it's a string
                if isinstance(schema_input, str):
                    import json
                    json_schema = json.loads(schema_input)
                else:
                    json_schema = schema_input

                string_schema_result = string_schema.json_schema_to_string(json_schema)
                return {
                    "success": True,
                    "converted_schema": string_schema_result,
                    "original_format": "json",
                    "target_format": "string"
                }
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON schema: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        return {"success": False, "error": str(e)}


@app.post("/generate/dict", response_model=DictGenerationResponse)
async def generate_dict(request: DictGenerationRequest, background_tasks: BackgroundTasks):
    """
    Generate structured output as plain Python dictionaries using string schemas.

    NEW: Supports JSON-consistent curly brace syntax!

    Features:
    - {name, age:int, email?} - Single objects
    - [{name, email}] - Arrays of objects
    - {team, members:[{name, role}]} - Nested structures
    - [string] - Simple arrays
    - Legacy formats still supported for backward compatibility

    Returns plain Python dictionaries instead of Pydantic models.
    Perfect for web APIs, JSON serialization, and simple data processing.
    """
    start_time = time.time()
    model_used = request.model or get_config().get("default_model")
    search_used = request.search_type.value if request.search_type != SearchType.NONE else None

    try:
        # Validate string schema
        try:
            json_schema = string_schema.parse_string_schema(request.schema_definition)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid string schema: {str(e)}")

        # Configure search
        anthropic_search = request.search_type == SearchType.ANTHROPIC
        duckduckgo_search = request.search_type == SearchType.DUCKDUCKGO

        # Generate using the generate_dict method with optional fallback
        result = llm_client.generate_dict(
            prompt=request.prompt,
            schema=request.schema_definition,
            model=model_used,
            temperature=request.temperature,
            max_retries=request.max_retries,
            anthropic_web_search=anthropic_search,
            duckduckgo_search=duckduckgo_search,
            fallback_models=request.fallback_models,
        )

        generation_time = time.time() - start_time

        # Update stats in background
        background_tasks.add_task(update_stats, True, model_used, search_used)

        return DictGenerationResponse(
            success=True,
            data=result,
            model_used=model_used,
            search_used=search_used,
            generation_time=generation_time,
            schema_used=json_schema,
            string_schema=request.schema_definition,
        )

    except HTTPException:
        raise
    except Exception as e:
        generation_time = time.time() - start_time
        background_tasks.add_task(update_stats, False, model_used, search_used)

        logger = logging.getLogger(__name__)
        logger.error(f"Dict generation failed: {str(e)}", exc_info=True)

        return DictGenerationResponse(
            success=False, generation_time=generation_time, error=str(e), string_schema=request.schema_definition
        )


@app.post("/search/test", response_model=SearchTestResponse)
async def test_search(request: SearchTestRequest):
    """Test search functionality with a query"""
    start_time = time.time()

    try:
        if request.search_type == SearchType.ANTHROPIC:
            # Test Anthropic search
            from ..search.anthropic_search import AnthropicSearch

            search_handler = AnthropicSearch(api_key=get_config().get("anthropic_api_key"), llm_client=llm_client)

            # Simple query optimization test
            optimized = f"Search for: {request.query}"

            # Attempt search
            results = search_handler.search(optimized)

            return SearchTestResponse(
                success=True,
                search_type=request.search_type.value,
                query_used=optimized,
                results_count=len(results) if isinstance(results, list) else 1,
                processing_time=time.time() - start_time,
            )

        elif request.search_type == SearchType.DUCKDUCKGO:
            # Test DuckDuckGo search
            from ..search.duckduckgo_search import DuckDuckGoSearch

            search_handler = DuckDuckGoSearch(llm_client=llm_client)

            # Test query optimization
            model = request.model or get_config().get("default_model")
            optimized = search_handler._optimize_search_query(request.query, model)

            # Attempt search
            results = search_handler.search(optimized)

            return SearchTestResponse(
                success=True,
                search_type=request.search_type.value,
                query_used=optimized,
                results_count=len(results) if isinstance(results, list) else 1,
                processing_time=time.time() - start_time,
            )
        else:
            raise HTTPException(status_code=400, detail="Invalid search type")

    except Exception as e:
        search_time = time.time() - start_time
        return SearchTestResponse(success=False, search_time=search_time, error=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get API usage statistics"""
    try:
        uptime = time.time() - app_stats["start_time"]
        avg_response_time = (
            sum(app_stats["response_times"]) / len(app_stats["response_times"]) if app_stats["response_times"] else 0.0
        )

        return StatsResponse(
            total_requests=app_stats["total_requests"],
            successful_requests=app_stats["successful_requests"],
            failed_requests=app_stats["failed_requests"],
            average_response_time=avg_response_time,
            models_usage=app_stats["models_usage"],
            search_usage=app_stats["search_usage"],
            uptime_seconds=uptime,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")


# Session-based admin authentication
def authenticate_admin(request: Request):
    """Authenticate admin user via session"""
    if not request.session.get("admin_authenticated"):
        # Redirect to login page instead of raising HTTPException
        raise HTTPException(status_code=302, detail="Not authenticated", headers={"Location": "/login"})
    return request.session.get("admin_username", "admin")


# Login endpoints
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request, error: str = None):
    """Display login page"""
    # If already authenticated, redirect to dashboard
    if request.session.get("admin_authenticated"):
        return RedirectResponse(url="/", status_code=302)

    if not admin_interface:
        raise HTTPException(status_code=503, detail="Database logging not enabled")

    return templates.TemplateResponse("login.html", {"request": request, "error": error})


@app.post("/admin/login", response_class=HTMLResponse)
async def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    """Handle login form submission"""
    # Use config for admin credentials
    config = get_config()
    admin_username = config.get("admin_username")
    admin_password = config.get("admin_password")

    correct_username = secrets.compare_digest(username, admin_username)
    correct_password = secrets.compare_digest(password, admin_password)

    if correct_username and correct_password:
        # Set session
        request.session["admin_authenticated"] = True
        request.session["admin_username"] = username
        return RedirectResponse(url="/", status_code=302)
    else:
        # Redirect back to login with error
        return RedirectResponse(url="/login?error=Invalid+credentials", status_code=302)


@app.post("/admin/logout")
@app.get("/admin/logout")
async def logout(request: Request):
    """Logout and clear session"""
    request.session.clear()
    return RedirectResponse(url="/login", status_code=302)


@app.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request, admin_user: str = Depends(authenticate_admin)):
    """Enhanced admin dashboard with comprehensive statistics"""
    if not admin_interface:
        raise HTTPException(status_code=503, detail="Database logging not enabled")

    # Get dashboard data
    stats = db.get_stats()
    provider_stats = db.get_provider_stats()
    top_models = db.get_top_models(limit=5)
    search_requests_count = db.get_search_requests_count()

    # Add additional stats that the template expects
    from datetime import timedelta

    now = datetime.now()

    # Get hour and week stats
    hour_ago = now - timedelta(hours=1)
    week_ago = now - timedelta(days=7)

    hour_calls = db.get_total_calls_count()  # Simplified for now
    week_calls = db.get_total_calls_count()  # Simplified for now

    # Add missing stats to the stats dict
    stats["hour_calls"] = hour_calls if hour_calls < stats["total_calls"] else 0
    stats["week_calls"] = week_calls if week_calls < stats["total_calls"] else stats["total_calls"]
    stats["avg_duration_ms"] = 1500  # Default value for now
    stats["total_tokens_used"] = 50000  # Default value for now
    stats["avg_tokens_per_call"] = 100  # Default value for now

    # Get model display names and format for modal using grouped models (proper provider ordering)
    model_display_names = {}
    modal_models = []

    # Get models grouped by provider
    grouped_models = llm_client.get_models_grouped_by_provider()
    default_model = get_config().get("default_model")

    # Add models in the desired order: anthropic, google, openai, ollama
    provider_order = ["anthropic", "google", "openai", "ollama"]

    for provider in provider_order:
        if provider in grouped_models:
            models = grouped_models[provider]
            for model in models:
                display_name = f"{model} ({provider})"
                model_display_names[model] = display_name
                modal_models.append({"id": model, "display_name": display_name, "selected": model == default_model})

    # Calculate max counts for progress bars
    max_provider_count = max(provider_stats.values()) if provider_stats else 1
    max_model_count = max([count for _, count in top_models]) if top_models else 1

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "stats": stats,
            "provider_stats": provider_stats,
            "top_models": top_models,
            "search_requests_count": search_requests_count,
            "model_display_names": model_display_names,
            "max_provider_count": max_provider_count,
            "max_model_count": max_model_count,
            "available_models": modal_models,
        },
    )


@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard_redirect(request: Request, admin_user: str = Depends(authenticate_admin)):
    """Redirect /admin to the main dashboard"""
    return RedirectResponse(url="/", status_code=302)


@app.get("/admin/llm_calls", response_class=HTMLResponse)
async def admin_llm_calls_redirect(request: Request, admin_user: str = Depends(authenticate_admin)):
    """Redirect old /admin/llm_calls to new /admin/requests"""
    # Preserve query parameters
    query_string = str(request.url.query)
    redirect_url = "/admin/requests"
    if query_string:
        redirect_url += f"?{query_string}"
    return RedirectResponse(url=redirect_url, status_code=301)


@app.get("/admin/export/csv")
async def export_csv(request: Request, limit: int = 1000, admin_user: str = Depends(authenticate_admin)):
    """Export LLM calls to CSV format"""
    if not admin_interface:
        raise HTTPException(status_code=503, detail="Database logging not enabled")

    return admin_interface.export_to_csv(limit=limit)


@app.get("/admin/export/json")
async def export_json(request: Request, limit: int = 1000, admin_user: str = Depends(authenticate_admin)):
    """Export LLM calls to JSON format"""
    if not admin_interface:
        raise HTTPException(status_code=503, detail="Database logging not enabled")

    return admin_interface.export_to_json(limit=limit)


@app.get("/admin/models")
async def get_admin_models(admin_user: str = Depends(authenticate_admin)):
    """Get available models for admin interface"""
    try:
        # Get configured providers using model manager
        config = get_config()
        model_manager = ModelManager(config.to_dict())
        configured_providers = model_manager.get_configured_providers()

        # Get models grouped by provider (proper ordering)
        grouped_models = llm_client.get_models_grouped_by_provider()

        # Format models for frontend in the desired order: anthropic, google, openai, ollama
        model_infos = []
        provider_order = ["anthropic", "google", "openai", "ollama"]

        for provider in provider_order:
            if provider in grouped_models:
                models = grouped_models[provider]
                for model in models:
                    model_infos.append({"name": model, "provider": provider})

        return {
            "models": model_infos,
            "default_model": config.get("default_model"),
            "configured_providers": configured_providers,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get models: {str(e)}")


@app.get("/admin/requests", response_class=HTMLResponse)
async def admin_llm_calls(
    request: Request,
    page: int = 1,
    limit: int = 50,
    model: str = None,
    provider: str = None,
    search_type: str = None,
    status: str = None,
    admin_user: str = Depends(authenticate_admin),
):
    """Enhanced admin interface for viewing LLM call history"""
    if not db:
        raise HTTPException(status_code=503, detail="Database logging not enabled")

    try:
        offset = (page - 1) * limit
        calls = db.get_calls(limit=limit, offset=offset, model=model, provider=provider, search_type=search_type)

        # Get total count for pagination
        total_count = db.get_total_calls_count(model=model, provider=provider, search_type=search_type)
        total_pages = (total_count + limit - 1) // limit

        # Get available options for filters
        available_providers = db.get_available_providers()

        # Format models for display using grouped models (proper provider ordering)
        model_options = []
        grouped_models = llm_client.get_models_grouped_by_provider()

        # Add models in the desired order: anthropic, google, openai, ollama
        provider_order = ["anthropic", "google", "openai", "ollama"]

        for provider in provider_order:
            if provider in grouped_models:
                models = grouped_models[provider]
                for model in models:
                    display_name = f"{model} ({provider})"
                    model_options.append({"id": model, "display_name": display_name})

        # Get model display names for the table using grouped models
        model_display_names = {}
        for provider, models in grouped_models.items():
            for model in models:
                model_display_names[model] = f"{model} ({provider})"

        # Build filter params for pagination links
        filter_params = ""
        if provider:
            filter_params += f"&provider={provider}"
        if model:
            filter_params += f"&model={model}"
        if search_type:
            filter_params += f"&search_type={search_type}"
        if status:
            filter_params += f"&status={status}"

        return templates.TemplateResponse(
            "request_history.html",
            {
                "request": request,
                "requests": calls,
                "page": page,
                "per_page": limit,
                "total_count": total_count,
                "total_pages": total_pages,
                "available_providers": available_providers,
                "available_models": model_options,
                "model_display_names": model_display_names,
                "current_filters": {"provider": provider, "model": model, "search_type": search_type, "status": status},
                "filter_params": filter_params,
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load LLM calls: {str(e)}")


@app.get("/admin/requests/{request_id}")
async def get_llm_call_details(request_id: int, admin_user: str = Depends(authenticate_admin)):
    """Get detailed information about a specific LLM call"""
    if not db:
        raise HTTPException(status_code=503, detail="Database logging not enabled")

    try:
        call = db.get_call_by_id(request_id)
        if not call:
            raise HTTPException(status_code=404, detail="Request not found")

        # Convert to dict and handle JSON fields
        call_dict = {
            "id": call.id,
            "timestamp": call.timestamp.isoformat(),
            "model": call.model,
            "provider": call.provider,
            "prompt": call.prompt,
            "response": call.response,
            "token_usage": call.token_usage,
            "error": call.error,
            "duration_ms": call.duration_ms,
            "search_type": call.search_type,
            "request_schema": call.request_schema,
        }

        return call_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get call details: {str(e)}")


@app.post("/generate/united", response_model=DictGenerationResponse)
async def generate_united(request: UnifiedGenerationRequest, background_tasks: BackgroundTasks):
    """
    United generation endpoint that accepts both JSON Schema and string schema definitions.

    Auto-detects schema type:
    - Dict/object → JSON Schema processing
    - String → String schema processing (supports all formats: simple, curly brace, arrays)

    Returns plain Python dictionaries for maximum compatibility.
    """
    start_time = time.time()
    model_used = request.model or get_config().get("default_model")

    # Determine search type using the new boolean field or legacy search_type
    search_type = determine_search_type(request.enable_web_search, model_used, request.search_type)
    search_used = search_type.value if search_type != SearchType.NONE else None

    try:
        # Initialize variables for error handling
        string_schema_used = None

        # Auto-detect schema type and process accordingly
        if request.is_json_schema():
            # Handle JSON Schema
            json_schema = request.get_json_schema()

            # Validate JSON Schema
            schema_errors = validate_json_schema(json_schema)
            if schema_errors:
                raise HTTPException(status_code=400, detail=f"Invalid JSON schema: {schema_errors}")

            # Convert to Pydantic model
            try:
                output_model = json_schema_to_pydantic(json_schema, "UnitedOutputModel")
            except SchemaConversionError as e:
                raise HTTPException(status_code=400, detail=f"Schema conversion failed: {str(e)}")

            # Generate using structured generation with optional fallback
            result = llm_client.generate_structured(
                prompt=request.prompt,
                output_model=output_model,
                model=model_used,
                temperature=request.temperature,
                max_retries=request.max_retries,
                enable_web_search=request.enable_web_search,
                fallback_models=request.fallback_models,
            )
            # Convert Pydantic result to dict
            result_data = result.model_dump()

            schema_used = json_schema
            string_schema_used = None

        else:
            # Handle string schema
            schema_definition = request.get_schema_definition()

            # Validate string schema
            try:
                # Handle array format if is_list is requested but not in schema
                if request.is_list and not schema_definition.strip().startswith("["):
                    schema_definition = f"[{schema_definition}]"
                json_schema = string_schema.parse_string_schema(schema_definition)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid string schema: {str(e)}")

            # Generate using the generate_dict method for string schemas with optional fallback
            result_data = llm_client.generate_dict(
                prompt=request.prompt,
                schema=schema_definition,
                model=model_used,
                temperature=request.temperature,
                max_retries=request.max_retries,
                enable_web_search=request.enable_web_search,
                fallback_models=request.fallback_models,
            )

            schema_used = json_schema
            string_schema_used = schema_definition

        generation_time = time.time() - start_time

        # Update stats in background
        background_tasks.add_task(update_stats, True, generation_time, model_used, search_used)

        return DictGenerationResponse(
            success=True,
            data=result_data,
            model_used=model_used,
            search_used=search_used,
            generation_time=generation_time,
            schema_used=schema_used,
            string_schema=string_schema_used,
        )

    except HTTPException:
        raise
    except Exception as e:
        generation_time = time.time() - start_time
        background_tasks.add_task(update_stats, False, generation_time, model_used, search_used)

        logger = logging.getLogger(__name__)
        logger.error(f"United generation failed: {str(e)}", exc_info=True)

        return DictGenerationResponse(
            success=False,
            generation_time=generation_time,
            error=str(e),
            string_schema=string_schema_used if not request.is_json_schema() else None,
        )


def main():
    """Main entry point for the console script"""
    import uvicorn

    # Initialize configuration system
    setup_united_llm_environment()
    config = get_config()

    uvicorn.run(
        "united_llm.api.server:app",
        host=config.get("api_host", "0.0.0.0"),
        port=config.get("api_port", 8818),
        reload=False,
        log_level="info",
    )


if __name__ == "__main__":
    main()
