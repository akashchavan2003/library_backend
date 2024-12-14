from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth.models import User
from .models import Book, BorrowRequest
from .serializers import UserSerializer, BookSerializer, BorrowRequestSerializer
from .permissions import IsLibrarian, IsOwnerOrLibrarian

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsLibrarian]

class BookViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [IsAuthenticated]

class BorrowRequestViewSet(viewsets.ModelViewSet):
    queryset = BorrowRequest.objects.all()
    serializer_class = BorrowRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_permissions(self):
        if self.action in ['create', 'list']:
            permission_classes = [IsAuthenticated]
        elif self.action in ['approve', 'reject']:
            permission_classes = [IsLibrarian]
        else:
            permission_classes = [IsOwnerOrLibrarian]
        return [permission() for permission in permission_classes]

    def create(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        if request.user.is_staff:
            queryset = BorrowRequest.objects.all()
        else:
            queryset = BorrowRequest.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['PATCH'], permission_classes=[IsLibrarian])
    def approve(self, request, pk=None):
        borrow_request = self.get_object()
        borrow_request.status = 'APPROVED'
        borrow_request.save()
        return Response({'status': 'Borrow request approved'})

    @action(detail=True, methods=['PATCH'], permission_classes=[IsLibrarian])
    def reject(self, request, pk=None):
        borrow_request = self.get_object()
        borrow_request.status = 'REJECTED'
        borrow_request.save()
        return Response({'status': 'Borrow request rejected'})