from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, ButtonHolder

from django.contrib.auth.forms import AuthenticationForm,UserCreationForm

class SearchingForm(forms.Form):
    kind_of_place_options = ((1,'Museos'),(2,'Galerías de Arte'))

    start_point  = forms.CharField(
        required = True,
        label='Especifica el punto de partida',
        max_length=100)
    range_in_Km  = forms.IntegerField(
        required = True,
        label='Especifica un rango de búsqueda en km',
        initial = 1,
        min_value=1,
        max_value=30)
    kind_of_place= forms.ChoiceField(
        required = True,
        initial='',
        label ="Tipo de lugar",
        choices=kind_of_place_options
        )
