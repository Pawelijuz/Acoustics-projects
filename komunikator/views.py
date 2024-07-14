from pathlib import Path
from django.shortcuts import render, get_object_or_404, redirect
from .models import Projekt, Task ,Comment
from .forms import ProjektForm, TaskForm, CommentForm, EditTaskForm, EmailTaskForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
import pandas as pd
from django.db.models import Q
import numpy as np
from datetime import datetime, date, timedelta
import smtplib
from django.core.mail import send_mail
import os
import warnings, re
import logging
from django.core.exceptions import ObjectDoesNotExist
import komunikator.models

#jeśli jakaś funkcja ma być dostępna tylko dla zalogowanych użytkowników to:@login_requred

@login_required()
def nowy_projekt(request):
    form = ProjektForm(request.POST or None, request.FILES or None)

    if form.is_valid():
        form.save()
        return redirect(wszystkie_projekty)

    return render(request, 'projekt_form.html', {'form': form})

@login_required()
def edytuj_projekt(request, id):
    projekt = get_object_or_404(Projekt, pk=id)
    form = ProjektForm(request.POST or None, request.FILES or None, instance=projekt)

    if form.is_valid():
        form.save()
        return redirect(wszystkie_projekty)

    return render(request, 'projekt_form.html', {'form': form})

def usun_wszystkie(request):
    projekty = Projekt.objects.all()
    if request.method == "POST":
        projekty.delete()
        return redirect(wszystkie_projekty)
    return render(request, 'potwierdz_wszystkie.html', {'projekt': projekty})

        
@login_required()      
def import_excel_pandas(request):

    if request.method == 'POST' and request.FILES['myfile']:
        #pobranie numerów IC z listy istniejścych projektów i konwertowanie ich na listę int
        ic_list = Projekt.objects.all().values_list('Numer_IC')
        ic_list_int = []
        for Numer_IC in ic_list:
            Numer_IC = int(Numer_IC[0])
            ic_list_int.append(Numer_IC)
            
        #pobranie projektów z excela
        myfile = request.FILES['myfile']
        #print(os.path.abspath(myfile))
        empexceldata = pd.read_excel(myfile, sheet_name='djangoerp')
        dbframe = empexceldata
        for dbframe in dbframe.itertuples():
            if dbframe.Numer_IC in ic_list_int:
                print("IC o numerze:", dbframe.Numer_IC, "jest już na liście")
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
                           
        return render(request, 'import_excel_db.html', {
            'uploaded_file_url': myfile
        })

    return render(request, 'import_excel_db.html', {})
    
def usun_projekt(request, id):
    projekt = get_object_or_404(Projekt, pk=id)
    if request.method == "POST":
        projekt.delete()
        return redirect(wszystkie_projekty)
    return render(request, 'potwierdz.html', {'projekt': projekt})

def taskList(request):
    user_tasks =Task.objects.filter(assignee=request.user)
    
    today = date.today()  
    context = {'user_tasks':user_tasks, 'today':today}
    return render(request, 'tasks.html',context)

def taskDetail(request,pk):
    task = get_object_or_404(Task, id=pk)
    context = {'task':task}
    return render(request, 'task-detail.html',context)        

def taskCreate(request, id):
    projekt = get_object_or_404(Projekt, pk=id)
    form = TaskForm
    new_task = None
    if request.method == "POST":
       form =TaskForm(request.POST)
       if form.is_valid():
           new_task = form.save(commit=False)
           new_task.projekt = projekt
           new_task.save()
    else:
        form = TaskForm
             
    context = {'form':form, 'projekt':projekt, 'new_task': new_task}
    return render(request, 'task-create.html',context)

def edit_task(request, id):
    task = get_object_or_404(Task, pk=id)
    form = EditTaskForm(instance=task)
    
    if request.method == 'POST':
        form = EditTaskForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            return redirect(taskList)

    return render(request, 'edit_task.html', {'form': form})

def delete_task(request, id):
    task = get_object_or_404(Task, pk=id)
    if request.method == "POST":
        task.delete()
        return redirect(wszystkie_projekty)
    return render(request, 'delete_task.html', {'task': task})

