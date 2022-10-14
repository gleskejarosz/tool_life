from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.contrib.auth.models import User
from django.views.generic import CreateView


class RegisterUser(CreateView):
    model = User
    template_name = "form.html"
    form_class = UserCreationForm
    success_url = reverse_lazy("homepage")
