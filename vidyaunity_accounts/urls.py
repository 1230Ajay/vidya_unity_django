from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView , TokenVerifyView
from django.urls import path ,include
from .views import *


urlpatterns = [
    path("register_account/",CustomUserCreateView.as_view(),name="register"),
    path("user/<uuid:uid>/", CustomUserDetailView.as_view()),
    path("",MyTokenObtainPairViewSerializer.as_view(),name='token_obtain_view'),
    path("refresh/",TokenRefreshView.as_view(),name="token_refresh_view"),
    path('verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('verify_account/<uuid:uid>/', VerifyAccountView.as_view(), name='verify_account'),
    
    path('institutes/', InstituteListAPIView.as_view(), name='institute-list'),
    path('institutes/<uuid:institute_uid>/students/', StudentsInInstituteAPIView.as_view(), name='students-in-institute'),
    path('institutes/<uuid:institute_uid>/tutors/', TutorsInInstituteAPIView.as_view(), name='tutors-in-institute'),
    
    path('courses/', CourseListView.as_view(), name='courses'),
    path('course/<uuid:uid>/',CourseDetailView.as_view() , name='courses'),
    path('student-have-courses/', CourseStudentsListAPIView.as_view(), name='student-courses-api'),
    path('course-in-students/', StudentCoursesAPIView.as_view(), name='course-students-count-api'),
    path('course/add-student/', AddStudentToCourseView.as_view(), name='add-student-to-course'),
    
    path('course/recommended/',RecomendedCourseListView.as_view(),name="recommended_courses")
]
