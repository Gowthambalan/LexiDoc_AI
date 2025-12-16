from fastapi import FastAPI
from app.db.database import engine
from app.db.models import Base

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.get("/")
def root():
    return {"status": "DB Connected & Tables Created"}


from app.routers import user

app.include_router(user.router)
