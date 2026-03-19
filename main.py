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
    DOB: Optional[str] = Field(None, example="2000-01-01")
    Gender: Optional[str] = Field(None, example="Male")


class Encounter(BaseModel):
    EncounterID: Optional[str] = None
    PatientID: Optional[str] = None
    EncounterDate: Optional[str] = Field(None, example="2026-03-18")
    EncounterType: Optional[str] = Field(None, example="Initial Visit")


class Symptom(BaseModel):
    EncounterID: Optional[str] = None
    SymptomType: Optional[str] = Field(None, example="cough")


class Cough(BaseModel):
    EncounterID: Optional[str] = None
    CoughType: Optional[str] = Field(None, example="chronic")


class Breath(BaseModel):
    EncounterID: Optional[str] = None
    Location: Optional[str] = Field(None, example="chest")
    SoundType: Optional[str] = Field(None, example="wheeze")
    Intensity: Optional[str] = Field(None, example="Normal")
    Pitch: Optional[str] = Field(None, example="Medium")


class Smoking(BaseModel):
    PatientID: Optional[str] = None
    SmokingStatus: Optional[str] = Field(None, example="current")
    PacksPerDay: Optional[float] = Field(None, example=1.0)
    YearsSmoked: Optional[float] = Field(None, example=5.0)
    QuitDate: Optional[str] = Field(None, example="2020-01-01")


class Exposure(BaseModel):
    PatientID: Optional[str] = None
    ExposureType: Optional[str] = Field(None, example="pollution")
    Duration: Optional[str] = Field(None, example="2 years")
    Setting: Optional[str] = Field(None, example="urban")


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


@app.get("/tables")
def get_all_tables():
    from database import get_db
    db = get_db()

    collections = {
        "Patients": "patients",
        "Encounters": "clinical_encounters",
        "Symptoms": "respiratory_symptoms",
        "Cough Data": "cough_characteristics",
        "Breath Sounds": "breath_sounds",
        "Smoking History": "smoking_histories",
        "Exposures": "environmental_exposures",
        "Probability Scores": "disease_probability_scores"
    }

    result = {}

    for title, name in collections.items():
        result[title] = list(db[name].find({}, {"_id": 0}))

    return {"success": True, "data": result}
@app.get("/health")
def health_check():
    return {"status": "ok"}
