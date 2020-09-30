from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.db.models import Count
from .models import Story, Status, Project
from django.shortcuts import get_object_or_404
from django.views.generic import ListView, CreateView, UpdateView, DetailView
from django import forms
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.mixins import UserPassesTestMixin
from django.template.response import TemplateResponse
from django.http import HttpResponse
from django.shortcuts import redirect
from django.contrib.auth.models import User



def superuser_check(user):
	if user.is_superuser:
		return False
	return True
	

@login_required
@user_passes_test(superuser_check, login_url = '/admin')
def home(request):

	# Get currently logged in user
	user = request.user

	# Get all the associated projects of the user
	projects  = user.project_set.all().order_by("name")

	# Project Counts
	projects_cnt = projects.count()

	# Find the role of the user in all the projects
	for project in projects:

		project.status_list = groupby_status(user, project)
		project.role = get_role(user, project)
		
	context = { 'projects' : projects}	
	return render(request, 'dashboard/home.html', context)

@login_required
@user_passes_test(superuser_check, login_url = '/admin')
def project_detail(request, pk):

	# Check if project exists
	get_object_or_404(Project, pk= pk)
	
	user = request.user	
	# Check if the user is associated with the project
	project = get_object_or_404(user.project_set, pk= pk)
	
	# Get the role of current user 
	role = user.assign_set.get(project = project).role

	is_project_leader = False
	if check_project_leader(role):
		is_project_leader = True

	# Get all project users
	associated_users = project.users.all().order_by("username")
	project_members =[]
	project_leader = []

	for associated_user in associated_users:
		role = associated_user.assign_set.get(project=project).role

		if check_project_leader(role):
			project_leader.append(associated_user)
		else:
			project_members.append(associated_user)


	status_list = groupby_status(user, project)


	# Get story/sr according to status types
	if is_project_leader:
		all_stories = Story.objects.filter(project = project).order_by('-sr_id')
		pass
	else:
		all_stories = Story.objects.filter(project = project, assigned_to=user).order_by('-sr_id')
		pass

	status = Status.objects.all().order_by("code")
	status_count = status.count()
	stories_list = []

	for status in status:
		stories_qset = all_stories.filter(status = status.pk)
		stories_list.append({"status_code":status.code,'count':stories_qset.count(),'status_description':status.description ,'stories_qset':stories_qset})

	context = {	'project': project,
				'project_leader':project_leader,
				'project_members':project_members,
				'status_list':status_list,
				'is_project_leader':is_project_leader,
				'stories_list': stories_list,
				'status_count':status_count}
	return render(request, 'dashboard/project-detail.html', context)
	

def projectExists(request, pk):
	# Get specific project based on pk
	project = Project.objects.filter(pk=pk)
	if project.count() == 0:
		return False
	return True

def check_project_leader(role):
	if role.code == 0:
		return True
	return False


def groupby_status(user, project):
	# Role of the user in current 'project'
	role = get_role(user, project)
	if check_project_leader(role): 
		# groupby with count operation
		project.count_qset = Story.objects.filter(project = project).values('status').annotate(scount=Count('status'))
		pass
	else:
		# groupby with count operation
		project.count_qset = Story.objects.filter(assigned_to=user, project = project).values('status').annotate(scount=Count('status'))
		pass

	status = Status.objects.all().order_by("code")
	status_list = []
	for status in status:
		found = False
		for proj in project.count_qset:
			if proj["status"] == status.pk:
				status_list.append({'code': status.code,'description':status.description,'count':proj["scount"]}) 
				found = True
				break
		if not found:
			status_list.append({'code': status.code,'description':status.description,'count':0}) 
	return status_list


def get_role(user, project):
	return user.assign_set.get(project=project).role

class StoryCreateForm(forms.ModelForm):
	class Meta:
		model = Story
		fields = ( 'title', 'description', 'assigned_to','status')
        
	def __init__(self, *args, **kwargs):
		self.project_id = kwargs.pop('project_id',None)
		self.method = kwargs.pop('method',None)
		super().__init__(*args, **kwargs)

		if self.method == "POST":
			return

		project = get_object_or_404(Project, pk= self.project_id) 
		associated_users = project.users.all().order_by("username")
		project_members =[]
		project_leaders = []

		for associated_user in associated_users:
			# Find role of each users in current project
			role = associated_user.assign_set.get(project=project).role
			associated_user.role = role
			if check_project_leader(role):
				project_leaders.append(associated_user.username)

		# Remove project leader from queryset
		for leader in project_leaders:
			associated_users = associated_users.exclude(username=leader)

		self.fields['assigned_to'].queryset = associated_users




class StoryCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
	template_name = 'dashboard/sr-create.html'

	def test_func(self):
		if self.request.user.is_superuser:
			return False
		
		return True
		

	def get(self, request, pk):
		
		user = self.request.user
		project = get_object_or_404(Project, pk= pk) 
		# Get the role of current user for current project
		role = get_object_or_404(user.assign_set, project= project).role 


		if not check_project_leader(role):
			return HttpResponse('<h1>404 - Forbidden</h1>')

		context = {'form': StoryCreateForm(project_id=pk, method = "GET"), 'project' : project}
		return render(request, self.template_name, context)

	def post(self, request, pk):
		user = self.request.user
		project = get_object_or_404(Project, pk= pk) 
		# Get the role of current user for current project
		role = get_object_or_404(user.assign_set, project= project).role 


		if not check_project_leader(role):
			return HttpResponse('<h1>404 - Forbidden</h1>')

		form = StoryCreateForm(request.POST, method = "POST")
		if form.is_valid():
			story = form.save(commit=False)
			
			project.sequence = project.sequence + 1
			project.save()
			story.sr_id = str(project.code)+"-"+str(project.sequence)

			story.assigned_by = user
			project = get_object_or_404(Project, pk= pk)
			story.project = project
			story.save()
			return redirect('project-detail',pk = pk)


class StoryDetailView(LoginRequiredMixin, UserPassesTestMixin, DetailView):
	model = Story
	template_name = 'dashboard/sr-detail.html'

	def test_func(self):
		user = self.request.user
		story = self.get_object()
		
		if user.is_superuser:
			return False
		else:
			# Check if current user has permission to view the Story Description
			if story.assigned_by == user or story.assigned_to == user:
				return True	
		
		return False


class StoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	template_name = 'dashboard/sr-update.html'

	def test_func(self):
		user = self.request.user
		if user.is_superuser:
			return False

		story_id = self.kwargs['pk']
		story = Story.objects.get(pk  = story_id)
		project = get_object_or_404(Project, pk= story.project.id) 
		# Get the role of current user for current project
		role = get_object_or_404(user.assign_set, project= project).role 


		if not check_project_leader(role):
			return False

		return True

	def get(self, request, pk):
		story = get_object_or_404(Story, pk= pk)		
		project_id = story.project.id

		form = StoryCreateForm(project_id=project_id,  instance=story, method = "GET")
		context = {'form': form, 'story':story}
		return render(request, self.template_name, context)
	
	def post(self, request, pk):
		story = get_object_or_404(Story, pk= pk)
		project_id = story.project.id
		form = StoryCreateForm(request.POST, method="POST")


		if form.is_valid():
			updated_title = request.POST.get("title", "")
			updated_description = request.POST.get("description", "")
			updated_assignee_id = request.POST.get("assigned_to", "")
			updated_status_id = request.POST.get("status", "")
			updated_assignee = get_object_or_404(User, id= updated_assignee_id)
			updated_status = get_object_or_404(Status, id= updated_status_id)

			# Update the story
			story.title = updated_title
			story.description = updated_description
			story.assigned_to = updated_assignee
			story.status = updated_status
			story.save()
			return redirect('project-detail',pk = project_id)


class UserStoryCreateForm(forms.ModelForm):
	
	class Meta:
		model = Story
		fields = ('status',)


class UserStoryUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
	template_name = 'dashboard/sr-user-update.html'

	def test_func(self):
		user = self.request.user
		if user.is_superuser:
			return False

		story_id = self.kwargs['pk']
		story = Story.objects.get(pk  = story_id)
		project = get_object_or_404(Project, pk= story.project.id) 
		# Get the role of current user for current project
		role = get_object_or_404(user.assign_set, project= project).role 

		if  check_project_leader(role):
			return False
		return True

	def get(self, request, pk):
		story = get_object_or_404(Story, pk= pk)		
		form = UserStoryCreateForm(instance=story)
		context = {'form': form, 'story':story}
		return render(request, self.template_name, context)
	
	def post(self, request, pk):
		story = get_object_or_404(Story, pk= pk)
		project_id = story.project.id
		form = UserStoryCreateForm(request.POST)

		if form.is_valid():
			updated_status_id = request.POST.get("status", "")
			updated_status = get_object_or_404(Status, id= updated_status_id)

			# Update the story
			story.status = updated_status
			story.save()

			return redirect('project-detail',pk = project_id)
		

