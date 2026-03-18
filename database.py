from pymongo import MongoClient
import os
import uuid
from datetime import datetime
from dotenv import load_dotenv
import certifi

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "respiratory_diagnosis_db"

client = MongoClient(MONGO_URI, tlsCAFile=certifi.where())
db = client[DB_NAME]

def get_db():
    return db

def insert_patient(patient_data: dict) -> str:
    # Generates ID if not provided, else uses provided
    if "PatientID" not in patient_data:
        patient_data["PatientID"] = str(uuid.uuid4())
    db.patients.update_one(
        {"PatientID": patient_data["PatientID"]}, 
        {"$set": patient_data}, 
        upsert=True
    )
    return patient_data["PatientID"]

def insert_encounter(encounter_data: dict) -> str:
    if "EncounterID" not in encounter_data:
        encounter_data["EncounterID"] = str(uuid.uuid4())
    if "EncounterDate" not in encounter_data:
        encounter_data["EncounterDate"] = datetime.now()
    db.clinical_encounters.insert_one(encounter_data)
    return encounter_data["EncounterID"]

def insert_symptom(symptom_data: dict) -> str:
    if "SymptomID" not in symptom_data:
        symptom_data["SymptomID"] = str(uuid.uuid4())
    db.respiratory_symptoms.insert_one(symptom_data)
    return symptom_data["SymptomID"]

def insert_cough_characteristic(cough_data: dict) -> str:
    if "CharacteristicID" not in cough_data:
        cough_data["CharacteristicID"] = str(uuid.uuid4())
    db.cough_characteristics.insert_one(cough_data)
    return cough_data["CharacteristicID"]

def insert_breath_sound(sound_data: dict) -> str:
    if "SoundID" not in sound_data:
        sound_data["SoundID"] = str(uuid.uuid4())
    db.breath_sounds.insert_one(sound_data)
    return sound_data["SoundID"]

def update_smoking_history(smoking_data: dict) -> str:
    if "HistoryID" not in smoking_data:
        smoking_data["HistoryID"] = str(uuid.uuid4())
    # According to DFD this is an UPDATE, tying it to patient
    db.smoking_histories.update_one(
        {"HistoryID": smoking_data.get("HistoryID")},
        {"$set": smoking_data},
        upsert=True
    )
    return smoking_data["HistoryID"]

def update_environmental_exposure(exposure_data: dict) -> str:
    # According to DFD this is an UPDATE
    patient_id = exposure_data.get("PatientID")
    db.environmental_exposures.update_one(
        {"PatientID": patient_id}, # Assuming one exposure record per patient for simplicity or updating based on PatientID
        {"$set": exposure_data},
        upsert=True
    )
    return "updated"

def insert_or_update_disease_score(score_data: dict) -> str:
    if "ScoreID" not in score_data:
        score_data["ScoreID"] = str(uuid.uuid4())
    db.disease_probability_scores.update_one(
        {"EncounterID": score_data.get("EncounterID")},
        {"$set": score_data},
        upsert=True
    )
    return score_data["ScoreID"]

def get_all_reports() -> list:
    pipeline = [
        {
            "$lookup": {
                "from": "clinical_encounters",
                "localField": "EncounterID",
                "foreignField": "EncounterID",
                "as": "encounter"
            }
        },
        {
            "$unwind": {
                "path": "$encounter",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$lookup": {
                "from": "patients",
                "localField": "encounter.PatientID",
                "foreignField": "PatientID",
                "as": "patient"
            }
        },
        {
            "$unwind": {
                "path": "$patient",
                "preserveNullAndEmptyArrays": True
            }
        },
        {
            "$project": {
                "_id": 0,
                "ScoreID": 1,
                "EncounterID": 1,
                "TargetDisease": 1,
                "ProbabilityScore": 1,
                "RiskLevel": 1,
                "AlgorithmVersion": 1,
                "EncounterDate": "$encounter.EncounterDate",
                "PatientName": "$patient.Name",
                "PatientID": "$patient.PatientID"
            }
        },
        {
            "$sort": {"EncounterDate": -1}
        }
    ]
    return list(db.disease_probability_scores.aggregate(pipeline))
