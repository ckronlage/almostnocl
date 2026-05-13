"""
FastAPI backend for MELD GUI – neuroimaging processing web application.
"""
import uuid
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from app.processing import load_nifti, apply_threshold, get_data_range

# ---------------------------------------------------------------------------
# Directory layout
# ---------------------------------------------------------------------------
BASE_DIR = Path(__file__).parent.parent
UPLOAD_DIR = BASE_DIR / "uploads"
OUTPUT_DIR = BASE_DIR / "outputs"
UPLOAD_DIR.mkdir(exist_ok=True)
OUTPUT_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# App setup
# ---------------------------------------------------------------------------
app = FastAPI(title="MELD GUI", version="0.1.0")

app.mount("/static", StaticFiles(directory=str(BASE_DIR / "app" / "static")), name="static")
app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")
app.mount("/outputs", StaticFiles(directory=str(OUTPUT_DIR)), name="outputs")

templates = Jinja2Templates(directory=str(BASE_DIR / "app" / "templates"))


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": exc.errors()})


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.get("/")
async def index(request: Request):
    response = templates.TemplateResponse("index.html", {"request": request})
    response.headers["Cache-Control"] = "no-store"
    return response


@app.post("/api/upload")
async def upload_nifti(file: UploadFile = File(...)):
    """Accept a NIfTI file (.nii or .nii.gz), return file ID and intensity range."""
    filename = file.filename or ""
    if not (filename.endswith(".nii") or filename.endswith(".nii.gz")):
        raise HTTPException(status_code=400, detail="Only .nii or .nii.gz files are supported.")

    file_id = str(uuid.uuid4())
    suffix = ".nii.gz" if filename.endswith(".nii.gz") else ".nii"
    save_path = UPLOAD_DIR / f"{file_id}{suffix}"

    with open(save_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    try:
        img = load_nifti(str(save_path))
        info = get_data_range(img)
    except Exception as exc:
        save_path.unlink(missing_ok=True)
        raise HTTPException(status_code=422, detail=f"Could not read NIfTI file: {exc}")

    return JSONResponse({
        "file_id": file_id,
        "filename": filename,
        "upload_file": save_path.name,
        "info": info,
    })


@app.post("/api/process/{file_id}")
async def process_nifti(file_id: str, lower: float = 0.0, upper: float = 1e6):
    """Apply intensity thresholding and return output filename for viewing/download."""
    # Locate uploaded file
    nii_path = _find_upload(file_id)
    if nii_path is None:
        raise HTTPException(status_code=404, detail="File not found. Please re-upload.")

    try:
        img = load_nifti(str(nii_path))
        result = apply_threshold(img, lower, upper)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Processing error: {exc}")

    # Save output
    out_filename = f"{file_id}_thresholded.nii.gz"
    out_path = OUTPUT_DIR / out_filename
    import nibabel as nib
    nib.save(result, str(out_path))

    return JSONResponse({
        "file_id": file_id,
        "output_file": out_filename,
    })


@app.get("/api/download/{filename}")
async def download_output(filename: str):
    """Download a processed output file."""
    # Sanitise: only allow filenames without path traversal
    if "/" in filename or ".." in filename:
        raise HTTPException(status_code=400, detail="Invalid filename.")
    out_path = OUTPUT_DIR / filename
    if not out_path.exists():
        raise HTTPException(status_code=404, detail="Output file not found.")
    return FileResponse(str(out_path), media_type="application/gzip", filename=filename)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _find_upload(file_id: str) -> Path | None:
    for suffix in (".nii.gz", ".nii"):
        p = UPLOAD_DIR / f"{file_id}{suffix}"
        if p.exists():
            return p
    return None
