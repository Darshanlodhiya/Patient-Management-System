from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Annotated, Literal, Optional
import json

app = FastAPI()

class Patient(BaseModel):
    
    id: Annotated[str, Field(..., description='Add your user ID', example='P001')] # '...' means that the field is required
    name: Annotated[str, Field(..., description="Patient's name", example="Patient's name")]
    city: Annotated[str, Field(..., description="Patient's city", example="Patient's city")]
    age: Annotated[int, Field(..., gt=0, lt=120, description="Patient's age", example="Patient's age")]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description="Patient's gender", example="Patient's gender")]
    height: Annotated[float, Field(..., gt=2, description="Patient's height", example="Patient's height")]
    weight: Annotated[float, Field(..., gt=0, lt=250, description="Patient's weight", example="Patient's weight")]
    
    @computed_field
    @property
    def bmi(self) -> float:
        
        bmi = round(self.weight/(self.height**2), 2)
        return bmi
    
    @computed_field
    @property
    def verdict(self) -> str:
        
        if self.bmi < 18:
            return 'UnderWeight'
        elif self.bmi < 25:
            return 'Normal'
        elif self.bmi < 30:
            return 'OverWeight'
        else:
            return 'Obese'
        
class PatientUpdate(BaseModel):
    
    name: Annotated[Optional[str], Field(default=None)]
    city: Annotated[Optional[str], Field(default=None)]
    age: Annotated[Optional[int], Field(gt=0, default=None)]
    gender: Annotated[Optional[Literal['male', 'female', 'other']], Field(default=None)]
    height: Annotated[Optional[float], Field(gt=0, default=None)]
    weight: Annotated[Optional[float], Field(gt=0, default=None)]

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
        
    return data
        
def save_data(data_to_save):
    with open('patients.json', 'w') as f:
        json.dump(data_to_save, f, indent=4)
        
@ app.get('/')
def hello():
    return{"message": "Hello World !"}

@ app.get('/about')
def about():
    return{"message": "This is a fully functional Patient Management System created in FastAPI."}

@app.get('/view')
def view():
    data = load_data()
    return data

@app.get('/patient/{patient_id}')
def patient_view(patient_id: str = Path(..., description='ID of the patient in DB', example='P001')):
    # load data
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code=404, detail='ID not found')

@app.get('/sort')
# in Query parameter -> '...' means the query is required.
def sort_patients(sort_by: str = Query(..., description='sort on the basis of height, weight or bmi.'), Order: str = Query('asc', description='sort in ascending or descending order')):
    
    valid_fields = ['height', 'weight', 'bmi']
    
    if sort_by not in valid_fields:
        raise HTTPException(status_code=400, detail = f'invalid field. select from {valid_fields}')

    if Order not in ['asc', 'desc']:
        raise HTTPException(status_code=400, detail = 'invalid order. select either asc or desc')
    
    data = load_data()
    
    sort_order = True if Order=='desc' else False
    
    sorted_data = sorted(data.values(), key = lambda x: x.get(sort_by, 0), reverse = sort_order)

    return sorted_data

@app.post("/create")
def create_patient(patient: Patient):
    
    # load existing data
    data = load_data()
    
    # check if the patient with this id exists
    if patient.id in data:
        raise HTTPException(status_code=400, detail='Patient already exists')
    
    # new patient add to the database
    data[patient.id] = patient.model_dump()   # model_dump converts pydantic object to dictionary
    
    save_data(data)
    
    return JSONResponse(status_code=201, content={'message': 'patient created successfully'})
    

@app.put('/edit/{patient_id}')
def patient_update(patient_id: str, patient_update: PatientUpdate):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient_id not found')

    # 1. Get the existing dictionary
    existing_patient_info = data[patient_id]
    
    # 2. Get the new data (only fields that were actually sent)
    updated_patient_info = patient_update.model_dump(exclude_unset=True)
 
    # 3. Update the dictionary
    for key, value in updated_patient_info.items():
        existing_patient_info[key] = value
        
    # 4. Ensure 'id' is present for Pydantic validation
    existing_patient_info['id'] = patient_id
    
    # 5. Re-run through Patient model to recalculate BMI and Verdict
    patient_pydantic_object = Patient(**existing_patient_info)
    
    # 6. Save back to the main data object
    data[patient_id] = patient_pydantic_object.model_dump()
 
    save_data(data)
    
    return JSONResponse(status_code=200, content={'message': 'patient updated successfully'})

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    
    # load data
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code=404, detail='patient not found')
    
    del data[patient_id]
    
    save_data(data)
    
    return JSONResponse(status_code=200, content={'message': 'patient deleted successfully'})