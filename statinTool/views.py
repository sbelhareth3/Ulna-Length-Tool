from datetime import date

import fhirclient.models.patient as p
import fhirclient.models.procedure as pro
import requests
from django.http import HttpResponse
from django.template import loader
from django.views.decorators.csrf import csrf_exempt
import fhirclient.models.observation as obs
from fhirclient import client
from fhirclient.models import bundle
import pandas
import os
import re


# Create your views here.
settings = {
    'app_id': 'my_web_app',
    'api_base': 'https://r4.smarthealthit.org'
}
smart = client.FHIRClient(settings=settings)

# since this is proof of concept, we use a dictionary, but this is where we connect to patient database
patient_db = {
    "Mr. Barrett Cummings": "494743a2-fea5-4827-8f02-c2b91e4a4c9e",
    "Mrs. Raeann O'Kon": "881f534f-d041-425d-a542-cbf669f43e18",
    "Mrs. Twanda Rippin": "b85d7e00-3690-4e2a-87a0-f3d2dfc908b3",
    "Mr. Mario Dietrich":"1fc53917-6bc1-4f87-9008-c91e94f0e188",
    "Mr. David Alcántar": "dc877b20-081d-4109-9e97-99f0fdc58287",
    "Mr. Marcos Barrows": "c4d8bbb7-7214-4260-8a67-065f51f0af18",
    "Mrs. Natalia Ruelas": "d809375c-fef0-42fa-8529-603016123ea5",
    "Mrs. Reba Nolan": "9da7d8c2-daef-4722-832e-dcf495d13a4e",
}



# calculator code
def ulna_to_height(sex, age, ulna_length):
    """Requires:
        sex                             - "male" or "female" string
        age                             - string or int
        ulna_length                     - string or int
    """
    
    #be liberal in what we accept...massage the input
    if sex in ("MALE", "m", "M", "boy", "xy", "male", "Male"):
        sex = "male"
    if sex in ("FEMALE", "f", "F", "girl", "xx", "female", "Female"):
        sex = "female"    
    

    #intialize some things -----------------------------------------------------
    errors = [] #a list of errors
    standing_height = 0 
    age = int(age)
    ulna_length = int(ulna_length)
    
    # Intitalize our response dictionary
    response = {"status": 200,
                "sex":sex,
                "message": "OK",
                "age": age,
                "ulna_length":ulna_length
                "standing_height":standing_height
                "errors": errors
                }
    
    
    #run some sanity checks ----------------------------------------------------
    if not 5 <= age <=18:
        errors.append("Age must be within the range of 5 to 18.")
        
    if sex.lower() not in ('male', 'female'):
        errors.append("Sex must be male or female.")

    
    if sex == 'male':
        standing_height = 4.605*ulna_length + 1.308*age + 28.003 
        # (R2=0.96)
    if sex == 'female': 
        standing_height = 4.459*ulna_length + 1.315*age + 31.485 
        # (R2=0.94)


    if errors:
        response['status']=422
        response['message'] = "The request contained errors and was unable to process."
        response['errors']=errors
    else:
        response['standing_height']=standing_height     
        

    
    return response

@csrf_exempt
def home(request):
    template = loader.get_template('statin_tool.html')
    context = {}
    print(request.POST.get('patients', False))
    if request.POST.get('patients', False) != 'empty':
        context = {'name': request.POST.get('patients', False), "pats": patient_db}
    if request.method == 'POST' and request.POST.get('patients', False) != 'empty':
        print(request.POST['patients'])
        p_id = patient_db[request.POST.get('patients', False)]
        sex = ''
        age = 0
        ulna_length = 0
        standing_height = 0


        
        # calling the calculator
        calculation = ulna_to_height(sex=sex, age=age, ulna_length=ulna_length)
        
        # checking if the calculation was a success
        if calculation['status'] == 200:
            result = calculation

            context = {
                "result": result,
                "name": request.POST.get('patients', False),
                "pats": patient_db
            }
        else:
            result = calculation['errors']
            context = {
                "result": result,

            }

    return HttpResponse(template.render(context, request))

    