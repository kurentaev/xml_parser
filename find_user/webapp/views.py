from django.views.generic import ListView
from webapp.models import Individuals


class IndexView(ListView):
    template_name = 'index.html'
    model = Individuals
    context_object_name = 'mymodels'

