from typing import Optional

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.utils.http import is_safe_url
from django.views.generic import ListView

from rest_framework import status
from rest_framework.decorators import api_view

from .serializer import (
    PostManualSerializer,
    NewsfeedBaseCreationSerializer,
)
from .forms import (
    NewsfeedBaseCreationForm,
)
from .models import (
    Author,
    PostManual,
)

from .views_utils import (
    ResourceManageReactWrapper,
    NewsfeedView,
)


DEFAULT_NEWSFEED_SIZE = settings.DEFAULT_NEWSFEED_SIZE
DEFAULT_LIKE_PROBABILITY = settings.DEFAULT_LIKE_PROBABILITY
ALLOWED_HOSTS = settings.ALLOWED_HOSTS
LOGIN_URL = settings.LOGIN_URL

EMPTY_DETAIL_RESOURCE = {}

EMPTY_LIST_RESOURCE = {}


def home_view(request, *args, **kwargs):
    return render(request, "pages/home.html", context={}, status=status.HTTP_200_OK)


class Dashboard(ResourceManageReactWrapper):
    style = {
        "textColor": "text-white",
        "color": "primary",
    }

    detail_resource = EMPTY_DETAIL_RESOURCE

    list_resource = {
        "viewType": "cards",
        "style": style,
        "type": "CaseStudy",
        "urlSettings": {
            "resource": {
                "urlName": "casestudy-list",
                "urlIdName": "",
            },
        },
        "excludeFromResource": [
            "id",
            "user",
            "name",
            "description",
            "case_study_rounds",
            # "resource_url",
            # "manage_url",
        ],
        "createFields": {
            "name": {"htmlTag": "input", "type": "text"},
            "description": {"htmlTag": "textarea"},
        },
    }

    props = {
        "allowedHosts": settings.ALLOWED_HOSTS,
        "style": style,
        "login": LOGIN_URL,
        "detailResource": detail_resource,
        "listResource": list_resource,
    }


class CaseStudyManage(ResourceManageReactWrapper):
    style = {
        "textColor": "text-white",
        "color": "success",
    }
    detail_resource = {
        "viewType": "",
        "style": style,
        "type": "CaseStudy",
        "urlName": "casestudy-detail",
        "refererUrlName": "root",
        "refererUrlIdName": "",
        "refererManyToManyResourceName": "",
        "excludeFromResource": [
            "id",
            "user",
            "name",
            "description",
            "resource_url",
            "manage_url",
        ],
    }
    list_resource = {
        "viewType": "cards",
        "style": style,
        "type": "CaseStudyRound",
        "urlSettings": {
            "resource": {
                "urlName": "casestudy-casestudyround-list",
                "urlIdName": "case_study_id",
            },
        },
        "excludeFromResource": [
            "id",
            "user",
            "name",
            "description",
            "newsfeed_base",
            # "resource_url",
            # "manage_url",
        ],
        "createFields": {
            "name": {"htmlTag": "input", "type": "text"},
            "description": {"htmlTag": "textarea"},
        },
    }
    props = {
        "allowedHosts": settings.ALLOWED_HOSTS,
        "style": style,
        "login": LOGIN_URL,
        "detailResource": detail_resource,
        "listResource": list_resource,
    }


class CaseStudyRoundManage(ResourceManageReactWrapper):
    style = {
        "textColor": "text-dark",
        "color": "warning",
    }
    detail_resource = {
        "viewType": "",
        "style": style,
        "type": "CaseStudyRound",
        "urlName": "casestudyround-detail",
        "refererUrlName": "casestudy-manage",
        "refererUrlIdName": "case_study_id",
        "refererManyToManyResourceName": "",
        "excludeFromResource": [
            "id",
            "user",
            "name",
            "description",
            "resource_url",
            "manage_url",
        ],
    }
    list_resource = {
        "viewType": "cards",
        "style": style,
        "type": "NewsfeedBase",
        "urlSettings": {
            "resource": {
                "urlName": "casestudyround-newsfeedbase-list",
                "urlIdName": "case_study_round_id",
            },
        },
        "excludeFromResource": [
            "id",
            "user",
            "name",
            "description",
            "post_manuals",
            "fixed_post_set",
            "post_order",
            # "resource_url",
            # "manage_url",
        ],
        "createFields": {
            "name": {"htmlTag": "input", "type": "text"},
            "description": {"htmlTag": "textarea"},
            "newsfeed_size": {"htmlTag": "input", "type": "number"},
            "fixed_post_set": {"htmlTag": "input", "type": "file"},
        },
    }

    props = {
        "allowedHosts": settings.ALLOWED_HOSTS,
        "style": style,
        "login": LOGIN_URL,
        "detailResource": detail_resource,
        "listResource": list_resource,
    }


