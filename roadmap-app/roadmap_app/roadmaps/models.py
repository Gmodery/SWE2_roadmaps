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

    def __str__(self):
        return f"Section for {self.parent_roadmap} | {self.start_date} - {self.end_date}"


class TaskCategory(models.Model):
    cat_name = models.CharField(max_length=50)
    cat_color = models.CharField(max_length=6, default="ffffff", null=False) # Hex code (minus the #)

    cat_roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return self.name

class Task(models.Model):
    TASK_STATUS_CHOICES = (
        ('not_started', 'Not Started'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
    )

    # Link each task to a Roadmap
    task_roadmap = models.ForeignKey(Roadmap, on_delete=models.CASCADE, related_name="tasks")
    task_name = models.CharField(max_length=100)
    task_description = models.TextField()
    status = models.CharField(max_length=20, choices=TASK_STATUS_CHOICES, default='pending')
    # Use a ForeignKey to connect the task to a category 
    category = models.ForeignKey(TaskCategory, on_delete=models.SET_NULL, null=True, blank=True, related_name="task_cat")
    start_time = models.DateField()
    end_time = models.DateField()

    def __str__(self):
        return self.task_name

    

class Attachment(models.Model):
    attachment_roadmap = models.ForeignKey(Roadmap, on_delete=models.DO_NOTHING) # One roadmap has many attachments
    attachment_name = models.CharField(max_length=75)

    attachment_metadata = models.FileField(null=True)

    def __str__(self):
        return self.attachment_name