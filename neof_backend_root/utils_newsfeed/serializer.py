from typing import List, Type
from datetime import datetime, timezone as dt_timezone
from math import floor

from django.utils import timezone

from rest_framework.validators import UniqueTogetherValidator

from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault,
    CurrentUserDefault,
    SkipField,
    empty,
)
from rest_framework import serializers

from .models import (
    CaseStudy,
    CaseStudyRound,
    NewsfeedBase,
    PostManual,
    ScrapedPost,
    AuthorSource,
    Author,
    AuthorAgent,
)


class UTV(UniqueTogetherValidator):
    def exclude_current_instance(self, attrs, queryset, instance):
        """
        If an instance is being updated, then do not include
        that instance itself as a uniqueness conflict, except for list updates
        """
        if instance is not None:
            if isinstance(instance, PostManual):
                return queryset.exclude(pk=instance.pk)
            return PostManual.objects.none()

        return queryset


class PostManualListSerializer(serializers.ListSerializer):
    def __init__(self, *args, **kwargs):
        self.newsfeed_base_id = kwargs.pop("newsfeed_base_id", False)
        super().__init__(*args, **kwargs)

    def update(self, instances, validated_data, *args, **kwargs):
        newsfeed_base = NewsfeedBase.objects.filter(id=self.newsfeed_base_id).first()
        instance_hash = {index: instance for index, instance in enumerate(instances)}

        result = []
        request = self.context.get("request")

        # print(" *** dude *** \n", request.data)

        user = request.user if request and hasattr(request, "user") else None

        for index, attrs in enumerate(validated_data):
            # print(f"index: {index}, attrs: {attrs}")
            res = None
            previous_post = instance_hash[index]
            existing_post = PostManual.objects.filter(**attrs)
            if existing_post.filter(
                newsfeed_base__id=self.newsfeed_base_id
            ):  # if post already exists within this newsfeed_base, skip
                result.append(previous_post)
                continue

            if existing_post:  # post exists, but not within this newsfeed_base
                res = existing_post.first()
            else:  # post does not exist yet
                try:
                    attrs["user"] = user
                    res = self.child.create(attrs)
                    existing_post_order_index = newsfeed_base.post_order[
                        "value_to_key"
                    ][f"{previous_post.id}"]
                    newsfeed_base.post_order["value_to_key"][
                        f"{res.id}"
                    ] = existing_post_order_index
                    newsfeed_base.post_order["order"][
                        existing_post_order_index
                    ] = res.id
                    del newsfeed_base.post_order["value_to_key"][f"{previous_post.id}"]
                    newsfeed_base.save()
                except BaseException as e:
                    raise e

                res.newsfeed_base.add(self.newsfeed_base_id)
                previous_post.newsfeed_base.remove(self.newsfeed_base_id)

            result.append(res)

        return result


