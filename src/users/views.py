from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView


class RegistrationView(CreateView):
    form_class = UserCreationForm
    template_name = "users/register.html"
    success_url = reverse_lazy("chat:index")
