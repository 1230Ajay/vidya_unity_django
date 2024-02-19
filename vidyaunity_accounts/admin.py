from django.contrib import admin

from .models import *

# Register your models here.
admin.site.register(CustomUser)
admin.site.register(LiveSession)
admin.site.register(Tutor)
admin.site.register(Student)
admin.site.register(Institute)
admin.site.register(SalaryPayment)
admin.site.register(SessionAttendance)
admin.site.register(Institute_Category)
admin.site.register(Course)
admin.site.register(Video)
