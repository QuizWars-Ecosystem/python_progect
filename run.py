import uvicorn
from fastapi import FastAPI

from api.config import settings

app = FastAPI(root_path=settings.api.root_path)



if __name__ == "__main__":
    uvicorn.run(app="run:app", host=settings.api.host, port=settings.api.port)
