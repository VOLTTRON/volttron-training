from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.contrib.auth import views as auth_views
from django.core.exceptions import ObjectDoesNotExist

from volttron.models import Volttron

import random
import psutil


@login_required
def home(request):
    return render(request, 'home.html')


def user_logout(request):
    username = request.user.username
    user = User.objects.get(username=username)
    try:
        v_object = Volttron.objects.get(user=user)
        v_object.stop_container()
    except ObjectDoesNotExist:
        pass
    return auth_views.logout(request, next_page='login')


def signup(request):
    if request.method == 'POST':
        if psutil.virtual_memory().available/(1024*1024) > settings.CONTAINER_MEMORY_LIMIT \
                and Volttron.objects.all().count() < settings.TOTAL_CONTAINERS:
            form = UserCreationForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)

                used_vip_ports = Volttron.objects.values_list('vip_port', flat=True)
                used_vc_ports = Volttron.objects.values_list('vc_port', flat=True)
                used_jupyter_ports = Volttron.objects.values_list('jupyter_port', flat=True)

                try:
                    vip_port = random.choice(list(settings.VIP_PORTS - set(used_vip_ports)))
                    vc_port = random.choice(list(settings.VC_PORTS - set(used_vc_ports)))
                    jupyter_port = random.choice(list(settings.JUPYTER_PORTS - set(used_jupyter_ports)))

                    v_object = Volttron.objects.create(user=user,
                                                       vip_port=vip_port,
                                                       vc_port=vc_port,
                                                       jupyter_port=jupyter_port)

                    return redirect('index')
                except IndexError:
                    return render(request, 'error.html',
                                  context={'error_msg': 'There are no open ports available for creating containers'})
        else:
            return render(request, 'error.html',
                          context={'error_msg': 'There is no free space for creating containers'})
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


def index(request):
    username = request.user.username
    user = User.objects.get(username=username)
    try:
        v_object = Volttron.objects.get(user=user)

        if request.method == 'GET':
            if v_object.is_running():
                return render(request, 'vhome.html',
                              context={'vc_url': '{}:{}/vc/index.html#/login'.format(settings.PUBLIC_URL,
                                                                                     v_object.vc_port),
                                       'jupyter_url': '{}:{}'.format(settings.PUBLIC_URL,
                                                                     v_object.jupyter_port),
                                       'vip_port': v_object.vip_port,
                                       'vc_port': v_object.vc_port,
                                       'jupyter_port': v_object.jupyter_port})
            else:
                return render(request, 'vhome.html',
                              context={'vip_port': v_object.vip_port,
                                       'vc_port': v_object.vc_port,
                                       'jupyter_port': v_object.jupyter_port})
        else:
            try:
                stop_cmd = request.POST['stop-volttron']
                v_object.stop_container()
            except KeyError:
                v_object.start_container()
            return redirect('index')
    except ObjectDoesNotExist:
        return render(request, 'vhome.html', context={})


def error_view(request):
    return render(request, 'error.html')