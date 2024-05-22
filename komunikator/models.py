from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from import_export import resources

class Projekt(models.Model):
    Numer_IC = models.IntegerField(blank=False, unique=True)
    Nazwa = models.CharField(default='', max_length=20)
    Rynek = models.CharField(default='', max_length=20)
    Opis = models.CharField(default='', max_length=40)
    Rejestracja = models.DateField(default=timezone.now)
    Data_rysunki = models.DateField(default=timezone.now)
    Data_części = models.DateField(default=timezone.now)
    
    def __str__(self):
        return str(self.Numer_IC) + '  ' + self.Nazwa

class Task(models.Model):
    TODO="TO DO"
    COMPLETED='COMPLETED'
    INPROGRESS='IN-PROGRESS'
    DRAWINGS_CONFIRMATION= 'DRAWINGS CONFIRMATION'
    DELIVERY_CONFIRMATION= 'DELIVERY CONFIRMATION'
    OTHER= 'OTHER' 
    
    CATEGORY_CHOICES = [
        (DRAWINGS_CONFIRMATION, 'DRAWINGS CONFIRMATION'),
        (DELIVERY_CONFIRMATION, 'DELIVERY CONFIRMATION'),
        (OTHER, 'OTHER'),

    ]
       
    STATUS_CHOICES = [
        (TODO, 'TO DO'),
        (COMPLETED, 'COMPLETED'),
        (INPROGRESS, 'IN-PROGRESS'),

    ]
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    projekt = models.ForeignKey(Projekt,null=True,blank=True, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(User, null=True,blank=True, on_delete=models.SET_NULL)
    date_created = models.DateTimeField(auto_now_add=True)
    due_date = models.DateField(null=True,blank=True)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES,null=True,blank=True,default= TODO)
    confirmation_day = models.DateField(null=True,blank=True)
    
    def __str__(self):
        return str(self.projekt) + " " + str(self.category)
    
    class UserResource(resources.ModelResource):
        username = resources.Field()

class Comment(models.Model):
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=80)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ('-created',)
        
    def __str__(self):
        return 'comment for task {} added by {}'.format(self.task, self.name)

class Parametr(models.Model):
    parametr = models.IntegerField()

    # żeby się wyświetlał IC zamiast Project, musi być na tym samym poziomie co class



# Create your models here.
