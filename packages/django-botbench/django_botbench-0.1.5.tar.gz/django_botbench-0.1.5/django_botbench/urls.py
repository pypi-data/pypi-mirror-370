
from django.urls import path, re_path

from . import views

urlpatterns = [
    path('embed/conversation/<uuid:conversation_id>/', views.conversation_embed, name='conversation'),
    path('embed/conversation/', views.conversation_new, name='conversation_new'),
]

