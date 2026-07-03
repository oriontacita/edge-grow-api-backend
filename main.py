from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from app.database import engine, Base
from app.routers import auth, dashboard, toddlers, measurements, users, settings, sync

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# CUSTOM MIDDLEWARE: Override format error validasi bawaan FastAPI (422) agar sesuai docs
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"success": False, "message": "Validation error", "errors": exc.errors()},
    )

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    if hasattr(exc, "status_code"):
        status_code = exc.status_code
        detail = exc.detail if isinstance(exc.detail, dict) else {"success": False, "message": exc.detail, "data": None}
        return JSONResponse(status_code=status_code, content=detail)
    
    return JSONResponse(
        status_code=500, 
        content={"success": False, "message": "Internal Server Error", "data": None}
    )

# Register Routers
app.include_router(auth.router)
app.include_router(dashboard.router)
app.include_router(toddlers.router)
app.include_router(measurements.router)
app.include_router(users.router)
app.include_router(settings.router)
app.include_router(sync.router)

@app.get("/")
def root():
    return {"message": "Edge Grow Backend is running!"}