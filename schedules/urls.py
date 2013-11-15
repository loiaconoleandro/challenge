from django.conf.urls import patterns, url

from schedules import views

urlpatterns = patterns(
   '',
   url(r'^$', views.IndexView.as_view(), name='index'),
   url(r'^check_flight/$', views.check_flight, name='check_flight'),
   url(r'^notify/$', views.notify, name='notify'),
   url(r'^add_notification/$', views.add_notification, name='add_notification'),
   url(r'^import_data/$', views.load_data_to_db, name='import_data')
)