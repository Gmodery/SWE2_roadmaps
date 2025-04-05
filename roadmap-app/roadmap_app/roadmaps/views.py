from django.shortcuts import render, redirect, get_object_or_404
from .models import Roadmap, AppUser, Class, Project, Task, TaskCategory, RoadmapSection, TaskRow
from django.contrib.auth.models import User
from collections import defaultdict
from django.urls import reverse
import random, string
from datetime import date, datetime, timedelta
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import SignUpForm, CreateClassForm, CreateProjectForm
from django.contrib.auth.decorators import login_required
from django.db import transaction

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


# -------- Roadmap Views -------------
@login_required(login_url='login')
def roadmap_details_view(request, class_id, project_id, roadmap_id):
    roadmap_instance = Roadmap.objects.get(id=roadmap_id)
    categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)
   
    task_rows = []
    for category in categories:
        cat_task_rows = TaskRow.objects.filter(taskrow_category=category)
        task_rows.append(cat_task_rows)

    sections = sorted(RoadmapSection.objects.filter(parent_roadmap=roadmap_instance), key=lambda section: section.start_date)


    def update_tasks(category):
        # Recalculate necessary rows for category
        # Step 1: Fetch all tasks from the database
        tasks = Task.objects.filter(task_roadmap=roadmap_instance, category=category).values('id', 'start_time', 'end_time').order_by('start_time')

        # List to track the active TaskRow objects (rows that are currently occupied)
        active_rows = []

        # Step 1: Iterate through each task
        for task in tasks:
            start_time = task['start_time']
            end_time = task['end_time']

            # Step 2: Try to fit the current task into an existing row
            assigned = False
            for row in active_rows:
                if row.end_time < start_time:
                    # If the task can fit in this row (it doesn't overlap with the task in this row)
                    row.end_time = end_time  # Update the row's end time
                    row.save()  # Save the updated row

                    # Associate task with the existing row
                    task_instance = Task.objects.get(id=task['id'])
                    task_instance.task_row = row
                    task_instance.save()
                    assigned = True
                    break

            # Step 3: If no row was found for the task, we need to add a new row
            if not assigned:
                # Create a new row and save it
                new_row = TaskRow.objects.create(taskrow_category=category, end_time=end_time)

                # Assign the task to the new row
                task_instance = Task.objects.get(id=task['id'])
                task_instance.task_row = new_row
                task_instance.save()

                # Add the new row to active_rows
                active_rows.append(new_row)

        TaskRow.objects.filter(taskrow_category=category).all()
        TaskRow.objects.filter(task_set__isnull=True).delete()

        # Set the number of rows for the category
        category.cat_rows = len(active_rows)

        # Save the category with the updated row count
        category.save()

        category.refresh_from_db()



    if request.method == "POST":
        if "category-name" in request.POST:
            # Add category
            cat_name = request.POST["category-name"]
            cat_color = request.POST["category-color"]

            new_category = TaskCategory(cat_name=cat_name, cat_color=cat_color, cat_roadmap=roadmap_instance, cat_rows=1)

            new_category.save()

            categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)


        elif "task-name" in request.POST:
            # Add task
            task_name = request.POST["task-name"]
            task_desc = request.POST["task-desc"]
            task_cat = int(request.POST["task-category"])
            task_start = request.POST['task-start']
            task_deadline = request.POST['task-deadline']

            if task_start < task_deadline: # Start must be before end
                first_start_date = sections[0].start_date
                
                if task_start >= str(first_start_date): # Start date must be after earliest section start
                    category = TaskCategory.objects.get(id=task_cat)

                    total_duration = (roadmap_instance.deadline - first_start_date).days

                    start_percent = ((datetime.strptime(task_start, "%Y-%m-%d").date() - first_start_date).days / total_duration) * 100
                    width_percentage = ((datetime.strptime(task_deadline, "%Y-%m-%d").date() - datetime.strptime(task_start, "%Y-%m-%d").date()).days) / total_duration * 100

                    new_task = Task(
                        task_roadmap=roadmap_instance,
                        task_name=task_name,
                        task_description=task_desc,
                        status='not_started',
                        category=category,
                        start_time=task_start,
                        end_time=task_deadline,
                        start_percent=start_percent,
                        width_percentage=width_percentage
                    )

                    new_task.save()

                    category.refresh_from_db()

                    update_tasks(category=category)

                    categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)


        elif "roadmap-title" in request.POST:
            # Roadmap Settings update
            map_title = request.POST["roadmap-title"]
            map_desc = request.POST["roadmap-desc"]
            map_deadline = request.POST["roadmap-deadline"]

            roadmap_instance.roadmap_title = map_title
            roadmap_instance.roadmap_description = map_desc
            roadmap_instance.deadline = map_deadline

            roadmap_instance.save()

        
        elif "task-name-edit" in request.POST:
            task_start = request.POST['task-start-edit']
            task_deadline = request.POST['task-deadline-edit']

            if task_start < task_deadline: # Start must be before end
                first_start_date = sections[0].start_date
                
                if task_start >= str(first_start_date): # Start date must be after earliest section start
                    total_duration = (roadmap_instance.deadline - first_start_date).days

                    start_percent = ((datetime.strptime(task_start, "%Y-%m-%d").date() - first_start_date).days / total_duration) * 100
                    width_percentage = ((datetime.strptime(task_deadline, "%Y-%m-%d").date() - datetime.strptime(task_start, "%Y-%m-%d").date()).days) / total_duration * 100


                    task_id = request.POST['task_id']
                    task_name = request.POST['task-name-edit']
                    task_desc = request.POST['task-desc-edit']
                    task_cat = TaskCategory.objects.get(id=int(request.POST['task-category-edit']))
                    task_status = request.POST['task-status-edit']
                    task_start = datetime.strptime(request.POST['task-start-edit'], '%Y-%m-%d').date()
                    task_end = datetime.strptime(request.POST['task-deadline-edit'], '%Y-%m-%d').date()

                    task = Task.objects.get(id=task_id)
                    task.task_name = task_name
                    task.task_description = task_desc
                    task.category = task_cat
                    task.status = task_status
                    task.start_time = task_start
                    task.end_time = task_end
                    task.start_percent = start_percent
                    task.width_percentage = width_percentage

                    print(task.start_percent, task.width_percentage)
                    
                    task.save()

                    task.refresh_from_db()

                    update_tasks(category=task_cat)

        
        elif "task_id_delete" in request.POST:
            try:
                task = Task.objects.get(id=request.POST["task_id_delete"])
                #print(task)
                task.delete()

                update_tasks(category=task.category)
                
                categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)
                

            except:
                pass



            
                
    print(categories[0].cat_rows)

    return render(request, "roadmaps/pages/roadmap.html", {"roadmap_instance": roadmap_instance, "categories": categories, "task_rows": task_rows, "sections": sections, "user": request.session['username'], "class_id": class_id, "project_id": project_id})

    # Student view
    if request.session["usertype"] == "student":
        return redirect("dashboard")
    
    # Instructor view
    elif request.session["usertype"] == "instructor":
        return redirect("dashboard")



