import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from . import models, database
from .routers import users, events, registrations, admin

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI(
    title="Event Management API",
    description="A feature-rich API for managing events, registrations, and more.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(events.router)
app.include_router(registrations.router)
app.include_router(admin.router)

os.makedirs("frontend", exist_ok=True)
app.mount("/static", StaticFiles(directory="frontend"), name="static")

@app.get("/")
def read_root():
    index_path = os.path.join("frontend", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "Welcome to the Event Management API. Visit /docs for Swagger documentation."}
