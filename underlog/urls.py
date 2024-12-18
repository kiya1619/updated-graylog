from django.urls import path
from . import views
from .views import *

urlpatterns = [
    path('logs/', logs, name='logs'),
    path('', login ,name='login'),
    path('show/', show ,name='show'),
   path('errorcategory/', errorcategory ,name='errorcategory'),
   path('network/', network ,name='network'),
   path('database/', database ,name='database'),
   path('general/', general ,name='general'),
   path('auth/', auth ,name='auth'),
   path('configuration/', configuration ,name='configuration'),
   path('send_email_view/', send_email_view ,name='send_email_view'),
   path('login/', login ,name='login'),
   path('source_cat/', source_cat ,name='source_cat'),
   path('badrequest/', badrequest ,name='badrequest'),
   path('test/', test ,name='test'),
   path('criticall/', criticall ,name='criticall'),
   path('export_logs/csv/<str:error_type>/', export_error_logs_csv, name='export_error_logs_csv'),
   path('export_all_logs_csv/csv/all/', export_all_logs_csv, name='export_all_logs_csv'),

   
   
]


