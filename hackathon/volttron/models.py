from django.conf import settings
from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch.dispatcher import receiver

from subprocess import Popen, PIPE
from threading import Timer

import time
import psutil


DOCKER_ERR = None


def run_process(cmd, timeout_sec=5, check_output=False):
    proc = Popen(cmd, shell=True, stdout=PIPE, stderr=PIPE)
    timer = Timer(timeout_sec, proc.kill)
    try:
        timer.start()
        stdout, stderr = proc.communicate()
    finally:
        timer.cancel()
    if check_output:
        return stdout


def port_choices(port_set):
    return zip(list(port_set), list(port_set))


class Volttron(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vip_port = models.IntegerField(help_text='Instance port for the vip address', choices=port_choices(settings.VIP_PORTS), unique=True)
    vc_port = models.IntegerField(help_text='Port for volttron central', choices=port_choices(settings.VC_PORTS), unique=True)
    jupyter_port = models.IntegerField(help_text='Port for Jupyter Notebook', choices=port_choices(settings.JUPYTER_PORTS), unique=True)

    def error(self):
        return DOCKER_ERR

    @classmethod
    def is_exist(cls, vip_port):
        existed_containers = run_process(cmd='docker container ls -a',
                                         check_output=True)
        if not existed_containers:
            global DOCKER_ERR
            DOCKER_ERR = 'Timeout'
        return existed_containers.find('hackathon_{}'.format(vip_port)) != -1

    def is_running(self):
        running_containers = run_process(cmd='docker ps',
                                         check_output=True)
        if not running_containers:
            global DOCKER_ERR
            DOCKER_ERR = 'Timeout'
        return running_containers.find('hackathon_{}'.format(self.vip_port)) != -1

    def start_jupyter_notebook(self):
        jupyter_cmd = 'cd {} && ./jupyter_notebook.sh hackathon_{} {}'.format(settings.TRAINING_ROOT,
                                                                              self.vip_port,
                                                                              self.jupyter_port)
        run_process(jupyter_cmd)

    def start_container(self):
        if not self.is_running():
            if psutil.virtual_memory().available / (1024 * 1024) > settings.CONTAINER_MEMORY_LIMIT:
                run_process('docker container start hackathon_{}'.format(self.vip_port))
                self.start_jupyter_notebook()
            else:
                global DOCKER_ERR
                DOCKER_ERR = 'Not Enough Memory'

    def stop_container(self):
        if self.is_running():
            run_process('docker container stop hackathon_{}'.format(self.vip_port))

    def remove_container(self):
        if Volttron.is_exist(self.vip_port):
            run_process('docker container rm hackathon_{} --force'.format(self.vip_port))

    def __str__(self):
        return 'hackathon_{}'.format(self.vip_port)


@receiver(pre_save, sender=Volttron)
def _pre_save(sender, instance, *args, **kwargs):
    if instance.id:
        old_volttron = Volttron.objects.get(pk=instance.id)
        if (old_volttron.vip_port, old_volttron.vc_port, old_volttron.jupyter_port) != (instance.vip_port, instance.vc_port, instance.jupyter_port):
            old_volttron.remove_container()


@receiver(post_save, sender=Volttron)
def _post_save(sender, instance, *args, **kwargs):
    global DOCKER_ERR
    if not Volttron.is_exist(instance.vip_port):
        if psutil.virtual_memory().available / (1024 * 1024) > settings.CONTAINER_MEMORY_LIMIT:
            vc_cmd = 'cd {0} && ./run_container.sh hackathon_{1} {1} {2}'.format(settings.TRAINING_ROOT,
                                                                                 instance.vip_port,
                                                                                 instance.vc_port)
            run_process(vc_cmd)
            time.sleep(2)
            instance.start_jupyter_notebook()
        else:
            DOCKER_ERR = 'Not Enough Memory'
    else:
        DOCKER_ERR = 'Container Name Exists'


@receiver(pre_delete, sender=Volttron)
def _pre_delete(sender, instance, *args, **kwargs):
    instance.remove_container()