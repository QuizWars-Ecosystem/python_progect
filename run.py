import uvicorn
from fastapi import FastAPI

from config import settings

app = FastAPI(root_path="/api")



if __name__ == "__main__":
    uvicorn.run(app="run:app", host=settings.run.host, port=settings.run.port)
