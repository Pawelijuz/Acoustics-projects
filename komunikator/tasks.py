from __future__ import absolute_import, unicode_literals
from celery import shared_task
from .models import Projekt, Task
from django.contrib.auth.models import User
import pandas as pd
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
import numpy as np
from datetime import datetime, date, timedelta
import warnings, re
import openpyxl
from openpyxl.worksheet.datavalidation import DataValidation

@shared_task

def ReadFile():

 #pobranie numerów IC z listy istniejścych projektów i konwertowanie ich na listę int
    ic_list = Projekt.objects.all().values_list('Numer_IC')
    ic_list_int = []
    for Numer_IC in ic_list:
        Numer_IC = int(Numer_IC[0])
        ic_list_int.append(Numer_IC)
            
    #pobranie projektów z excela
    #myfile = pd.read_excel(r"C:\Users\purba\OneDrive\Pulpit\python\MojProjekt\Planner.xlsx")
    #with warnings.catch_warnings():
        #warnings.filterwarnings("ignore", category=UserWarning)
    
    #myfile = pd.read_excel('Planner.xlsx')
    
    empexceldata = pd.read_excel('Planner.xlsx', sheet_name='djangoerp')
    dbframe = empexceldata

#dodać warunek dodający i zmieniający zadania
#dodać uaktualnienia pozostałych pól
    for dbframe in dbframe.itertuples():
            Numer_IC = dbframe.Numer_IC
            if dbframe.Numer_IC in ic_list_int :
                projekt = Projekt.objects.get(Numer_IC = Numer_IC)
                projekt.Rynek = dbframe.Rynek
                projekt.Nazwa = dbframe.Nazwa
                projekt.save()
               
            else:
                obj = Projekt.objects.create(Numer_IC=dbframe.Numer_IC, Rynek=dbframe.Rynek, Nazwa=dbframe.Nazwa,
                                         Opis=dbframe.Opis, Rejestracja=dbframe.Rejestracja,
                                         Data_rysunki=dbframe.Rysunki, Data_części=dbframe.Części)
                obj.save()

                def convert_text_to_username(text):
                 # Remove whitespace and special characters
                    text = re.sub(r'\W+', '', text)
                    # Truncate to 255 characters
                    text = text[:255]
                    # Lowercase
                    text = text.upper()
                    return text
                username_id = convert_text_to_username(dbframe.Rynek)    
                Projekt.user = User.objects.get(username=username_id)

                tsk = Task.objects.create(projekt=obj, category="DRAWINGS CONFIRMATION", due_date=dbframe.Rysunki, assignee=Projekt.user, confirmation_day=dbframe.Potwierdzenie)
                tsk.save()
                if dbframe.Podwykonawca == "WMS":       
                    subcontractor_id = convert_text_to_username(dbframe.Podwykonawca)
                    Projekt.user = User.objects.get(username=subcontractor_id)  
                    tsk = Task.objects.create(projekt=obj, category="DELIVERY CONFIRMATION", due_date=dbframe.Części, assignee=Projekt.user)
                    tsk.save()        
    
    
    
  