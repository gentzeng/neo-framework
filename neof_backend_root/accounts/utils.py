from django.views import View
from django.shortcuts import render


class ReactWrapper(View):
    template = "pages/react-page.html"
    page = "auth-page.js"
    props = {}

    def get(self, request):
        context = {"props": self.props, "page": self.page}

        return render(request, self.template, context)
