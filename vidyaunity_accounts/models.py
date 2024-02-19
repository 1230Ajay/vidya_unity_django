from django.conf import settings
from django.db import models
from django.contrib.auth.models import AbstractUser
from .manager import CustomManager
import uuid
from django.utils.text import slugify
from django.core.exceptions import ValidationError

class CustomUser(AbstractUser):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True) 
    username = None
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    is_institute_manager = models.BooleanField(default=False)
    is_tutor = models.BooleanField(default=False)
    is_student = models.BooleanField(default=True)
    
    description = models.TextField(blank=True, null=True)
    address = models.CharField(max_length=50)
    phone = models.CharField(max_length=15, blank=True, null=True, unique=True)
    avatar = models.ImageField(blank=True, null=True, upload_to="profile")
    open_id = models.CharField(max_length=50, blank=True, null=True)
    online = models.BooleanField(default=False)
    
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    

    objects = CustomManager()
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    groups = models.ManyToManyField(
        "auth.Group",
        related_name="custom_user_set",
        blank=True,
        help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.",
        verbose_name="groups",
    )

    def __str__(self):
        return f"{self.email} - Manager:{self.is_institute_manager}, Tutor:{self.is_tutor}, Student:{self.is_student}"


class Institute_Category(models.Model):
    category_image= models.ImageField(upload_to="catagory_image",null=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

class Institute(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, blank=True, null=True)
    categories = models.ManyToManyField(Institute_Category, related_name="institutes")

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.name

def validate_video_extension(value):
    valid_extensions = ['.mp4', '.avi', '.mkv', '.mov']  # Add more if needed
    extension = str(value).lower().split('.')[-1]
    if not any(extension == ext for ext in valid_extensions):
        raise ValidationError('Unsupported file extension.')




 # Assuming __str__ method of CustomUser is defined
    
class Course(models.Model):
    image = models.ImageField(upload_to="course_image", null=True)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    no_of_video = models.IntegerField(default=0)
    no_of_lessons = models.IntegerField(default=0)
    no_of_resourse = models.IntegerField(default=0)
    institutes = models.ManyToManyField("Institute", related_name="courses")
    students = models.ManyToManyField("Student", related_name="courses_enrolled", blank=True, null=True)
    price = models.FloatField(null=True, blank=True)
    rating = models.FloatField(null=True, blank=True)
    recommended = models.BooleanField(default=False)
    author = models.ForeignKey("CustomUser",on_delete=models.CASCADE)

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
    
class Student(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE)
    institutes = models.ManyToManyField("Institute", related_name="students", blank=True, null=True)
 

    def __str__(self):
        return str(self.user) 

    
class Video(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    video_file = models.FileField(upload_to='videos/')
    thumbnail = models.ImageField(upload_to='thumbnails/', blank=True, null=True)
    slug = models.SlugField(unique=True, blank=True, null=True)
    course = models.ManyToManyField(Course, related_name="courses",null=True,blank=True)
   
    
    def save(self, *args, **kwargs):
        self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title

class Payment(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.student

class SalaryPayment(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tutor = models.ForeignKey("Tutor", on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    
class LiveSession(models.Model):
    topic = models.CharField(max_length=30)
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tutor = models.ForeignKey("Tutor", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    slug = models.SlugField(unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
        self.slug = slugify(f"{self.course.slug}-{self.start_time}")
        super().save(*args, **kwargs)
        
    def __str__(self):
        return self.topic

class SessionAttendance(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    student = models.ForeignKey("Student", on_delete=models.CASCADE)
    live_session = models.ForeignKey(LiveSession, on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    

class LiveSessionNote(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    tutor = models.ForeignKey("Tutor", on_delete=models.CASCADE)
    live_session = models.ForeignKey(LiveSession, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.title

class InstituteManager(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE)
    institute = models.OneToOneField(Institute, on_delete=models.CASCADE)

  
class Tutor(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    user = models.OneToOneField("CustomUser", on_delete=models.CASCADE)
    institutes = models.ManyToManyField(Institute, related_name="tutors")

    
    


