from django.contrib.auth.models import User
from rest_framework import serializers
from django.core.exceptions import ValidationError
import re

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only = True)

    class Meta:
        model = User
        fields = "__all__"

    def validate_email(self, value):                    #unique email
        if User.objects.filter(email = value).exists():
            raise serializers.ValidationError("This email haas already been registered!")
        return value

    def validate_password(self, value):         #validate_<field_name> function gets called automatically in DRF
        if len(value) <= 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not(re.search(r'[A-Za-z]', value) and re.search(r'\d', value)):
            raise serializers.ValidationError("Password must contain at least one alphabet and one numeric character.")

        return value

    def create(self, validated_data):
        user = User(
            username = validated_data['username'],
            email = validated_data['email']
        )
        # print(f"Raw password: {validated_data['password']}")

        user.set_password(validated_data['password'])
        # print(f"Hashed password: {user.password}")

        user.save()
        return user