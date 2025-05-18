from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.

class HomeView(TemplateView):
    template_name = 'frontend/index.html'

class CrudTestView(TemplateView):
    template_name = 'frontend/crud_test.html'