class NewsfeedBaseManage(ResourceManageReactWrapper):
    style = {
        "textColor": "text-white",
        "color": "dark",
    }
    detail_resource = {
        "viewType": "",
        "style": style,
        "type": "NewsfeedBase",
        "urlName": "newsfeedbase-detail",
        "refererUrlName": "casestudyround-manage",
        "refererUrlIdName": "case_study_round_id",
        "refererManyToManyResourceName": "",
        "excludeFromResource": [
            "id",
            "user",
            "name",
            "description",
            "resource_url",
            "manage_url",
        ],
    }
    list_resource = {
        "viewType": "postTable",
        "style": style,
        "type": "PostManual",
        "urlSettings": {
            "resource": {
                "urlName": "newsfeedbase-postmanual-list",
                "urlIdName": "newsfeed_base_id",
            },
            "newsfeedBase": {
                "urlName": "newsfeedbase-detail",
                "urlIdName": "pk",
            },
        },
        "excludeFromResource": [
            # "id",
            "user",
            "type",
            "newsfeed_base",
            "article_url",
            "image_url",
            "splash_image_url",
            "time_created",
            "time_updated",
            "resource_url",
            "manage_url",
        ],
        "createFields": {
            # "name": {"htmlTag": "input", "type": "text"},
            # "description": {"htmlTag": "textarea"},
            "article_url": {"htmlTag": "input", "type": "url"},
            "image_url": {"htmlTag": "input", "type": "url"},
            "splash_image_url": {"htmlTag": "input", "type": "url"},
            "header": {"htmlTag": "textarea"},
            "title": {"htmlTag": "textarea"},
            "content": {"htmlTag": "textarea"},
            "first_reaction": {"htmlTag": "input", "type": "number"},
            "second_reaction": {"htmlTag": "input", "type": "number"},
            "third_reaction": {"htmlTag": "input", "type": "number"},
        },
    }

    props = {
        "allowedHosts": settings.ALLOWED_HOSTS,
        "style": style,
        "login": LOGIN_URL,
        "detailResource": detail_resource,
        "listResource": list_resource,
    }


class PostManualManage(ResourceManageReactWrapper):
    style = {
        "textColor": "text-dark",
        "color": "danger",
    }
    detail_resource = {
        "viewType": "",
        "style": style,
        "type": "PostManual",
        "urlName": "postmanual-detail",
        "refererUrlName": "newsfeedbase-manage",
        "refererUrlIdName": "",
        "refererManyToManyResourceName": "newsfeed_base",
        "excludeFromResource": [
            "id",
            "user",
            "name",
            "description",
            "resource_url",
            "manage_url",
        ],
    }

    props = {
        "allowedHosts": settings.ALLOWED_HOSTS,
        "style": style,
        "login": LOGIN_URL,
        "detailResource": detail_resource,
        "listResource": EMPTY_LIST_RESOURCE,
    }


class NewsfeedFbView(NewsfeedView):
    exclude_from_resource = [
        "id",
        "user",
        "name",
        "description",
        "resource_url",
        "manage_url",
    ]
    props = {
        "excludeFromResource": exclude_from_resource,
        "urlSetting": {
            "urlName": "newsfeedbase-newsfeed-fb",
            "urlIdName": "newsfeed_base_id",
        },
    }


class AuthorListView(ListView):
    template_name = "author/list.html"
    queryset = Author.objects.all()


def newsfeed_selection_view(request, *args, **kwargs):
    """
    REST API endpoint to show
    """
    user = request.user
    if not user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=status.HTTP_401_UNAUTHORIZED)
        return redirect(settings.LOGIN_URL)
    posts = PostManual.objects.all()
    newsfeed = PostManualSerializer(posts, many=True).data
    context = {
        "newsfeed": newsfeed,
    }

    return render(
        request, "newsfeedCreation/creation.html", context, status=status.HTTP_200_OK
    )


@api_view(["POST"])
def newsfeed_create_view(request, *args, **kwargs):
    """
    REST API endpoint to create new newsfeed
    """
    user = request.user
    if not user.is_authenticated:
        user = None
        if request.is_ajax():
            return JsonResponse({}, status=status.HTTP_401_UNAUTHORIZED)
        return redirect(settings.LOGIN_URL)
    form = NewsfeedBaseCreationForm(request.POST or None)
    if form.is_valid():
        newsfeed_obj = form.save(commit=False)
        newsfeed_obj.user = user
        newsfeed_obj.save()
        if request.is_ajax():
            return JsonResponse(
                NewsfeedBaseCreationSerializer(newsfeed_obj).data,
                status=status.HTTP_201_CREATED,
            )

        next_url: Optional[str] = request.POST.get("next") or None
        if next_url is not None and is_safe_url(next_url, ALLOWED_HOSTS):
            return redirect(next_url)

    if form.errors:
        if request.is_ajax():
            return JsonResponse(form.errors, status=status.HTTP_400_BAD_REQUEST)

    return render(
        request, "newsfeedCreation/create.html", {}, status=status.HTTP_200_OK
    )
