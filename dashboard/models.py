from django.db import models
from django.contrib import admin
from django.contrib.auth.models import User


class Project(models.Model):
	code = models.CharField(max_length=10, unique=True)
	name = models.CharField(max_length=50)
	description = models.CharField(max_length=500)
	sequence = models.IntegerField()
	users = models.ManyToManyField(User, through = 'Assign')

	def __str__(self):
		return self.name


class Role(models.Model):
	code = models.IntegerField()
	Description = models.CharField(max_length=30)

	def __str__(self):
		return str(self.code) + " : " + self.Description


class Assign(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    role = models.ForeignKey(Role, on_delete=models.CASCADE)

    class Meta:
    	unique_together = ('project', 'user')

    def __str__(self):
    	return self.user.username + " -> " + self.project.name


class Assign_inline(admin.TabularInline):
    model = Assign
    extra = 1


class ProjectAdmin(admin.ModelAdmin):
    inlines = (Assign_inline,)	


class Status(models.Model):
	code = models.IntegerField(unique=True)
	description = models.CharField(max_length=20)

	def __str__(self):
		return str(self.description)


class Story(models.Model):
	sr_id = models.CharField(max_length=20)
	title = models.CharField(max_length=50)
	description = models.CharField(max_length=200)
	assigned_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "assigner")
	assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name = "assignee")
	project = models.ForeignKey(Project, on_delete=models.CASCADE)
	status = models.ForeignKey(Status, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.sr_id + " : " + self.title 

