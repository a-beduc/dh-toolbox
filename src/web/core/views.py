from django.template.response import TemplateResponse


def home_view(request):
    return TemplateResponse(request, "core/home.html", {})