def wszystkie_projekty(request):
        today = date.today()    
        if 'q' in request.GET:
            q = request.GET['q']    
            multiple_q = Q(Q(Numer_IC__icontains=q) | Q(Opis__icontains=q) | Q(Rynek__icontains=q) | Q(Nazwa__icontains=q))
            projekt = Projekt.objects.filter(multiple_q)
            return render(request, 'projekty.html', {'projekty': projekt})
        else:
            projekt = Projekt.objects.all
            context = {'projekty':projekt,'today':today}
            return render(request, 'projekty.html', context)               
           
def comments_detail(request, task):
    task = get_object_or_404(Task)
    comments = task.comments.filter(active=True)
    
    if request.method == 'POST':
       comment_form = CommentForm(data=request.POST)
    if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.task = task
            new_comment.save() 
    else:
            comment_form = CommentForm()
       
    context = {'comment_form': comment_form, 'task': task, 'comments': comments}
    return render(request, 'comments_detail.html',context)
 
    
def projectDetail(request, id):
    projekt = get_object_or_404(Projekt, pk=id)
    task = projekt.tasks.filter(projekt = projekt)   
    comments = Comment.objects.select_related().filter(task__in = task) 

    context = {'projekt':projekt,'task':task, 'comments': comments }
    return render(request, 'project-detail.html',context)

def add_new_comment(request, id):
    task = get_object_or_404(Task, pk=id)
    projekt = task.projekt
    form = CommentForm 
    new_comment = None                                        
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.task = task
            new_comment.save() 
    else:
        form = CommentForm()           
    context = {'form': form, 'task': task, 'projekt':projekt, 'new_comment': new_comment}
    return render(request, 'add_new_comment.html',context)

def add_new_comment_projects(request, id):
    task = get_object_or_404(Task, pk=id)
    projekt = task.projekt
    form = CommentForm 
    new_comment = None                                        
    if request.method == 'POST':
        form = CommentForm(data=request.POST)
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.task = task
            new_comment.save() 
    else:
        form = CommentForm()           
    context = {'form': form, 'task': task, 'projekt':projekt, 'new_comment': new_comment}
    return render(request, 'add_new_comment_projects.html',context)



def edit_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)
    task = comment.task
    projekt = task.projekt
    new_comment = None
    form = CommentForm(request.POST or None, request.FILES or None, instance=comment)
    
    if form.is_valid():
        new_comment = form.save(commit=False)
        comment.task = task
        form.save()
   
    context = {'form': form, 'projekt':projekt, 'task': task, 'comment':comment, 'new_comment': new_comment}
    return render(request, 'edit_comment.html', context)

def delete_comment(request, id):
    comment = get_object_or_404(Comment, pk=id)
    task = comment.task
    projekt = task.projekt
    form = CommentForm(request.POST or None, request.FILES or None, instance=comment)
    button = None
    if request.method == "POST":
        comment.delete()
        message = 'Comment deleted'
        button = True    
    else:
        message = 'Do you want to delete comment?'
        
    context = {'form': form, 'task': task, 'projekt':projekt, 'comment':comment, 'message':message, 'button': button}
    return render(request, 'delete_comment.html', context)

def view_comments(request, id):
    task = get_object_or_404(Task, pk=id)
    projekt = task.projekt
    comments = task.comments.filter(active=True)
    
    context = {'task': task, 'comments': comments, 'projekt': projekt}
    return render(request, 'view_comments.html',context)

def email(request):
    #task = get_object_or_404(Task, id=task_id)
    sent = False
    form = EmailTaskForm(request.POST)
    if request.method == 'POST':
        form = EmailTaskForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            subject = 'testowy text' 
            message = 'to jest testowa wiadomość'
            send_mail(subject, message, 'acousticsprojects@gmail.com', [cd['to']])
            sent = True
        else:
            form = EmailTaskForm()
        
    context ={'form': form, 'sent': sent}
    return render(request, 'email.html',context)

def upload_test(request):

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

    return render(request, 'import_excel_db.html', {})