from rest_framework import serializers
from .models import Course, CustomUser , Institute , Video , Student
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['uid', 'email', 'phone', 'avatar', 'online',"description","first_name","last_name"]
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password')
        instance = super().create(validated_data)
        instance.set_password(password)
        instance.save()
        return instance



class MyTokenObtainPairSerializer(TokenObtainPairSerializer):

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Access Student instance and retrieve uid

        try:
            student = user.student
            token['student_id'] = str(student.uid)
        except Student.DoesNotExist:
            token['student_id'] = None

        token['username'] = f"{user.first_name}{user.last_name}"
        token['email'] = user.email
        token['is_institute_manager'] = user.is_institute_manager
        token['is_tutor'] = user.is_tutor
        token['is_student'] = user.is_student
        token["avatar"] = user.avatar.url

        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        user = self.user

        if not user.is_email_verified:
            raise serializers.ValidationError("Email not verified. Please verify your email link has sent to your email")

        return data
    

class UserActivationSerializer(serializers.Serializer):
    uid = serializers.IntegerField()
    


class InstituteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Institute
        fields = '__all__'


class CourseListSerializer(serializers.ModelSerializer):
    institutes = InstituteSerializer(many=True,read_only=True)
   
    class Meta:
        model = Course
        fields = '__all__'
        

    
class VideoSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Video
        fields = ["uid",'title', 'description', 'video_file', 'thumbnail', 'slug']

class CourseSerializer(serializers.ModelSerializer):
    institutes = InstituteSerializer(many=True,read_only=True)
    videos = VideoSerializer(many=True, read_only=True)
    author = serializers.ReadOnlyField(source='author.uid')
    class Meta:
        model = Course
        fields = ['image', 'uid', 'name', 'description', 'slug', 'no_of_video', 'no_of_lessons', 'no_of_resourse', 'institutes', 'price', 'rating',"videos","author"]
        

class StudentSerializer(serializers.ModelSerializer):
    user = CustomUserSerializer(read_only=True)
    class Meta:
        model = Student
        fields = '__all__'