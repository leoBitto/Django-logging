from django.urls import path
from .views import *
# include the following line inside the urls of base
# path('dashboard/logging/', include('logging.urls', namespace='logging')),

app_name = 'logging'

urlpatterns = [
    path('graphs/', GraphsView.as_view(), name='graphs'),
    path('Access-ErrorList/', AEListView.as_view(), name='AElist'),
    path('IPList/', IPListView.as_view(), name='IPlist'),
    path('log/access/<int:log_id>/', AccessLogDetailView.as_view(), name='access_log_detail'),  # URL per visualizzare i dettagli di un log
    path('log/error/<int:log_id>/', ErrorLogDetailView.as_view(), name='error_log_detail'),  # URL per visualizzare i dettagli di un log
    path('consent/', ConsentView.as_view(), name='consent_view'),
]