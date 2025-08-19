import uvicorn

from .settings import settings

if __name__ == "__main__":
    uvicorn.run(
        "llama_deploy.appserver.app:app",
        host=settings.host,
        port=settings.port,
    )
