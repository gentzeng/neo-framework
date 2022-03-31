from django.views import View
from django.shortcuts import render
from rest_framework.reverse import reverse_lazy

# is used by eval()
from . import models  # noqa: F401


class ResourceManageReactWrapper(View):
    template = "pages/react-page.html"
    page = "resource-manage-page.js"
    props = {}

    def get(self, request, **kwargs):
        context = {
            "props": self.props,
            "page": self.page,
        }

        if "resource_id" not in kwargs:
            if context["props"]["listResource"]:
                context["props"]["listResource"]["urls"] = {
                    k: reverse_lazy(
                        v["urlName"],
                        request=request,
                    )
                    for k, v in context["props"]["listResource"]["urlSettings"].items()
                }
            return render(request, self.template, context)

        if (resource_id := kwargs["resource_id"]) is not None:
            if context["props"]["detailResource"]:
                context["props"]["detailResource"]["url"] = reverse_lazy(
                    context["props"]["detailResource"]["urlName"],
                    kwargs={"pk": resource_id},
                    request=request,
                )

                obj_class_name = context["props"]["detailResource"]["type"]
                obj_class = eval(f"models.{obj_class_name}")

                referer_url_id_name = context["props"]["detailResource"].get(
                    "refererUrlIdName", ""
                )
                referer_many_to_many_resource_name = context["props"][
                    "detailResource"
                ].get("refererManyToManyResourceName", "")
                referer_url_id = None

                if referer_url_id_name != "":
                    try:
                        referer_url_id = getattr(
                            obj_class.objects.filter(id=resource_id)[0],
                            referer_url_id_name,
                        )
                    except BaseException:
                        referer_url_id = None

                if referer_many_to_many_resource_name != "":
                    try:
                        obj = obj_class.objects.filter(id=resource_id)[0]
                        many_to_many_parent_qs = getattr(
                            obj, referer_many_to_many_resource_name
                        )
                        many_to_many_parent_qs = many_to_many_parent_qs.values()
                        many_to_many_parent_obj = many_to_many_parent_qs[0]
                        referer_url_id = many_to_many_parent_obj["id"]
                    except BaseException:
                        referer_url_id = None

                referer_url_name = context["props"]["detailResource"]["refererUrlName"]

                context["props"]["detailResource"]["refererUrl"] = reverse_lazy(
                    referer_url_name,
                    kwargs={}
                    if referer_url_name == "root"
                    else {"resource_id": referer_url_id},
                    request=request,
                )

            if context["props"]["listResource"]:
                context["props"]["listResource"]["urls"] = {
                    k: reverse_lazy(
                        v["urlName"],
                        kwargs={v["urlIdName"]: resource_id}
                        if v["urlIdName"] != ""
                        else {},
                        request=request,
                    )
                    for k, v in context["props"]["listResource"]["urlSettings"].items()
                }

        return render(request, self.template, context)


class NewsfeedView(View):
    template = "pages/react-newsfeed-page.html"
    page = "newsfeed-page.js"
    props = {}

    def get(self, request, **kwargs):
        context = {
            "props": self.props,
            "page": self.page,
        }
        if (newsfeed_base_id := kwargs["newsfeed_base_id"]) is not None:
            urlSetting = context["props"]["urlSetting"]
            context["props"]["url"] = reverse_lazy(
                urlSetting["urlName"],
                kwargs={urlSetting["urlIdName"]: newsfeed_base_id}
                if urlSetting["urlIdName"] != ""
                else {},
                request=request,
            )
        return render(request, self.template, context)
