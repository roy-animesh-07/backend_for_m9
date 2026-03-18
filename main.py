from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware

from backend_service import process_encounter_data, fetch_past_reports


app = FastAPI(
    title="Respiratory Diagnosis API",
    description="AI-powered respiratory disease prediction system",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Patient(BaseModel):
    PatientID: Optional[str] = None
    Name: Optional[str] = Field(None, example="John Doe")
    Age: Optional[int] = Field(None, ge=0, example=25)
    Gender: Optional[str] = Field(None, example="Male")


class Encounter(BaseModel):
    EncounterID: Optional[str] = None
    EncounterDate: Optional[str] = None


class Symptom(BaseModel):
    SymptomType: Optional[str] = Field(None, example="cough")
    Severity: Optional[str] = Field(None, example="high")


class Cough(BaseModel):
    CoughType: Optional[str] = Field(None, example="chronic")


class Breath(BaseModel):
    SoundType: Optional[str] = Field(None, example="wheeze")


class Smoking(BaseModel):
    SmokingStatus: Optional[str] = Field(None, example="current")


class Exposure(BaseModel):
    ExposureType: Optional[str] = Field(None, example="pollution")


class FullRequest(BaseModel):
    patient: Patient
    encounter: Encounter
    symptom: Symptom
    cough: Cough
    breath: Breath
    smoking: Smoking
    exposure: Exposure

@app.get("/")
def root():
    return {
        "message": "🚀 Respiratory Diagnosis API is running",
        "docs": "/docs"
    }


@app.post("/process", tags=["Diagnosis"])
def process_data(req: FullRequest):
    """
    Process full patient encounter and return disease probability
    """
    try:
        result = process_encounter_data(
            req.patient.dict(),
            req.encounter.dict(),
            req.symptom.dict(),
            req.cough.dict(),
            req.breath.dict(),
            req.smoking.dict(),
            req.exposure.dict()
        )

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/reports", tags=["Reports"])
def get_reports():
    """
    Fetch all past diagnosis reports
    """
    try:
        result = fetch_past_reports()

        if not result.get("success"):
            raise HTTPException(status_code=500, detail=result.get("message"))

        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "ok"}