from django.db import models
from django.contrib.auth.models import AbstractUser


# One table to hold all user types
# Extends AbstractUser so we can still use Django's authentication features
class AppUser(AbstractUser):
    USER_ROLES = (
        ('admin', 'Administrator'),
        ('instructor', 'Instructor'),
        ('student', 'Student'),
    )

    # Add one field to define user type
    role = models.CharField(max_length=20, choices=USER_ROLES, default='student')


class Ticket(models.Model):
    ticket_title = models.CharField(max_length=50)
    ticket_description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.ticket_title


class Class(models.Model):
    class_name = models.CharField(max_length=25)
    class_desc = models.TextField(max_length=300, default="")
    class_instructor = models.ForeignKey(AppUser, on_delete=models.DO_NOTHING, related_name="instructor_classes") # One class has one instructor
    class_student = models.ManyToManyField(AppUser, related_name="student_classes") # N students can be a part of M classes
    class_join_code = models.CharField(unique=True, max_length=5, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.class_name


# TODO: Link project and roadmap together with foreign key
class Project(models.Model):
    project_title = models.CharField(max_length=25)
    project_description = models.TextField(blank=True, null=True)
    project_instructor = models.ForeignKey(AppUser, on_delete=models.DO_NOTHING)
    class_id = models.ManyToManyField(Class) # Many projects linked to many classes
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_title


class Roadmap(models.Model):
    roadmap_title = models.CharField(max_length=25)
    roadmap_description = models.TextField()
    roadmap_students = models.ManyToManyField(AppUser) # One student can have many roadmaps, and one roadmap can have many students
    created_at = models.DateTimeField(auto_now_add=True)

    metadata = models.JSONField(default=dict)

    def __str__(self):
        return self.roadmap_title

# I moved this up here since it needs to be defined before being used in Task
class TaskCategory(models.Model):
    # A unique name for each category.
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    # Good idea having specific choices. When would a task be in the pending state?
    TASK_STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    # Link each task to a Roadmap
    # I changed the first argument to be the roadmap class, rather than a string
    task_roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="tasks")
    task_name = models.CharField(max_length=100)
    task_description = models.TextField()
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='pending')
    # Use a ForeignKey to connect the task to a category 
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="task_cat")
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    def __str__(self):
        return self.task_name
    

"""
Good changes, just make sure to run manage.py makemigrations and manage.py migrate
so that the changes take effect in the DB. If you want to throw together an html page
and a view to create and update a task that would be good to get an idea of how it works
"""
    

class Attachment(models.Model):
    attachment_roadmap = models.ForeignKey(Roadmap, on_delete=models.DO_NOTHING) # One roadmap has many attachments
    attachment_name = models.CharField(max_length=75)

    attachment_metadata = models.FileField(null=True)

    def __str__(self):
        return self.attachment_name