class PostManualSerializer(serializers.ModelSerializer):
    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        This method implements the creation of a `ListSerializer` parent
        class when `many=True` is used. You can customize it if you need to
        control which keyword arguments are passed to the parent, and
        which are passed to the child.
        Note that we're over-cautious in passing most arguments to both parent
        and child classes in order to try to cover the general case. If you're
        overriding this method you'll probably want something much simpler, eg:
        @classmethod
        def many_init(cls, *args, **kwargs):
            kwargs['child'] = cls()
            return CustomListSerializer(*args, **kwargs)
        """
        allow_empty = kwargs.pop("allow_empty", None)
        max_length = kwargs.pop("max_length", None)
        min_length = kwargs.pop("min_length", None)
        newsfeed_base_id = kwargs.pop("newsfeed_base_id", None)
        child_serializer = cls(*args, **kwargs)
        list_kwargs = {
            "child": child_serializer,
        }
        if allow_empty is not None:
            list_kwargs["allow_empty"] = allow_empty
        if max_length is not None:
            list_kwargs["max_length"] = max_length
        if min_length is not None:
            list_kwargs["min_length"] = min_length
        if newsfeed_base_id is not None:
            list_kwargs["newsfeed_base_id"] = newsfeed_base_id
        list_kwargs.update(
            {
                key: value
                for key, value in kwargs.items()
                if key in serializers.LIST_SERIALIZER_KWARGS
            }
        )
        meta = getattr(cls, "Meta", None)
        list_serializer_class = getattr(
            meta, "list_serializer_class", serializers.ListSerializer
        )
        return list_serializer_class(*args, **list_kwargs)  # type: ignore

    # id = serializers.IntegerField()  # does not work
    user = serializers.ReadOnlyField(source="user.username")
    resource_url = serializers.SerializerMethodField()
    manage_url = serializers.SerializerMethodField()
    newsfeed_base_id = None

    def __init__(self, instance=None, data=empty, **kwargs):
        kwargs.pop("newsfeed_base_id", False)
        super().__init__(instance, data, **kwargs)

    def get_resource_url(self, obj):
        request = self.context.get("request")
        return obj.get_absolute_resource_url(request=request)

    def get_manage_url(self, obj):
        request = self.context.get("request")
        return obj.get_absolute_manage_url(request=request)

    class Meta:
        model: Type[PostManual] = PostManual
        list_serializer_class = PostManualListSerializer
        fields: str = "__all__"


class NewsfeedBaseCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[NewsfeedBase] = NewsfeedBase
        exclude = (
            "id",
            "post_order",
        )


class NewsfeedBaseSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    time_created = serializers.DateTimeField(
        default=timezone.now, format="%Y_%m_%d, %H:%M"
    )
    time_updated = serializers.DateTimeField(
        default=timezone.now, format="%Y_%m_%d, %H:%M"
    )
    post_manuals = PostManualSerializer(
        many=True,
        read_only=True,
    )

    resource_url = serializers.SerializerMethodField()
    manage_url = serializers.SerializerMethodField()

    def get_resource_url(self, obj):
        request = self.context.get("request")
        return obj.get_absolute_resource_url(request=request)

    def get_manage_url(self, obj):
        request = self.context.get("request")
        return obj.get_absolute_manage_url(request=request)

    # def update_post_order(self, instance, value):
    #     return new_post_order

    class Meta:
        model: Type[NewsfeedBase] = NewsfeedBase
        # fields: str = "__all__"
        fields: List[str] = [
            "id",
            "user",
            "name",
            "description",
            "newsfeed_size",
            "post_order",
            "fixed_post_set",
            "time_created",
            "time_updated",
            "post_manuals",
            "resource_url",
            "manage_url",
        ]


class CaseStudyRoundSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")

    time_created = serializers.DateTimeField(
        default=timezone.now, format="%Y_%m_%d, %H:%M"
    )
    time_updated = serializers.DateTimeField(
        default=timezone.now, format="%Y_%m_%d, %H:%M"
    )
    newsfeed_base = NewsfeedBaseSerializer(
        many=False,
        read_only=True,
    )

    resource_url = serializers.SerializerMethodField()
    manage_url = serializers.SerializerMethodField()

    def get_resource_url(self, obj):
        request = self.context.get("request")
        return obj.get_absolute_resource_url(request=request)

    def get_manage_url(self, obj):
        request = self.context.get("request")
        return obj.get_absolute_manage_url(request=request)

    class Meta:
        model: Type[CaseStudyRound] = CaseStudyRound
        fields: List[str] = [
            "id",
            "user",
            "name",
            "description",
            "time_created",
            "time_updated",
            "newsfeed_base",
            "resource_url",
            "manage_url",
        ]


class CaseStudySerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source="user.username")
    time_created = serializers.DateTimeField(
        default=timezone.now, format="%Y_%m_%d, %H:%M"
    )
    time_updated = serializers.DateTimeField(
        default=timezone.now, format="%Y_%m_%d, %H:%M"
    )
    case_study_rounds = CaseStudyRoundSerializer(
        many=True,
        read_only=True,
    )

    resource_url = serializers.SerializerMethodField()
    manage_url = serializers.SerializerMethodField()

    def get_resource_url(self, obj):
        request = self.context.get("request")
        return obj.get_absolute_resource_url(request=request)

    def get_manage_url(self, obj):
        request = self.context.get("request")
        return obj.get_absolute_manage_url(request=request)

    class Meta:
        model: Type[CaseStudy] = CaseStudy
        fields: List[str] = [
            "id",
            "user",
            "name",
            "description",
            "time_created",
            "time_updated",
            "case_study_rounds",
            "resource_url",
            "manage_url",
        ]


class AuthorSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[AuthorSource] = AuthorSource
        fields: str = "__all__"


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model: Type[Author] = Author
        fields: str = "__all__"


class AuthorAgentSerializer(serializers.ModelSerializer):
    author_source = AuthorSourceSerializer(
        read_only=True,
    )
    author = AuthorSerializer(
        read_only=True,
    )

    class Meta:
        model: Type[AuthorAgent] = AuthorAgent
        fields: str = "__all__"


class NewsfeedFbSerializer(serializers.ModelSerializer):
    author_agent = AuthorAgentSerializer(
        read_only=True,
    )

    time_since_creation = serializers.SerializerMethodField()

    def get_time_since_creation(self, obj):
        time_diff = datetime.now(dt_timezone.utc) - obj.date
        return floor(time_diff.seconds / 60)

    class Meta:
        model: Type[ScrapedPost] = ScrapedPost
        fields: List[str] = [
            "id",
            "user",
            "author_agent",
            "newsfeed_base",
            "post_url",
            "date",
            "time_since_creation",
            "text",
            "shared_text",
            "shared_text_domain",
            "language",
            "media",
            "image_url",
            "image",
            "image_low_quality_url",
            "image_low_quality",
            "video_views",
            "video_url",
            "like",
            "heart",
            "angry",
            "happy",
            "wow",
            "sad",
            "shares",
            "comments",
            "location",
            "header",
            "title",
            "content",
            "retweet",
            "quote_url",
            "user_rt_id",
            "user_rt",
            "retweet_id",
            "reply_to",
            "time_created",
            "time_updated",
        ]
