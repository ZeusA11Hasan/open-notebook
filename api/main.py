from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.routers import notebooks, search, models, transformations, notes, embedding, settings, context, sources

app = FastAPI(
    title="Open Notebook API",
    description="API for Open Notebook - Research Assistant",
    version="0.2.2",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(notebooks.router, prefix="/api", tags=["notebooks"])
app.include_router(search.router, prefix="/api", tags=["search"])
app.include_router(models.router, prefix="/api", tags=["models"])
app.include_router(transformations.router, prefix="/api", tags=["transformations"])
app.include_router(notes.router, prefix="/api", tags=["notes"])
app.include_router(embedding.router, prefix="/api", tags=["embedding"])
app.include_router(settings.router, prefix="/api", tags=["settings"])
app.include_router(context.router, prefix="/api", tags=["context"])
app.include_router(sources.router, prefix="/api", tags=["sources"])

@app.get("/")
async def root():
    return {"message": "Open Notebook API is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}