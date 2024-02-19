from django.http import HttpResponse
from django.shortcuts import render
from .utils import UserUtils
from rest_framework import generics 
from .models import CustomUser,Institute, Student, Tutor
from .serializers import *
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.permissions import AllowAny
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q

import logging

logger = logging.getLogger(__name__)

class CustomUserCreateView(generics.CreateAPIView):
    queryset = CustomUser.objects.all()
    serializer_class = CustomUserSerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        instance = serializer.save()
        UserUtils().verify_user_account(instance.email, instance.uid)
        print(f"User registered: {instance.email}")
        return Response(serializer.data)
        
class CustomUserDetailView(generics.RetrieveAPIView):
    serializer_class = CustomUserSerializer
    
    def get_user_created_course(self,uid):
       try:
           custome_user = CustomUser.objects.get(uid=uid)
           courses = Course.objects.filter(author=custome_user)
           
           
           return courses
       except Course.DoesNotExist:
           return []
    
    def get(self,request,uid,*args,**kwargs):
        try:
            custome_user = CustomUser.objects.get(uid=uid)
            serializer = self.get_serializer(custome_user)
            
            courses = self.get_user_created_course(uid)
            courses_serializer = CourseSerializer(courses,many=True)
            
            reponse_data = {
                "data":serializer.data,
                "courses":courses_serializer.data
            }
            
            return Response(reponse_data)
            
        except CustomUser.DoesNotExist:
            return Response({"error":"User Not Found"},status=404)


    
class MyTokenObtainPairViewSerializer(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer



class VerifyAccountView(generics.RetrieveAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = [AllowAny]
    serializer_class = CustomUserSerializer

    def get_object(self):
        uid = self.kwargs.get('uid')
        return get_object_or_404(CustomUser, uid=uid)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)

        if not instance.is_email_verified:
            instance.is_email_verified = True
            instance.save()
            return HttpResponse({"detail": "Account is verified, and now you can log in."})
        else:
            return HttpResponse({"detail": "Account is already verified."})
        
        
class InstituteListAPIView(generics.ListAPIView):
    queryset = Institute.objects.all()
    serializer_class = InstituteSerializer

class StudentsInInstituteAPIView(generics.ListAPIView):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        institute_uid = self.kwargs['institute_uid']
        return CustomUser.objects.filter(student__institutes__uid=institute_uid)

class TutorsInInstituteAPIView(generics.ListAPIView):
    serializer_class = CustomUserSerializer

    def get_queryset(self):
        institute_uid = self.kwargs['institute_uid']
        return CustomUser.objects.filter(tutor__institutes__uid=institute_uid)


class CourseListView(generics.ListAPIView):
    queryset = Course.objects.all()
    serializer_class = CourseListSerializer
    
class RecomendedCourseListView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    def get_queryset(self):
        queryset = Course.objects.filter(recommended=True)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(name__icontains=search_query) | 
                Q(description__icontains=search_query)
            )
        return queryset
    

class CourseDetailView(generics.RetrieveAPIView):
    serializer_class = CourseSerializer

    def get_videos(self, course_uid):
        try:
            course = Course.objects.get(uid=course_uid)
            videos = Video.objects.filter(course=course)
            return videos
        except Course.DoesNotExist:
            return []

    def get(self, request, uid, *args, **kwargs):
        try:
            course = Course.objects.get(uid=uid)
            serializer = self.get_serializer(course)

            videos = self.get_videos(uid)
            video_serializer = VideoSerializer(videos, many=True)

            response_data = {
                'data': serializer.data,
                'videos': video_serializer.data,
            }
            return Response(response_data)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=404)
        



class StudentCoursesAPIView(generics.ListAPIView):
    serializer_class = CourseListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get the currently logged-in user
        user = self.request.user

        try:
            # Try to get the student associated with the user
            student = Student.objects.get(user=user)
         
            # Return the courses enrolled by the student
            return student.courses_enrolled.all()

        except Student.DoesNotExist:
            # If the student does not exist, return an empty queryset
            return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()

        if not queryset:
            # If the queryset is empty, return a 404 Not Found response
            return Response({"detail": "Student not found or no courses enrolled."}, status=status.HTTP_404_NOT_FOUND)

        # Serialize the queryset and return a 200 OK response
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class CourseStudentsListAPIView(generics.ListAPIView):
    serializer_class = StudentSerializer

    def get_queryset(self):
        course_id = self.kwargs['course_uid']
        print(course_id)
        try:
            course = Course.objects.get(uid=course_id)
            return course.students.all()
        except Course.DoesNotExist:
            return []

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
  




        
class AddStudentToCourseView(generics.UpdateAPIView):
    serializer_class = CourseListSerializer

    def update(self, request, *args, **kwargs):
        user = self.request.user
        course_uid = request.data.get('course_uid')

        if not course_uid or not user:
            return Response({'error': 'Both course_uid and student_uid must be provided'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            course = Course.objects.get(uid=course_uid)
            student = Student.objects.get(user=user)
         
        except (Course.DoesNotExist, Student.DoesNotExist):
            return Response({'error': 'Course or Student not found'}, status=status.HTTP_404_NOT_FOUND)

        course.students.add(student)
        serializer = self.get_serializer(course)

        return Response({'success': 'Student added to the course successfully', 'data': serializer.data})