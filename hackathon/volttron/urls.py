from django.conf.urls import url
from django.contrib.auth import views as auth_views

from . import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login/$', auth_views.login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', views.user_logout, name='logout'),
    url(r'^signup/$', views.signup, name='signup'),
    url(r'^index/$', views.index, name='index'),
    url(r'^error/$', views.error_view, name='error'),
]