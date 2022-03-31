from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from rest_framework import serializers

from typing import List

User = get_user_model()


class UserSerializer(serializers.HyperlinkedModelSerializer):
    case_studies = serializers.HyperlinkedIdentityField(
        many=True, view_name="casestudy-detail", read_only=True
    )

    class Meta:
        model: User = User
        fields: List[str] = [
            "url",
            "id",
            "first_name",
            "last_name",
            "username",
            "email",
            "case_studies",
        ]


class RegisterSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(label="Confirm Password")

    class Meta:
        model: User = User
        fields: List[str] = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "password",
            "confirm_password",
        ]
        extra_kwargs: dict = {
            "password": {"write_only": True},
            "confirm_password": {"write_only": True},
        }

    def validate(self, data):
        password = data.get("password")
        password_errors = dict()
        try:
            validate_password(password)
        except exceptions.ValidationError as e:
            password_errors["password"] = list(e.messages)

        if password_errors:
            raise serializers.ValidationError(password_errors)

        confirm_password = data.get("confirm_password")

        if password != confirm_password:
            raise serializers.ValidationError("Passwords do not match.")

        return data

    def create(self, validated_data):
        user = User.objects.create_user(
            validated_data["username"],
            validated_data["email"],
        )
        user.set_password(validated_data["password"])
        user.first_name = validated_data["first_name"]
        user.last_name = validated_data["last_name"]
        user.role = 1
        user.save()
        return user


# class LoginSerializer(serializers.Serializer):
#     username = serializers.CharField()
#     password = serializers.CharField()

#     def validate(self, data):
#         user = authenticate(**data)
#         if user and user.is_active:
#             return user
#         raise serializers.ValidationError("Incorrect Credentials Passed!")
