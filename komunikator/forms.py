from django.forms import ModelForm
from .models import Projekt, Task, Comment
from django import forms
from django.forms import DateInput

class ProjektForm(ModelForm):
    class Meta:
        model = Projekt
        fields = ['Numer_IC', 'Nazwa', 'Rynek', 'Opis', 'Rejestracja', 'Data_rysunki', 'Data_części']

class TaskForm(ModelForm):
      class Meta:
        model = Task
        fields ='__all__'
        widgets = {'due_date': DateInput( format=('%Y-%m-%d'),
               attrs={'type': 'date' }),
                   'confirmation_day': DateInput( format=('%Y-%m-%d'),
               attrs={'type': 'date' })
                   } 
    
#klasa utworzona do edycji tylko pola status
class EditTaskForm(ModelForm):
      class Meta:
            model = Task
            fields = ['status']
       
class CommentForm(forms.ModelForm):
    class Meta:
      model = Comment
      #fields ='__all__'
      fields = ['task', 'name', 'body']
      
class EmailTaskForm(forms.Form):
        name = forms.CharField(max_length=25)
        email = forms.EmailField()
        to = forms.EmailField()
        emailtext = forms.CharField(required=False, widget=forms.Textarea)