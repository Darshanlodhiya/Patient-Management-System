from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open('patients.json', 'r') as f:
        data = json.load(f)
        
    return data

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

