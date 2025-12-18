# from fastapi import FastAPI
# from app.db.database import engine
# from app.db.models import Base

# app = FastAPI()

# Base.metadata.create_all(bind=engine)

# @app.get("/")
# def root():
#     return {"status": "DB Connected & Tables Created"}


# from app.routers import user

# app.include_router(user.router)


# from fastapi import FastAPI
# from app.db.database import engine
# from app.db.models import Base
# from app.routers import user

# app = FastAPI()


# app.include_router(user.router)

# @app.get("/")
# def root():
#     return {"status": "DB Connected & Tables Created"}

from fastapi import FastAPI
from app.routers import user
from app.routers import upload
from app.routers import chat
from app.routers import dashboard

app = FastAPI()

app.include_router(user.router)
app.include_router(upload.router)
app.include_router(chat.router)
app.include_router(dashboard.router)

@app.get("/")
def root():
    return {"status": "API Running"}
