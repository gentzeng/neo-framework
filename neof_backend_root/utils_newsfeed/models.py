import uuid

from django.conf import settings
from django.db import models
from django.core.files import File
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
    FileExtensionValidator,
    URLValidator,
)
from django.utils import timezone
from django.contrib.auth import get_user_model

from rest_framework.reverse import reverse

import os.path as path
import urllib.request
from .utils import RenameFilesModel

from .csv_upload import get_csv_data_size, load_csv

DEFAULT_NEWSFEED_SIZE = settings.DEFAULT_NEWSFEED_SIZE
DEFAULT_LIKE_PROBABILITY = settings.DEFAULT_LIKE_PROBABILITY

User = get_user_model()

# Account
# class ResearchUser(User):
# class TestSubject():
# class EphemeralTestSubject(TestSubject):
# class RegisteredTestSubject(TestSubject):


def user_directory_path(instance, filename):
    # file will be uploaded to MEDIA_ROOT/beat/author/<filename>
    user_id = list(User.objects.filter(username=instance.user).values("id"))[0]["id"]
    return (
        f"static/uploads/userName-{instance.user}-userID-{user_id}"
        f"/newsfeedBase/fixed_post_set/{filename}"
    )


class CaseStudy(models.Model):
    user = models.ForeignKey(
        User, related_name="case_studies", on_delete=models.CASCADE
    )
    name = models.CharField(max_length=128, null=True)
    description = models.CharField(max_length=512, null=True)
    time_created = models.DateTimeField(default=timezone.now, null=False)
    time_updated = models.DateTimeField(default=timezone.now, null=False)
    # Link to study?

    def get_absolute_resource_url(self, **kwargs):
        request = kwargs["request"]
        return reverse("casestudy-detail", kwargs={"pk": self.id}, request=request)

    def get_absolute_manage_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "casestudy-manage",
            kwargs={"resource_id": self.id},
            request=request,
        )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                    "description",
                ],
                name="%(app_label)s_%(class)s_knique",
            )
        ]


class CaseStudyRound(models.Model):
    user = models.ForeignKey(
        User, related_name="case_study_rounds", on_delete=models.CASCADE
    )
    case_study = models.ForeignKey(
        CaseStudy,
        related_name="case_study_rounds",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=128, null=True)
    description = models.CharField(max_length=512, null=True)
    time_created = models.DateTimeField(default=timezone.now, null=False)
    time_updated = models.DateTimeField(default=timezone.now, null=False)

    def get_absolute_resource_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "casestudy-casestudyround-detail",
            kwargs={"case_study_id": self.case_study.id, "pk": self.id},
            request=request,
        )

    def get_absolute_manage_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "casestudyround-manage",
            kwargs={"resource_id": self.id},
            request=request,
        )


class NewsfeedBase(models.Model):
    @classmethod
    def make_query(cls, *args, **kwargs):
        return cls.objects.filter(**kwargs)

    user = models.ForeignKey(
        User, related_name="newsfeed_bases", on_delete=models.CASCADE
    )
    case_study_round = models.OneToOneField(
        CaseStudyRound,
        on_delete=models.CASCADE,
        null=True,
    )
    name = models.CharField(max_length=128, null=True)
    description = models.CharField(max_length=512, null=True)
    newsfeed_size = models.IntegerField(
        default=None,
        blank=False,
        null=True,
    )

    post_order = models.JSONField(default=dict, blank=True, null=True)

    fixed_post_set = models.FileField(
        upload_to=user_directory_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(["csv"])],
    )

    time_created = models.DateTimeField(default=timezone.now, null=False)
    time_updated = models.DateTimeField(default=timezone.now, null=False)

    def get_absolute_resource_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "casestudyround-newsfeedbase-detail",
            kwargs={"case_study_round_id": self.case_study_round.id, "pk": self.id},
            request=request,
        )

    def get_absolute_manage_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "newsfeedbase-manage",
            kwargs={"resource_id": self.id},
            request=request,
        )

    def save(self, *args, **kwargs):
        self.super_save(
            *args, **kwargs
        ).set_newsfeed_size().set_and_save_post_order().save_posts_from_fixed_post_set()

    def set_newsfeed_size(self, *args, **kwargs):
        if self.newsfeed_size:
            return self
        if self.fixed_post_set:
            newsfeed_size = get_csv_data_size(file_path=self.fixed_post_set.path)
            self.newsfeed_size = newsfeed_size
            return self

        return self

    def set_and_save_post_order(self):
        if not self.newsfeed_size or self.post_order:
            return self

        self.post_order = {
            "order": [None for _ in range(self.newsfeed_size)],
            "value_to_key": {},
        }

        super().save(force_update=True)

        return self

    def super_save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        return self

    def save_posts_from_fixed_post_set(self):
        if not self.fixed_post_set or self.has_posts():
            return self

        load_csv(
            user=self.user,
            file_path=self.fixed_post_set.path,
            newsfeed_base_id=self.id,
        )
        return self

    def has_posts(self):
        if PostManual.objects.filter(newsfeed_base__id=self.id):
            return True

        return False


