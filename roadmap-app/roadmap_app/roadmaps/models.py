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

    def generate_unique_code(self):
        return ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))

    def __str__(self):
        return self.class_name


# TODO: Link project and roadmap together with foreign key
# TODO: Add description to project model
class Project(models.Model):
    project_title = models.CharField(max_length=25)
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


class Attachment(models.Model):
    attachment_roadmap = models.ForeignKey(Roadmap, on_delete=models.DO_NOTHING) # One roadmap has many attachments
    attachment_name = models.CharField(max_length=75)

    attachment_metadata = models.FileField(null=True)

    def __str__(self):
        return self.attachment_name
