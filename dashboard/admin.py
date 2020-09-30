from django.contrib import admin
from .models import  Project, Role, Assign, ProjectAdmin, Status, Story


admin.site.register(Project,ProjectAdmin)
admin.site.register(Role)
admin.site.register(Assign)
admin.site.register(Status)
admin.site.register(Story)
