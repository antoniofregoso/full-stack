import uvicorn
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import strawberry
from sqlalchemy.sql import text

from config import db

from app.Graphql.schema import Query, Mutation
from app.core.service.core_bootstrap import (
    seed_auth_permissions,
    seed_auth_roles,
    seed_auth_role_permissions,
    seed_auth_users,
    seed_core_countries,
    seed_core_currencies,
    seed_core_langs,
    seed_core_pages,
    seed_core_systems,
    seed_core_user_assignments,
)

from strawberry.fastapi import GraphQLRouter
from logging_config import configure_logging, get_logger

# Configurar logging al inicio
configure_logging()
logger = get_logger(__name__)

def init_app():
    apps = FastAPI(
        title="API",
        description="API description",
        version="0.0.1",
    )

    apps.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Allows all origins
        allow_credentials=True,
        allow_methods=["*"],  # Allows all methods
        allow_headers=["*"],  # Allows all headers
    )

    @apps.on_event("startup")
    async def startup():
        logger.info("Starting application and connecting to database...")
        # await db.create_all()
        await seed_auth_users()
        await seed_auth_roles()
        await seed_auth_permissions()
        await seed_auth_role_permissions()
        await seed_core_langs()
        await seed_core_currencies()
        await seed_core_countries()
        await seed_core_pages()
        await seed_core_systems()
        await seed_core_user_assignments()

    @apps.on_event("shutdown")
    async def shutdown():
        logger.info("Closing database connection...")
        await db.close()

    @apps.get("/")
    def root():
        return {"message": "Hello World"}

    @apps.get("/health")
    async def health_check():
        try:
            async with db as session:
                await session.execute(text("SELECT 1"))
            return {"status": "healthy", "database": "online"}
        except Exception as e:
            return JSONResponse(
                status_code=503,
                content={"status": "unhealthy", "database": "offline", "error": str(e)}
            )
    
    schema = strawberry.Schema(query=Query, mutation=Mutation)
    graphql_app = GraphQLRouter(schema)
    
    apps.include_router(graphql_app, prefix="/graphql")

    return apps

app = init_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host="localhost", port=8000, reload=True)
