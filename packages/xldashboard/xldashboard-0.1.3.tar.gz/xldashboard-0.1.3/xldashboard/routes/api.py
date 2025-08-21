# xl_dashboard/routes/api.py

from django.urls import path

from xldashboard.controllers import action_view

app_name = 'xl_dashboard'

urlpatterns = [
    path('action/<str:action_name>/', action_view, name='dashboard_action'),
]
