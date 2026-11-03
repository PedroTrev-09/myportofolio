from django.core.exceptions import ValidationError as DjangoValidationError
from rest_framework import serializers

from main.models import Experience, Project
from main.validation import clean_experience_description, experience_dates, image_url, plain_text


class PlainTextModelSerializer(serializers.ModelSerializer):
    """Forms and APIs share rules, but each boundary runs its own validation."""
    text_fields = ()

    def validate(self, attrs):
        errors = {}
        for field in self.text_fields:
            if field in attrs:
                try:
                    attrs[field] = plain_text(attrs[field])
                except DjangoValidationError as error:
                    errors[field] = error.messages
        if errors:
            raise serializers.ValidationError(errors)
        return attrs


class ProjectSerializer(PlainTextModelSerializer):
    text_fields = ("title", "category", "short_description", "full_description", "tags")
    star_count = serializers.SerializerMethodField()
    is_starred = serializers.SerializerMethodField()
    starred_by_names = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = ["id", "title", "category", "image_url", "short_description",
                  "full_description", "tags", "created_at", "star_count",
                  "is_starred", "starred_by_names"]
        read_only_fields = ["id", "created_at"]

    def validate_image_url(self, value):
        try:
            return image_url(value)
        except (DjangoValidationError, ValueError) as error:
            raise serializers.ValidationError("Use an HTTP(S) image URL or root-relative asset path.") from error

    def get_star_count(self, obj):
        return obj.starred_by.count()

    def get_is_starred(self, obj):
        request = self.context.get("request")
        return bool(request and request.user.is_authenticated and request.user in obj.starred_by.all())

    def get_starred_by_names(self, obj):
        return ", ".join(user.username for user in obj.starred_by.all())


class ExperienceSerializer(PlainTextModelSerializer):
    text_fields = ("title", "location", "description")
    category_display = serializers.CharField(source="get_category_display", read_only=True)
    is_ongoing = serializers.BooleanField(read_only=True)

    class Meta:
        model = Experience
        fields = ["id", "title", "location", "description", "category", "category_display",
                  "started_at", "ended_at", "is_ongoing"]
        read_only_fields = ["id"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        start = attrs.get("started_at", getattr(self.instance, "started_at", None))
        end = attrs.get("ended_at", getattr(self.instance, "ended_at", None))
        try:
            experience_dates(start, end)
        except DjangoValidationError as error:
            raise serializers.ValidationError({"ended_at": error.messages}) from error
        return attrs

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["description"] = clean_experience_description(data["description"])
        return data