@login_required(login_url='login')
def delete_category_view(request, class_id, project_id, roadmap_id, cat_id):
    if request.method == "POST":
        try:
            category = TaskCategory.objects.get(id=cat_id)
            category.delete()

        except:
            pass


    roadmap_instance = Roadmap.objects.get(id=roadmap_id)
    categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)
    sections = sorted(RoadmapSection.objects.filter(parent_roadmap=roadmap_instance), key=lambda section: section.start_date)

    task_rows = []
    for category in categories:
        cat_task_rows = TaskRow.objects.filter(taskrow_category=category)
        task_rows.append(cat_task_rows)


    return render(request, "roadmaps/pages/roadmap.html", {"roadmap_instance": roadmap_instance, "categories": categories, "task_rows": task_rows, "sections": sections, "user": request.session['username'], "class_id": class_id, "project_id": project_id}) 




@login_required(login_url='login')
def add_section_view(request, class_id, project_id, roadmap_id):
    roadmap_instance = Roadmap.objects.get(id=roadmap_id)
    categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)

    task_rows = []
    for category in categories:
        cat_task_rows = TaskRow.objects.filter(taskrow_category=category)
        task_rows.append(cat_task_rows)
        
    if request.method == "POST":
        if "add_section" in request.POST:
            sections = sorted(RoadmapSection.objects.filter(parent_roadmap=roadmap_instance), key=lambda section: section.start_date)
            new_end = sections[-1].end_date+timedelta(days=10) if sections[-1].end_date+timedelta(days=10) < roadmap_instance.deadline else roadmap_instance.deadline

            new_section = RoadmapSection(parent_roadmap=roadmap_instance, section_name="New Section", start_date=sections[-1].end_date, end_date=new_end)
            new_section.save()

    sections = sorted(RoadmapSection.objects.filter(parent_roadmap=roadmap_instance), key=lambda section: section.start_date)

    RoadmapSection.objects.last().start_date = sections[-1].end_date

    return render(request, "roadmaps/pages/roadmap.html", {"roadmap_instance": roadmap_instance, "categories": categories, "task_rows": task_rows, "sections": sections, "user": request.session['username'], "class_id": class_id, "project_id": project_id})


