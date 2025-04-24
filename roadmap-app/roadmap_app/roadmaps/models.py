from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import User


# One table to hold all user types
# Extends AbstractUser so we can still use Django's authentication features
class AppUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('instructor', 'Instructor'),
        ('admin', 'Admin'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} ({self.role})"

class Ticket(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=[
        ('open', 'Open'),
        ('resolved', 'Resolved')
    ], default='open')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.status}"


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
    class_instance = models.ForeignKey(Class, on_delete=models.CASCADE, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.project_title


class Roadmap(models.Model):
    roadmap_title = models.CharField(max_length=25)
    roadmap_description = models.TextField()
    roadmap_students = models.ManyToManyField(AppUser) # One student can have many roadmaps, and one roadmap can have many students
    parent_project = models.ForeignKey(Project, on_delete=models.CASCADE, null=True)
    deadline = models.DateField(auto_now_add=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.roadmap_title


class RoadmapSection(models.Model):
    parent_roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, null=True)
    section_name = models.CharField(max_length=50, default="Section", null=True)
    start_date = models.DateField(null=True)
    end_date = models.DateField(null=True)
    width_percentage = models.FloatField(null=True)
    start_percent = models.FloatField(null=True)

    def __str__(self):
        return f"Section for {self.parent_roadmap} | {self.start_date} - {self.end_date}"


class TaskCategory(models.Model):
    cat_name = models.CharField(max_length=50)
    cat_color = models.CharField(max_length=6, default="ffffff", null=False) # Hex code (minus the #)
    cat_rows = models.IntegerField(null=True)

    cat_roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.cat_name
    

class TaskRow(models.Model):
    # An individual row that contains tasks
    taskrow_category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, null=True, related_name="taskrow_cat")
    end_time = models.DateField(null=True)

    def __str__(self):
        return f"Row ID: {self.id}"

class Task(models.Model):
    TASK_STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    # Link each task to a Roadmap
    task_roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="tasks")
    task_name = models.CharField(max_length=100)
    task_description = models.TextField()
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='pending')
    # Use a ForeignKey to connect the task to a category 
    category = models.ForeignKey(TaskCategory, on_delete=models.CASCADE, null=True, blank=True, related_name="task_cat")
    start_time = models.DateField()
    end_time = models.DateField()

    task_row = models.ForeignKey(TaskRow, null=True, on_delete=models.SET_NULL, related_name='task_set')

    width_percentage = models.FloatField(null=True)
    start_percent = models.FloatField(null=True)

    def __str__(self):
        return self.task_name

    

    

class Attachment(models.Model):
    attachment_roadmap = models.ForeignKey(Roadmap, on_delete=models.DO_NOTHING) # One roadmap has many attachments
    attachment_name = models.CharField(max_length=75)

    attachment_metadata = models.FileField(null=True)

    def __str__(self):
        return self.attachment_name
