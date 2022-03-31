from rest_framework.routers import DefaultRouter
from django.urls import path, include

from .views import (
    AuthorListView,
    newsfeed_selection_view,
    newsfeed_create_view,
    Dashboard,
    CaseStudyManage,
    CaseStudyRoundManage,
    NewsfeedBaseManage,
    NewsfeedFbView,
    PostManualManage,
)

from .api import (
    api_root,
    CaseStudyViewSet,
    CaseStudyRoundViewSet,
    NewsfeedBaseViewSet,
    PostManualViewSet,
    NewsfeedFbViewSet,
)

router = DefaultRouter()
router.register(r"case-study", CaseStudyViewSet)
router.register(r"case-study-round", CaseStudyRoundViewSet)
router.register(r"newsfeed-base", NewsfeedBaseViewSet)
router.register(r"post-manual", PostManualViewSet)

urlpatterns = [
    path("", include(router.urls)),
    # nested apis
    path(
        "case-study/<int:case_study_id>/case-study-round/",
        CaseStudyRoundViewSet.as_view({"get": "list", "post": "create"}),
        name="casestudy-casestudyround-list",
    ),
    path(
        "case-study/<int:case_study_id>/case-study-round/<int:pk>/",
        CaseStudyRoundViewSet.as_view({"get": "retrieve"}),
        name="casestudy-casestudyround-detail",
    ),
    path(
        "case-study-round/<int:case_study_round_id>/newsfeed-base/",
        NewsfeedBaseViewSet.as_view(
            {
                "get": "list",
                "post": "create",
                "put": "update",
                "patch": "partial_update",
            }
        ),
        name="casestudyround-newsfeedbase-list",
    ),
    path(
        "case-study-round/<int:case_study_round_id>/newsfeed-base/<int:pk>/",
        NewsfeedBaseViewSet.as_view({"get": "retrieve"}),
        name="casestudyround-newsfeedbase-detail",
    ),
    path(
        "newsfeed-base/<int:newsfeed_base_id>/post-manual/",
        PostManualViewSet.as_view(
            {
                "get": "list",
                "post": "create",
                "put": "update",
                "patch": "partial_update",
            }
        ),
        name="newsfeedbase-postmanual-list",
    ),
    path(
        "newsfeed-base/<int:newsfeed_base_id>/post-manual/<int:pk>/",
        PostManualViewSet.as_view(
            {"get": "retrieve", "put": "update", "patch": "partial_update"}
        ),
        name="newsfeedbase-postmanual-detail",
    ),
    # manage paths
    path(
        "case-study-manage/<int:resource_id>/",
        CaseStudyManage.as_view(),
        name="casestudy-manage",
    ),
    path(
        "case-study-round-manage/<int:resource_id>/",
        CaseStudyRoundManage.as_view(),
        name="casestudyround-manage",
    ),
    path(
        "newsfeed-base-manage/<int:resource_id>/",
        NewsfeedBaseManage.as_view(),
        name="newsfeedbase-manage",
    ),
    path(
        "post-manual-manage/<int:resource_id>/",
        PostManualManage.as_view(),
        name="postmanual-manage",
    ),
    # newsfeed views
    path(
        "newsfeed-base/<int:newsfeed_base_id>/newsfeed/fb/",
        NewsfeedFbViewSet.as_view(
            {
                "get": "list",
            }
        ),
        name="newsfeedbase-newsfeed-fb",
    ),
    path(
        "newsfeed/<int:newsfeed_base_id>/fb/",
        NewsfeedFbView.as_view(),
        name="newsfeed-fb",
    ),
    path("api/utils-newsfeed/", api_root),
    path("authors/", AuthorListView.as_view(), name="author-list"),
    path("newsfeed/creation", newsfeed_selection_view, name="newsfeedbase-manage"),
    path("newsfeed/create", newsfeed_create_view, name="newsfeed/create"),
    path("dashboard/", Dashboard.as_view(), name="root"),
]
