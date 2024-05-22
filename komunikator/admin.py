from django.contrib import admin
from .models import Projekt,Task, Comment
from import_export.admin import ImportExportModelAdmin



admin.site.register(Projekt)
admin.site.register(Task)
admin.site.register(Comment)

class ProjektAdmin(ImportExportModelAdmin):
     pass

#@admin.register(Projekt)
#jakie pola chcemy pokazać w admin-ie
#class ProjektAdmin(admin.ModelAdmin):
     #fields = ["Numer_IC', "Opis"]

#@admin.register(Comment)
#class CommentAdmin(admin.ModelAdmin):
#     list_display = ('name', 'task', 'created', 'active')
#     list_filter = ('active', 'created', 'updated')
#     search_fields = ('name', 'body')