def save_sections_view(request, class_id, project_id, roadmap_id):
    if request.method == "POST":
        roadmap_instance = Roadmap.objects.get(id=roadmap_id)

        section_ids = [int(x) for x in request.POST.getlist("section_id[]")]
        section_names = request.POST.getlist("section_name[]")
        start_dates = request.POST.getlist("start_date[]")
        end_dates = request.POST.getlist("end_date[]")

        first_start_date = datetime.strptime(min(start_dates), "%Y-%m-%d").date()
        total_duration = (roadmap_instance.deadline - first_start_date).days

        # First pass to make updates
        for i, section_id in enumerate(section_ids):
            if start_dates[i] > end_dates[i]:
                continue

            section = RoadmapSection.objects.get(id=section_id)
            section.section_name = section_names[i]
            section.start_date = start_dates[i]
            section.end_date = end_dates[i]
            section.start_percent = ((datetime.strptime(section.start_date, "%Y-%m-%d").date() - first_start_date).days / total_duration) * 100
            section.width_percentage = ((datetime.strptime(section.end_date, "%Y-%m-%d").date() - datetime.strptime(section.start_date, "%Y-%m-%d").date()).days) / total_duration * 100

            section.save()


        sections = sorted(RoadmapSection.objects.filter(parent_roadmap=roadmap_instance), key=lambda section: section.start_date)

        # Second pass to fix overlaps and ensure minimum section length
        for i in range(len(section_ids) - 1):
            current_section = RoadmapSection.objects.get(id=section_ids[i])
            next_section = RoadmapSection.objects.get(id=section_ids[i + 1])

            # Ensure the current section has at least 10 days
            min_end_date = current_section.start_date + timedelta(days=10)
            if current_section.end_date < min_end_date:
                current_section.end_date = min_end_date

            # Ensure the next section starts immediately after the current section
            next_section.start_date = current_section.end_date

            # Ensure the next section also has at least 10 days
            next_min_end_date = next_section.start_date + timedelta(days=10)
            if next_section.end_date < next_min_end_date:
                next_section.end_date = next_min_end_date

            current_section.save()
            next_section.save()


        categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)
        sections = sorted(RoadmapSection.objects.filter(parent_roadmap=roadmap_instance), key=lambda section: section.start_date)

        task_rows = []
        for category in categories:
            cat_task_rows = TaskRow.objects.filter(taskrow_category=category)
            task_rows.append(cat_task_rows)
        
        return render(request, "roadmaps/pages/roadmap.html", {"roadmap_instance": roadmap_instance, "categories": categories, "task_rows": task_rows, "sections": sections, "user": request.session['username'], "class_id": class_id, "project_id": project_id})



def remove_section_view(request, class_id, project_id, roadmap_id, section_id):
    roadmap_instance = Roadmap.objects.get(id=roadmap_id)
    categories = TaskCategory.objects.filter(cat_roadmap=roadmap_instance)

    task_rows = []
    for category in categories:
        cat_task_rows = TaskRow.objects.filter(taskrow_category=category)
        task_rows.append(cat_task_rows)

    if request.method == "POST":
        try:
            RoadmapSection.objects.get(id=section_id).delete()
        except:
            pass

    sections = sorted(RoadmapSection.objects.filter(parent_roadmap=roadmap_instance), key=lambda section: section.start_date)

    return render(request, "roadmaps/pages/roadmap.html", {"roadmap_instance": roadmap_instance, "categories": categories, "task_rows": task_rows, "sections": sections, "user": request.session['username'], "class_id": class_id, "project_id": project_id})

# render function syntax: 
# render(HTTP request object, 
# html file in templates directory, 
# dictionary of data to pass to the template {variable_name : roadmaps list} )