class NewsfeedScrapingSetting(models.Model):
    case_study_round = models.OneToOneField(
        CaseStudyRound,
        on_delete=models.CASCADE,
    )
    # oldest time or time span


class NewsfeedDisplayingSetting(models.Model):
    case_study_round = models.ForeignKey(
        CaseStudyRound,
        related_name="newsfeed_displaying_setting",
        on_delete=models.CASCADE,
    )
    like_probability = models.DecimalField(
        default=DEFAULT_LIKE_PROBABILITY,
        max_digits=5,
        decimal_places=2,
        blank=False,
        null=False,
        validators=[MaxValueValidator, MinValueValidator],
    )


class AuthorSource(models.Model):
    name = models.CharField(max_length=255, null=False)
    url = models.URLField(
        default="",
        max_length=1024,
        blank=True,
        null=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                ],
                name="%(app_label)s_%(class)s_unique",
            ),
        ]


class Author(models.Model):
    name = models.CharField(max_length=255, null=False)
    url = models.URLField(
        default="",
        max_length=1024,
        blank=True,
        null=True,
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "name",
                ],
                name="%(app_label)s_%(class)s_unique",
            ),
        ]


class AuthorAgent(RenameFilesModel):
    author = models.ForeignKey(
        Author,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.CASCADE,
    )
    author_source = models.ForeignKey(
        AuthorSource,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.CASCADE,
    )
    name = models.CharField(max_length=255, blank=True, null=True)
    avatar_url = models.URLField(
        default="",
        max_length=1024,
        blank=True,
        null=True,
    )
    avatar = models.ImageField(
        upload_to="static/uploads/authors/temp/",
        blank=True,
        null=True,
        max_length=1024,
    )
    username = models.CharField(max_length=255)
    verified = models.BooleanField(default=False, blank=False, null=False)
    link = models.URLField(
        default="",
        max_length=1024,
        blank=True,
        null=True,
    )
    bio = models.TextField(default="", blank=True, null=True)
    followers = models.PositiveIntegerField(default=int(0), blank=True, null=True)
    following = models.PositiveIntegerField(default=int(0), blank=True, null=True)

    RENAME_FILES = {"avatar": {"dest": "static/authors", "keep_ext": True}}

    def save(self, *args, **kwargs):
        super(RenameFilesModel, self).save(*args, **kwargs)
        if self.avatar_url and not self.avatar:
            result = urllib.request.urlretrieve(self.avatar_url)
            with open(result[0], "rb") as f:
                self.avatar.save(path.basename(self.avatar_url), File(f))

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "username",
                    "author_source",
                    "author",
                ],
                name="%(app_label)s_%(class)s_unique",
            ),
        ]


