from django.http.request import QueryDict
from django.db.utils import IntegrityError as DjangoIntegrityError
from django.forms.models import model_to_dict

from rest_framework import viewsets, permissions, status
from rest_framework.reverse import reverse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.generics import get_object_or_404

from knox.auth import TokenAuthentication

from .models import (
    CaseStudy,
    CaseStudyRound,
    NewsfeedBase,
    PostManual,
    ScrapedPost,
)

from .serializer import (
    CaseStudySerializer,
    CaseStudyRoundSerializer,
    NewsfeedBaseSerializer,
    PostManualSerializer,
    NewsfeedFbSerializer,
)
from .utils import IsOwnerOrReadOnly


@api_view(["Get"])
def api_root(request, format=None):
    return Response(
        {
            "users": reverse("user-list", request=request, format=format),
            "case_studies": reverse("casestudy-list", request=request, format=format),
        }
    )


class CaseStudyViewSet(viewsets.ModelViewSet):
    """ """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = CaseStudySerializer
    queryset = CaseStudy.objects.filter()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            serializer.data, status=status.HTTP_201_CREATED, headers=headers
        )

    def get_queryset(self, *args, **kwargs):
        """
        Filter case studies for user
        """
        queryset_user = self.queryset.filter(user=self.request.user)

        return queryset_user

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CaseStudyRoundViewSet(viewsets.ModelViewSet):
    """ """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = CaseStudyRoundSerializer
    foreign_class = CaseStudy
    queryset = CaseStudyRound.objects.filter()

    def get_queryset(self):
        """
        Filter case studies for user
        """
        queryset = self.queryset.filter(user=self.request.user)

        if (case_study_id := self.kwargs.get("case_study_id")) is not None:
            queryset = queryset.filter(case_study__id=case_study_id)

        return queryset

    def perform_create(self, serializer):
        # todo: handle case if case_study_id not given
        case_study_id = self.kwargs.get("case_study_id")
        queryset = self.foreign_class.objects.filter(
            user=self.request.user, id=case_study_id
        )

        if queryset:
            case_study = list(queryset)[0]
            serializer.save(user=self.request.user, case_study=case_study)


class NewsfeedBaseViewSet(viewsets.ModelViewSet):
    """ """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NewsfeedBaseSerializer
    foreign_class = CaseStudyRound
    queryset = NewsfeedBase.objects.all()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_queryset(self):
        """
        Filter case studies for user
        """
        queryset = self.queryset.filter(user=self.request.user)

        if (case_study_round_id := self.kwargs.get("case_study_round_id")) is not None:
            queryset = queryset.filter(case_study_round__id=case_study_round_id)

        return queryset

    def perform_create(self, serializer):
        case_study_round_id = self.kwargs.get("case_study_round_id")
        queryset_foreign = self.foreign_class.objects.filter(
            user=self.request.user, id=case_study_round_id
        )

        if queryset_foreign:
            case_study_round = list(queryset_foreign)[0]
            queryset = self.queryset.filter(case_study_round__id=case_study_round_id)
            if queryset:
                pass
            else:
                serializer.save(
                    user=self.request.user, case_study_round=case_study_round
                )


