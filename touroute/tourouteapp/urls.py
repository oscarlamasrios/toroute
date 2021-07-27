from django.conf.urls import include, url
from tourouteapp import views

urlpatterns=[
  url(r'^index$', views.index, name='index'),
  url(r'^tweets/$', views.tweets, name='tweets'),
  url(r'^$', views.login_view, name = 'login_view'),
  url(r'^logout/$', views.logout_view, name='logout_view'),
  url(r'^signup/$', views.signup_view, name='signup_view'),
]
