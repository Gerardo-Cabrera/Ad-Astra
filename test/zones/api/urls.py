from django.urls import path

from zones.api import views

urlpatterns = [
    path('edit', views.edit),
    path('delete/<int:id>', views.delete),
]
