from django.shortcuts import render
from rest_framework.decorators import api_view, permission_classes
from django.contrib.auth import authenticate
from django.core.mail import send_mail
from base.models import LoginOTP
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from django.contrib.auth.models import User
from base.serializers import ProductSerializer, UserSerializer, UserSerializerWithToken
# Create your views here.
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenObtainPairView

from django.contrib.auth.hashers import make_password
from rest_framework import status


class MyTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)

        serializer = UserSerializerWithToken(self.user).data
        for k, v in serializer.items():
            data[k] = v

        return data

@api_view(['POST'])
def requestLoginOtp(request):
    data = request.data
    email = data.get('username') or data.get('email')
    password = data.get('password')

    user = authenticate(username=email, password=password)

    if user is None:
        return Response(
            {'detail': 'No active account found with the given credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )

    code = LoginOTP.generate_code()
    LoginOTP.objects.create(user=user, code=code)

    send_mail(
        subject='Your Digital Edge login code',
        message=f'Your one-time login code is {code}. It expires in 10 minutes.',
        from_email=None,
        recipient_list=[user.email],
    )

    return Response({'detail': 'OTP sent to your email', 'email': user.email})


@api_view(['POST'])
def verifyLoginOtp(request):
    data = request.data
    email = data.get('email')
    code = data.get('otp')

    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response({'detail': 'Invalid code'}, status=status.HTTP_400_BAD_REQUEST)

    otp = LoginOTP.objects.filter(
        user=user, code=code, isUsed=False
    ).order_by('-createdAt').first()

    if otp is None or otp.is_expired():
        return Response({'detail': 'Invalid or expired code'}, status=status.HTTP_400_BAD_REQUEST)

    otp.isUsed = True
    otp.save()

    serializer = UserSerializerWithToken(user, many=False)
    return Response(serializer.data)
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer
@api_view(['POST'])
def registerUser(request):
    data = request.data
    try:
        user = User.objects.create(
            first_name=data['name'],
            username=data['email'],
            email=data['email'],
            password=make_password(data['password'])
        )

        serializer = UserSerializerWithToken(user, many=False)
        return Response(serializer.data)
    except:
        message = {'detail': 'User with this email already exists'}
        return Response(message, status=status.HTTP_400_BAD_REQUEST)
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUserProfile(request):
    user = request.user
    serializer = UserSerializerWithToken(user, many=False)

    data = request.data
    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']

    if data['password'] != '':
        user.password = make_password(data['password'])

    user.save()

    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def getUserProfile(request):
    user = request.user
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUsers(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([IsAdminUser])
def getUserById(request, pk):
    user = User.objects.get(id=pk)
    serializer = UserSerializer(user, many=False)
    return Response(serializer.data)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def updateUser(request, pk):
    user = User.objects.get(id=pk)

    data = request.data

    user.first_name = data['name']
    user.username = data['email']
    user.email = data['email']
    user.is_staff = data['isAdmin']

    user.save()

    serializer = UserSerializer(user, many=False)

    return Response(serializer.data)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def deleteUser(request, pk):
    userForDeletion = User.objects.get(id=pk)
    userForDeletion.delete()
    return Response('User was deleted')
