from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="SEO Content API", version="1.0.0")

# CORS middleware (será configurado también en Azure)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"message": "Hello World from Azure!", "status": "running"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "FastAPI on Azure"}
