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
from django.core.exceptions import ObjectDoesNotExist
import logging
@shared_task

def ReadFile():

 #pobranie numerów IC z listy istniejścych projektów i konwertowanie ich na listę int
    ic_list = Projekt.objects.all().values_list('Numer_IC')
    ic_list_int = []
    for Numer_IC in ic_list:
        Numer_IC = int(Numer_IC[0])
        ic_list_int.append(Numer_IC)
               
    empexceldata = pd.read_excel('NOWY Projekty specjalne - planowanie.xlsx', sheet_name='export')
    dbframe = empexceldata

    for dbframe in dbframe.itertuples():
        if dbframe.Zakończone == "TAK" or dbframe.Wstrzymać_export == "TAK" or dbframe.Numer_IC == 0:
            pass
        else:
            def convert_text_to_username(text):
                # Remove whitespace and special characters
                text = re.sub(r'\W+', '', text)
                # Truncate to 255 characters
                text = text[:255]
                # Lowercase
                text = text.upper()
                return text 
            
            Numer_IC = dbframe.Numer_IC
            if dbframe.Numer_IC in ic_list_int :
                projekt = Projekt.objects.get(Numer_IC = Numer_IC)
                projekt.Rynek = dbframe.Rynek
                projekt.Nazwa = dbframe.Nazwa
                projekt.Opis = dbframe.Opis
                projekt.save()
                task1 = Task.objects.get(projekt = projekt, category="DRAWINGS CONFIRMATION")
                task1.due_date = dbframe.Rysunki
                task1.confirmation_day = dbframe.Potwierdzenie
                task1.save()
                logger = logging.getLogger(__name__)
                try:
                    task2 = Task.objects.get(projekt = projekt, category="DELIVERY CONFIRMATION")
                except ObjectDoesNotExist:
                #utworzenie zadania DELIVERY dla projektu który już jest na liście 
                    if dbframe.Podwykonawca == "WMS":
                        username_id = convert_text_to_username(dbframe.Rynek)    
                        Projekt.user = User.objects.get(username=username_id)    
                        Task.objects.create(
                                projekt=projekt, 
                                category="DELIVERY CONFIRMATION", 
                                due_date=dbframe.Części, 
                                assignee=Projekt.user
                                )
                #aktualizacja dla zadania DELIVERY dla projektu który już jest 
                else:
                    if dbframe.Podwykonawca == "WMS":
                        task2.due_date = dbframe.Części
                        task2.save()
                #skasowanie zadania DELIVERY dla istniejącego projektu (usunięcie "WMS" z excela)
                    else:  
                        task2.delete()      
            #utworzenie nowego projektu
            else:
                obj = Projekt.objects.create(Numer_IC=dbframe.Numer_IC, Rynek=dbframe.Rynek, Nazwa=dbframe.Nazwa,
                                         Opis=dbframe.Opis, Rejestracja=dbframe.Rejestracja,
                                         Data_rysunki=dbframe.Rysunki, Data_części=dbframe.Części)
                obj.save()
                
                username_id = convert_text_to_username(dbframe.Rynek)    
                Projekt.user = User.objects.get(username=username_id)
                #utworzenie zadania DRAWINGS dla nowego projektu
                tsk = Task.objects.create(projekt=obj, category="DRAWINGS CONFIRMATION", due_date=dbframe.Rysunki, assignee=Projekt.user, confirmation_day=dbframe.Potwierdzenie)
                tsk.save()
                #utworzenie zadania DELIVERY dla projektu nowego
                if dbframe.Podwykonawca == "WMS":
                    create_delivery_task(dbframe, obj, subcontractor_name="WMS", task_category="DELIVERY CONFIRMATION", date_format=None)
                def create_delivery_task(dbframe, obj, subcontractor_name="WMS", task_category="DELIVERY CONFIRMATION", date_format=None):
                    try:    
                        subcontractor_id = convert_text_to_username(dbframe.Podwykonawca)
                        Projekt.user = User.objects.get(username=subcontractor_id)
                        due_date = dbframe.Części if isinstance(dbframe.Części, datetime) else None  
                        if due_date:
                            Task.objects.create(
                                projekt=obj, 
                                category="DELIVERY CONFIRMATION", 
                                due_date=due_date, 
                                assignee=Projekt.user
                                )
                        else:
                                raise ValueError("Invalid due date format")  
                    except User.DoesNotExist:
                        print(f"User with username {subcontractor_id} does not exist.") 

    