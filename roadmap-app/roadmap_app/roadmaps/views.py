from django.shortcuts import render, redirect, get_object_or_404
from .models import Roadmap, AppUser, Class, Project, Task, TaskCategory, RoadmapSection
from django.contrib.auth.models import User
from collections import defaultdict
from django.urls import reverse
import random, string
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, CreateClassForm, CreateProjectForm
from django.contrib.auth.decorators import login_required

def home(request):
    return render(request, 'roadmaps/home.html')

# Get the username and password from index.html POST and authenticate against User table
def login_view(request):
    # When index.html posts to itself, authenticate and redirect if successful
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)

            usertype = user.role

            request.session['username'] = username
            request.session['usertype'] = usertype
            request.session['user_id']  = user.id

            return redirect("dashboard")  # Redirect to a protected page
        else:
            messages.error(request, "Invalid username or password", extra_tags="login")

    # Else just render index.html
    return render(request, 'roadmaps/index.html')



def signup_view(request):
    # If we post, populate the form with the post data, make sure it is valid, then save the new user,
    # log in, and redirect to their dashboard
    if request.method == "POST":
        form = SignUpForm(request.POST)

        if form.is_valid():
            user = form.save() # Save new AppUser in database with posted data
            login(request, user) # Login and redirect to dashboard (save session data in request)
            request.session['username'] = request.POST['username']
            request.session['usertype'] = request.POST['role']
            request.session['user_id']  = user.id

            messages.success(request, "Account created successfully!")
            return redirect('../pages/dashboard')

    else:
        form = SignUpForm()

    # After setting "form" to SignUpForm, render the html page and
    # send it the form data under the alias 'form'
    return render(request, 'roadmaps/signup.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('login')


@login_required(login_url='login')
def join_class_view(request):
    # Do stuff to add student to class if code is valid the redirect to dashboard
    
    # Redirect if not a student
    if request.session["usertype"] != "student":
        return redirect('dashboard')

    if request.method == "POST":
            join_code = request.POST['join_code']

            target_class = Class.objects.get(class_join_code=join_code)
            student = AppUser.objects.get(id=request.session["user_id"])

            if target_class and student not in target_class.class_student.all():
                target_class.class_student.add(student)
                messages.success(request, f"{target_class.class_name} joined!")

            else:
                messages.error(request, "Class code invalid")
                return redirect('dashboard')


    return redirect("dashboard")


@login_required(login_url='login')
def dashboard(request):
    # Student view
    if request.session["usertype"] == "student":

        return render(request, 'roadmaps/pages/dashboard.html', {"username": request.session['username'], 
                                                                 "classes" : AppUser.objects.get(id=request.session['user_id']).student_classes.all(), 
                                                                 "student": True})

    
    # Instructor view
    elif request.session["usertype"] == "instructor":
        if request.method == "POST":
            def get_unique_code():
                code = None
                
                while code == None:
                    characters = string.ascii_letters + string.digits
                    code = ''.join(random.choices(characters, k=5))

                    _class = Class.objects.filter(class_join_code=code)

                    if _class:
                        code == None

                return code
                

            form = CreateClassForm(request.POST)

            if form.is_valid():                
                class_code = get_unique_code()

                class_name = form.cleaned_data['class_name']
                class_desc = form.cleaned_data['class_desc']

                new_class = Class (
                    class_name=class_name,
                    class_desc=class_desc,
                    class_instructor=AppUser.objects.get(id=request.session['user_id']),
                    class_join_code=class_code
                )

                new_class.save()

                messages.success(request, "Class creation successful!")
                
                # Refresh the page with the new class
                return redirect('dashboard')
            
            else:
                messages.error(request, "Class creation failed")
                return redirect('dashboard')
            

        else:
            form = CreateClassForm()


        return render(request, 'roadmaps/pages/dashboard.html', {"username": request.session['username'], 
                                                                 "classes" : Class.objects.filter(class_instructor=AppUser.objects.get(id=request.session['user_id'])), 
                                                                 "student": False, "create_class_form": form})




# Create roadmap page
@login_required(login_url='login')
def create_roadmap_view(request, class_id, project_id):
    if request.session["usertype"] == "student":
        return redirect("dashboard")

    class_instance = Class.objects.get(id=class_id)
    project_instance = Project.objects.get(id=project_id)

    if request.method == "POST":
        roadmap_title = request.POST.get('roadmap_title')
        roadmap_description = request.POST.get('roadmap_description')

        # Dictionary to store students grouped by group number
        group_dict = defaultdict(list)

        # Process each student input field
        for student in class_instance.class_student.all():
            group_number = request.POST.get(f'group_{student.id}')
            if group_number:
                group_dict[int(group_number)].append(student)

        # Create a roadmap for each group
        for group_number, students in group_dict.items():
            roadmap_title = f"{roadmap_title} - Group {group_number}"
            roadmap = Roadmap.objects.create(
                roadmap_title=roadmap_title,
                roadmap_description=roadmap_description
            )
            roadmap.roadmap_students.add(*students)

        return redirect('dashboard')


    else:
        if not class_instance:
            students = None

        else:
            students = class_instance.class_student.all().values('id', 'username')


    return render(request, "roadmaps/pages/create-roadmap-form.html", {"class_instance":class_instance, "students":students})


@login_required(login_url='login')
def class_detail_view(request, class_id):
    # List class details and verify that user has authority to access this class id
    selected_class = Class.objects.get(id=class_id)

    # Validate authorization to view this class
    if request.session['usertype'] == "student":
        # If student, verify that they are in this class
        class_students = selected_class.class_student.all()
        current_student = AppUser.objects.get(id=request.session['user_id'])

        if current_student not in class_students:
            return redirect('dashboard')

    elif request.session['usertype'] == "instructor":
        # If instructor, verify that they own this class
        if selected_class.class_instructor.id != request.session['user_id']:
            return redirect('dashboard')

    class_name = selected_class.class_name
    class_desc = selected_class.class_desc
    class_instructor = selected_class.class_instructor
    class_code = selected_class.class_join_code

    projects = Project.objects.filter(class_instance=selected_class)

    project_form = CreateProjectForm()

    return render(request, "roadmaps/pages/class_details.html", {"projects": projects, "class_name": class_name,
                  "class_desc": class_desc, "class_instructor": class_instructor, "class_code": class_code, 
                  "student": request.session['usertype'] == "student", "class_instance_id": class_id, "proj_form": project_form})


@login_required(login_url='login')
def class_delete_view(request, class_id):
    Class.objects.get(id=class_id).delete()
    return redirect('dashboard')
    

@login_required(login_url='login')
def create_project_view(request, class_id):
    if request.method == "POST" and request.session['usertype'] == 'instructor':
        form = CreateProjectForm(request.POST)

        if form.is_valid():
            proj_title = form.cleaned_data['project_name']
            proj_desc = form.cleaned_data['project_desc']

            instructor = AppUser.objects.get(id=request.session['user_id'])

            new_proj = Project (
                project_title=proj_title,
                project_description=proj_desc,
                project_instructor=instructor,
                class_instance=Class.objects.get(id=class_id)
            )

            new_proj.save()

        return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

        
    else:
        return redirect("dashboard")


@login_required(login_url='login')
def project_details_view(request, class_id, project_id):
    class_instance = Class.objects.get(id=class_id)
    project_instance = Project.objects.get(id=project_id)

    # Validate authorization to view this class
    if request.session['usertype'] == "student":
        # If student, verify that they are in this class
        class_students = class_instance.class_student.all()
        current_student = AppUser.objects.get(id=request.session['user_id'])

        if current_student not in class_students:
            return redirect('dashboard')
        
        all_maps = Roadmap.objects.filter(parent_project=project_instance)
        roadmaps = []

        for roadmap in all_maps:
            if current_student in roadmap.roadmap_students.all():
                roadmaps.append(roadmap)



    elif request.session['usertype'] == "instructor":
        # If instructor, verify that they own this class
        if class_instance.class_instructor.id != request.session['user_id']:
            return redirect('dashboard')
        
        # If instructor, able to view all roadmaps for this project
        roadmaps = Roadmap.objects.filter(parent_project=project_instance)
        
    print(class_instance.id, project_instance.id, roadmaps[0].id)

    return render(request, "roadmaps/pages/project_details.html", {"student": request.session['usertype'] == "student", "class_instance": class_instance,
                                                                   "project_instance": project_instance, "roadmaps": roadmaps})



def delete_project_view(request, class_id, project_id):
    Project.objects.get(id=project_id).delete()
    return redirect(reverse('class_detail', kwargs={'class_id': class_id}))



@login_required(login_url='login')
def account_detail_view(request):
    # Display account type and details
    user = AppUser.objects.get(id=request.session['user_id'])

    username = user.username
    user_type = user.role.title()
    full_name = f"{user.first_name} {user.last_name}"
    email = user.email
    date_joined = user.date_joined

    return render(request, "roadmaps/pages/account_details.html", {"username": username, "user_type": user_type, "full_name": full_name, "email": email, "date_joined": date_joined, "student": user_type=="Student"})



@login_required(login_url='login')
def roadmap_details_view(request, class_id, project_id, roadmap_id):
    roadmap_instance = Roadmap.objects.get(id=roadmap_id)
    categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)
    sections = sorted(RoadmapSection.objects.filter(parent_roadmap=roadmap_instance), key=lambda section: section.start_date)


    return render(request, "roadmaps/pages/roadmap.html", {"roadmap_instance": roadmap_instance, "categories": categories, "sections": sections, "user": request.session['username']})

    if request.method == "POST":
        pass

    # Student view
    if request.session["usertype"] == "student":
        return redirect("dashboard")
    
    # Instructor view
    elif request.session["usertype"] == "instructor":
        return redirect("dashboard")

    


# render function syntax: 
# render(HTTP request object, 
# html file in templates directory, 
# dictionary of data to pass to the template {variable_name : roadmaps list} )