from django.shortcuts import render, redirect
from django.urls import path
from members.views import logout_user
from komunikator.views import wszystkie_projekty, nowy_projekt, edytuj_projekt, usun_projekt, usun_wszystkie, projectDetail, taskList, taskDetail, taskCreate, edit_task, delete_task, comments_detail, add_new_comment, edit_comment, delete_comment, view_comments, add_new_comment_projects, email, upload_test
from mojeerp2 import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [  
    path('wszystkie/', wszystkie_projekty, name="wszystkie_projekty"),
    path('nowy/', nowy_projekt, name="nowy_projekt"),
    path('usun_wszystkie/', usun_wszystkie, name="usun_wszystkie"),
    path('edytuj/<int:id>', edytuj_projekt, name="edytuj_projekt"),
    path('usun/<int:id>', usun_projekt, name="usun_projekt"),
    path('import/', wszystkie_projekty, name="import"),
    path('import_Excel_pandas/', views.import_excel_pandas, name="import_excel_pandas"),
    path('projects/<int:id>', projectDetail, name ='project-detail'),
    path('tasks', taskList, name ='tasks'),
    path('tasks/<int:pk>', taskDetail, name ='task-detail'),
    path('create-task/<int:id>', taskCreate, name ='create-task'),
    path('edit_task/<int:id>', edit_task, name ='edit_task'),
    path('delete_task/<int:id>', delete_task, name="delete_task"),
    path('comment/', comments_detail, name ='comments_detail'),
    path('add_new_comment/<int:id>', add_new_comment, name ='add_new_comment'),
    path('add_new_comment_projects/<int:id>', add_new_comment_projects, name ='add_new_comment_projects'),
    path('edit_comment/<int:id>', edit_comment, name="edit_comment"),
    path('delete_comment/<int:id>', delete_comment, name="delete_comment"),
    path('view_comments/<int:id>', view_comments, name="view_comments"),
    path('email/', email, name="email"),
    path('import_upload_test/', upload_test, name="upload_test"),
    ] + static(settings.MEDIA_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root = settings.STATIC_ROOT)