class AbstractPost(models.Model):
    @classmethod
    def make_query(cls, *args, **kwargs):
        return cls.objects.filter(**kwargs)

    def upload_image(instance, filename):  # type: ignore
        return (
            "static/uploads/postManual/images/%Y_%m_%d"
            f"_{type(instance)}_{instance.id}_image"
        )

    def upload_image_low_quality(instance, filename):  # type: ignore
        return (
            "static/uploads/postManual/images/%Y_%m_%d"
            f"_{type(instance)}_{instance.id}_image_low_quality"
        )

    user = models.ForeignKey(
        User,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.CASCADE,
    )
    author_agent = models.ForeignKey(
        AuthorAgent,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.CASCADE,
        null=True,
    )
    newsfeed_base = models.ManyToManyField(
        NewsfeedBase,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        blank=True,
    )

    # normal fields
    post_url = models.URLField(
        default="",
        max_length=1024,
        null=False,
        validators=[URLValidator(schemes=["http", "https"])],
    )

    date = models.DateTimeField(default=timezone.now, null=False)
    text = models.TextField(default="", null=False)
    shared_text = models.TextField(default="", null=True)
    shared_text_domain = models.TextField(default="", null=True)
    language = models.CharField(max_length=128, blank=True, null=True)

    media = models.JSONField(default=dict, blank=True, null=True)

    image_url = models.URLField(
        default="",
        max_length=1024,
        blank=True,
        null=True,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    image = models.ImageField(
        upload_to=upload_image,
        blank=True,
        null=True,
    )

    image_low_quality_url = models.URLField(
        default="",
        max_length=1024,
        blank=True,
        null=True,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    image_low_quality = models.ImageField(
        upload_to=upload_image_low_quality,
        blank=True,
        null=True,
    )

    video_views = models.PositiveIntegerField(default=0, blank=True, null=True)

    video_url = models.URLField(
        default="",
        max_length=1024,
        blank=True,
        null=False,
        validators=[URLValidator(schemes=["http", "https"])],
    )  # noqa: E501
    # video = models.ImageField( # Video Field?
    #     upload_to="static/uploads/postManual/videos/%Y/%m/%d/",
    #     blank=True,
    #     null=True,
    # )

    # reactions
    like = models.PositiveIntegerField(default=0)
    heart = models.PositiveIntegerField(default=0, blank=True, null=True)
    angry = models.PositiveIntegerField(default=0, blank=True, null=True)
    happy = models.PositiveIntegerField(default=0, blank=True, null=True)
    wow = models.PositiveIntegerField(default=0, blank=True, null=True)
    sad = models.PositiveIntegerField(default=0, blank=True, null=True)

    shares = models.PositiveIntegerField(default=0, blank=True, null=True)
    comments = models.PositiveIntegerField(default=0)
    location = models.TextField(default="")

    header = models.URLField(
        default="",
        max_length=1024,
        null=False,
        validators=[URLValidator(schemes=["http", "https"])],
    )
    title = models.TextField(default="", blank=True, null=True)
    content = models.TextField(default="", blank=True, null=True)

    # Twitter Stuff
    retweet = models.BooleanField(default=False, blank=True, null=True)
    quote_url = models.URLField(
        default="",
        max_length=1024,
        validators=[URLValidator(schemes=["http", "https"])],
        blank=True,
        null=True,
    )
    user_rt_id = models.TextField(default="", blank=True, null=True)
    user_rt = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=False, blank=True, null=True
    )
    retweet_id = models.UUIDField(
        primary_key=False, default=uuid.uuid4, editable=False, blank=True, null=True
    )
    reply_to = models.TextField(default="", blank=True, null=True)

    # internal fields
    time_created = models.DateTimeField(default=timezone.now, null=False)
    time_updated = models.DateTimeField(default=timezone.now, null=False)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.image_url and not self.image:
            try:
                result = urllib.request.urlretrieve(self.image_url)
                with open(result[0], "rb") as f:
                    self.image.save(path.basename(self.image_url), File(f))
            except BaseException:
                pass
        if self.image_low_quality_url and not self.image_low_quality:
            try:
                result = urllib.request.urlretrieve(self.image_low_quality_url)
                with open(result[0], "rb") as f:
                    self.image_low_quality.save(
                        path.basename(self.image_low_quality_url), File(f)
                    )
            except BaseException:
                pass

        if self.shared_text and not self.shared_text_domain:
            shared_text_split = self.shared_text.split("\n", 1)
            shared_text_domain = shared_text_split[0]
            shared_text = shared_text_split[1]
            self.shared_text_domain = shared_text_domain
            self.shared_text = shared_text
            super().save(*args, **kwargs)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "author_agent",
                    "post_url",
                    "date",
                    "text",
                    "language",
                    "header",
                    "title",
                    "content",
                    "media",
                    "image_url",
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
                    "retweet",
                    "quote_url",
                    "user_rt_id",
                    "user_rt",
                    "retweet_id",
                    "reply_to",
                ],
                name="%(app_label)s_%(class)s_unique",
            ),
        ]


# class PostCreatedByResearcher(AbstractPost):
class PostManual(AbstractPost):
    def get_absolute_resource_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "postmanual-detail",
            kwargs={"pk": self.id},
            request=request,
        )

    def get_absolute_manage_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "postmanual-manage",
            kwargs={"resource_id": self.id},
            request=request,
        )


class ScrapedPost(AbstractPost):
    def get_absolute_resource_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "postmanual-detail",
            kwargs={"pk": self.id},
            request=request,
        )

    def get_absolute_manage_url(self, **kwargs):
        request = kwargs["request"]
        return reverse(
            "postmanual-manage",
            kwargs={"resource_id": self.id},
            request=request,
        )


class PostUrl(models.Model):
    post_manual = models.ForeignKey(
        PostManual,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    scraped_post = models.ForeignKey(
        ScrapedPost,
        related_name="%(app_label)s_%(class)s_related",
        related_query_name="%(app_label)s_%(class)ss",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    url = models.URLField(
        default="",
        max_length=1024,
        validators=[URLValidator(schemes=["http", "https"])],
    )


class PostStatistic(models.Model):
    post_id = models.IntegerField(null=False)
    token_id = models.IntegerField(null=False)
    visibility_time = models.IntegerField(null=False)  # in Seconds
    clicked = models.IntegerField(null=False)
    read_time = models.IntegerField(null=False)
    reactions_category = models.IntegerField(null=False)
    reactions_count = models.IntegerField(null=False)
    reactions_override = models.IntegerField(null=False)
    statistics_category = models.IntegerField(null=False)
    statistics_count = models.IntegerField(null=False)
    recommendations_category = models.IntegerField(null=False)
    recommendations_count = models.IntegerField(null=False)
    # Todo: Get current timestamp DEFAULT CURRENT_TIMESTAMP, DateTimeField??
    time_created = models.DateTimeField(default=timezone.now, null=False)
    time_updated = models.DateTimeField(default=timezone.now, null=False)
    # DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,


class Result(models.Model):
    COUNT_token_id = models.BigIntegerField(default=0, null=False)
    token_id = models.IntegerField(null=False)
    min_time_created = models.IntegerField(default=None)
    max_time_updated = models.IntegerField(default=None)
    SUM_visibility_time = models.IntegerField(default=None)
