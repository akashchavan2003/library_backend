from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Book, BorrowRequest

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'

class BorrowRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = BorrowRequest
        fields = '__all__'
        read_only_fields = ['status', 'user']

    def validate(self, data):
        # Validate date range
        if data['start_date'] > data['end_date']:
            raise serializers.ValidationError("Start date must be before end date")

        # Check for overlapping borrow requests
        overlapping_requests = BorrowRequest.objects.filter(
            book=data['book'],
            status='APPROVED',
            start_date__lt=data['end_date'],
            end_date__gt=data['start_date']
        )
        
        if overlapping_requests.exists():
            raise serializers.ValidationError("Book is already borrowed during this period")

        return data