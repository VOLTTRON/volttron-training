# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin

from volttron.models import Volttron


class VolttronAdmin(admin.ModelAdmin):
    actions = ['sync_containers', 'stop_selected_containers', 'start_selected_containers']
    list_display = ['__str__', 'user', 'vc_port', 'jupyter_port', 'is_running', 'error']

    def sync_containers(self, request, queryset):
        for obj in queryset:
            if not Volttron.is_exist(obj.vip_port):
                obj.delete()

    def stop_selected_containers(self, request, queryset):
        for obj in queryset:
            obj.stop_container()

    def start_selected_containers(self, request, queryset):
        for obj in queryset:
            obj.start_container()


admin.site.register(Volttron, VolttronAdmin)
