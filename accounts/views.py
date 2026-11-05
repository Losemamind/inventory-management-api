from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import mixins, viewsets
from rest_framework.permissions import IsAuthenticated

from .serializers import RegisterSerializer
from .models import User
from .permissions import IsAdminRole
from .serializers import UserManagementSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        return Response(
            {
                'message': 'สมัครสมาชิกสำเร็จ',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                }
            },
            status=status.HTTP_201_CREATED
        )

class UserManagementViewSet(mixins.ListModelMixin,mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    queryset = User.objects.all().order_by('id')
    serializer_class = UserManagementSerializer
    permission_classes = [IsAuthenticated, IsAdminRole]