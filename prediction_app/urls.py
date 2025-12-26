from django.urls import path
from prediction_app import views

urlpatterns = [
    path(
        '',
        views.index,
        name="home"),
    path(
        'check/diabetes/',
        views.diabetes_prediction,
        name="diabetes_prediction"),
    path(
        'check/result/',
        views.diabetes_result,
        name="diabetes_result"),
    path(
        'history/',
        views.history,
        name="history"),
    path(
        'download/result/',
        views.download,
        name="download"),
    path(
        'export/csv/',
        views.export_csv,
        name="export_csv"),
    path(
        'about/',
        views.about,
        name="about"),
    path(
        'contact/',
        views.contact,
        name="contact"),
    path(
        'monitor/',
        views.monitor,
        name="monitor"),
    path(
        'dashboard/doctor/',
        views.doctor_dashboard,
        name="doctor_dashboard"),
]
