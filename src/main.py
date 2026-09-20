from fastapi import FastAPI, Form
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from src.auth import router as auth_router

app = FastAPI()

app.add_middleware(
    SessionMiddleware,
    secret_key="dev-secret-2604",
    https_only=False,   # False for local testing only
    same_site="lax",
)
app.include_router(auth_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory "database" - a simple list of dicts
records = [
    {"id": 1, "packageName": "lodash", "affectedVersion": "4.17.15", "emailId": "seed@example.com", "description": "Seed record for testing update/delete.", "severity": "High"},
]
next_id = 2

@app.get("/api/records")
def list_records(q: str = ""):
    if q:
        q_lower = q.lower()
        filtered = [r for r in records if q_lower in r["packageName"].lower() or q_lower in r["affectedVersion"].lower()]
        return filtered
    return records

@app.post("/api/records")
def add_record(
    packageName: str = Form(...),
    affectedVersion: str = Form(...),
    emailId: str = Form(...),
    description: str = Form(...),
    severity: str = Form(...)
):
    global next_id
    new_record = {
        "id": next_id,
        "packageName": packageName,
        "affectedVersion": affectedVersion,
        "emailId": emailId,
        "description": description,
        "severity": severity
    }
    records.append(new_record)
    next_id += 1
    return RedirectResponse(url="/", status_code=303)

@app.post("/api/records/1/update")
def update_record_1(
    packageName: str = Form(...),
    affectedVersion: str = Form(...)
):
    for r in records:
        if r["id"] == 1:
            r["packageName"] = packageName
            r["affectedVersion"] = affectedVersion
    return RedirectResponse(url="/", status_code=303)

@app.post("/api/records/delete-highest")
def delete_highest():
    if records:
        highest = max(records, key=lambda r: r["id"])
        records.remove(highest)
    return RedirectResponse(url="/", status_code=303)

app.mount("/", StaticFiles(directory=".", html=True), name="static")