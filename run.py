import uvicorn
from fastapi import FastAPI

from api.config import settings
from api.handlers import router as jobs_rout

app = FastAPI(root_path=settings.api.root_path)
app.include_router(jobs_rout)



if __name__ == "__main__":
    uvicorn.run(app="run:app", host=settings.api.host, port=settings.api.port)
