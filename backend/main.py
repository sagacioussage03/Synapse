from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import hardware, system, alarm

app = FastAPI(title="Project Synapse - Control Core")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Bring in the routes!
app.include_router(hardware.router)
app.include_router(system.router)
app.include_router(alarm.router)

@app.get("/")
def read_root():
    return {"status": "Synapse Core is Online"}