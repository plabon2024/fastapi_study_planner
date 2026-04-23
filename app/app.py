from fastapi import FastAPI
from starlette.exceptions import HTTPException 
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.config.config import getAppConfig

# Import all models to register them with SQLAlchemy
from app.db.base import Base, User, Subject, Plan, StudySession, Progress

from app.api.routes import auth
app = FastAPI()


# all routes
app.include_router(auth.router, prefix="/api")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    errors = {}
    for error in exc.errors():
        print(f"The error is: {error}")
        errors[error["loc"][-1]] = error["msg"]

    return JSONResponse(
        {"message": "Validation Error", "errors": errors}, status_code=422
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    if exc.status_code == 404:
        return JSONResponse(
            {
                "message": "Route not found",
                "path": request.url.path,
            },
            status_code=404,
        )

    return JSONResponse(
        {"message": exc.detail},
        status_code=exc.status_code,
    )

@app.get("/")
def root():
    config = getAppConfig()
    return {
        "message": "Hello, FastAPI",
        "app_name": config.app_name,
        "app_env": config.app_env,
        "database_url": config.database_url,
    }
