from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.contrib import messages




def loginPage(request):
	if request.method == "POST":
		# Get username and password
		username = request.POST.get("username")
		password = request.POST.get("password")
		
		# Authenticate user
		user = authenticate(request, username = username, password = password)

		# Check if user exists in User table
		if user:
			# Check if a user is superuser
			if user.is_superuser:
				return redirect('/admin')
				
			else:
				# Log in the user
				login(request, user)
				return redirect('home')
							
		err_message = "Incorrect username or password."		
		messages.error(request, err_message)

	return render(request, 'users/login.html')

