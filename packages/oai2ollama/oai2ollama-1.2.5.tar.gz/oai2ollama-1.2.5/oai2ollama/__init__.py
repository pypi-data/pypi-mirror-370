from ._app import app
from .config import env


def start():
    import uvicorn

    uvicorn.run(app, host=env.host, port=11434)


__all__ = ["app", "start"]
