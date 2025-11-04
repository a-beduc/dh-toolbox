from django.contrib.auth import authenticate, login, logout
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_safe

from accounts.services import create_account
from web.accounts.forms import LoginForm, RegisterForm


@require_safe
def login_view(request):
    form = LoginForm()
    context = {"form": form}
    return TemplateResponse(request, "accounts/login.html", context)


@csrf_protect
def login_submit_view(request):
    if not request.method == "POST":
        redirect('accounts:login')

    form = LoginForm(request.POST)
    if not form.is_valid():
        context = {"form": form}
        return TemplateResponse(
            request, "accounts/login.html", context=context, status=400
        )

    username = form.cleaned_data["username"]
    password = form.cleaned_data["password"]
    user = authenticate(request, username=username, password=password)

    if user is None:
        context = {"form": form}
        return TemplateResponse(
            request, "accounts/login.html", context=context, status=401
        )

    login(request, user)
    return redirect('core:home')


@require_safe
def logout_view(request):
    logout(request)
    return redirect('accounts:login')


@require_safe
def register_view(request):
    form = RegisterForm()
    context = {"form": form}
    return TemplateResponse(request, 'accounts/register.html', context=context)


@csrf_protect
def register_submit_view(request):
    if request.method != 'POST':
        redirect('accounts:register')

    form = RegisterForm(request.POST)
    if not form.is_valid():
        context = {"form": form}
        return TemplateResponse(
            request, "accounts/register.html", context=context, status=400
        )

    username = form.cleaned_data["username"]
    email = form.cleaned_data["email"]
    password1 = form.cleaned_data["password1"]
    password2 = form.cleaned_data["password2"]

    create_account(
        username=username,
        password1=password1,
        password2=password2,
        email=email
    )

    return redirect('accounts:login')