class PostManualViewSet(viewsets.ModelViewSet):
    """ """

    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated, IsOwnerOrReadOnly)
    serializer_class = PostManualSerializer
    foreign_class = NewsfeedBase
    queryset = PostManual.objects.filter()

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def get_object(self):
        """
        Returns the object the view is displaying.
        You may want to override this if you need to provide non-standard
        queryset lookups.  Eg if objects are referenced using multiple
        keyword arguments in the url conf.
        """
        queryset = self.filter_queryset(self.get_queryset())

        # Perform the lookup filtering.
        lookup_url_kwarg = self.lookup_url_kwarg or self.lookup_field

        filter_kwargs = {self.lookup_field: self.kwargs[lookup_url_kwarg]}
        obj = get_object_or_404(queryset, **filter_kwargs)

        # May raise a permission denied
        self.check_object_permissions(self.request, obj)

        return obj

    def get_queryset(self, ids=None):
        queryset = self.queryset.filter(user=self.request.user)

        if (newsfeed_base_id := self.kwargs.get("newsfeed_base_id")) is not None:
            queryset = queryset.filter(newsfeed_base__id=newsfeed_base_id)
            if ids:
                queryset = queryset.filter(id__in=ids)

        return queryset

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        if isinstance(kwargs.get("data", {}), list):
            kwargs["many"] = True

            return super(PostManualViewSet, self).get_serializer(*args, **kwargs)

        serializer_class = self.get_serializer_class()
        kwargs.setdefault("context", self.get_serializer_context())
        if self.request.method == "GET":
            return serializer_class(*args, **kwargs)

        data_with_newfeed_base = self.request.data.copy()
        if isinstance(data_with_newfeed_base, QueryDict):
            data_with_newfeed_base["newsfeed_base"] = kwargs.get("newsfeed_base_id")
        else:
            data_with_newfeed_base["newsfeed_base"] = [kwargs.get("newsfeed_base_id")]

        kwargs.pop("newsfeed_base_id", None)
        kwargs["data"] = data_with_newfeed_base

        return serializer_class(*args, **kwargs)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        serializer = None
        newsfeed_base_id = self.kwargs.get("newsfeed_base_id")

        if (ids := self.validate_list_ids(request.data)) is not None:
            instances = self.get_queryset(ids=ids)
            serializer = self.get_serializer(
                instances,
                data=request.data,  # .update({"newsfeed_base_id" : newsfeed_base_id}),
                partial=partial,
                many=True,
                newsfeed_base_id=newsfeed_base_id,
            )
        else:
            instances = self.get_object()
            serializer = self.get_serializer(
                instances,
                data=request.data,
                partial=partial,
                newsfeed_base_id=newsfeed_base_id,
            )

        serializer.is_valid(raise_exception=True)

        self.perform_update(serializer)

        return Response(serializer.data)

    def validate_list_ids(self, data):
        if not isinstance(data, list):
            return None

        id_list = [int(x["id"]) for x in data]

        if len(id_list) != len(set(id_list)):
            raise ValidationError("Multiple updates to a single id found")

        return id_list

    def create(self, request, *args, **kwargs):
        response_data = None
        newsfeed_base_id = self.kwargs.get("newsfeed_base_id")

        serializer = self.get_serializer(
            data=request.data, newsfeed_base_id=newsfeed_base_id
        )

        serializer.is_valid(raise_exception=True)
        try:
            self.perform_create(serializer, newsfeed_base_id=newsfeed_base_id)
            response_data = serializer.data
        except DjangoIntegrityError:
            # Since we defined a UniqueConstraint on PostManual, this exception means
            # , a post with the request data in question does already exist.
            response_data = self.update_existing_post_with_newsfeed_base_id(
                request, newsfeed_base_id=newsfeed_base_id
            )

        headers = self.get_success_headers(response_data)
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_create(self, serializer, **kwargs):
        serializer.save(user=self.request.user)

    def update_existing_post_with_newsfeed_base_id(
        self, request, newsfeed_base_id=None
    ):
        existing_post = self.get_existing_post(request)

        if newsfeed_base_id is not None:
            existing_post.newsfeed_base.add(newsfeed_base_id)
            existing_post.save()

        return self.get_response_data_for_updated_existing_post(request, existing_post)

    def get_existing_post(self, request):
        query_filter = request.data.dict()
        del query_filter["foreignKey"]

        return PostManual.objects.filter(**query_filter).first()

    def get_response_data_for_updated_existing_post(self, request, existing_post):
        response_data = model_to_dict(existing_post)
        response_data["image"] = request.build_absolute_uri(response_data["image"].url)
        response_data["splash_image"] = request.build_absolute_uri(
            response_data["splash_image"].url
        )
        response_data["time_created"] = response_data["time_created"].strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        response_data["time_updated"] = response_data["time_updated"].strftime(
            "%Y-%m-%dT%H:%M:%S.%fZ"
        )
        response_data["newsfeed_base"] = [
            nfb.pk for nfb in response_data["newsfeed_base"]
        ]

        return response_data


class NewsfeedFbViewSet(viewsets.ModelViewSet):
    authentication_classes = (TokenAuthentication,)
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = NewsfeedFbSerializer
    foreign_class = NewsfeedBase
    queryset = ScrapedPost.objects.filter()

    def get_queryset(self):
        """
        Get the newsfeed
        """
        # Todo: how to get the user?
        queryset = ScrapedPost.objects.none()

        if (newsfeed_base_id := self.kwargs.get("newsfeed_base_id")) is not None:
            queryset = self.queryset.filter(newsfeed_base__id=newsfeed_base_id)

        return queryset
