from models import *
from django.forms import *
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

class UserForm(ModelForm):
    """email = forms.EmailField(required=True)
    first_name = forms.CharField(label=_("Nombre"),
        max_length=30,
        widget=forms.TextInput,
        error_messages={'required': 'Debe ingresar su nombre',
                        'min_legth': '',
                        'max_legth': '',
        }
    )"""
    class Meta:
        model = User
        fields = ['first_name','last_name','email','password']

class ActaForm(ModelForm):
    class Meta:
        model = Acta
        exclude = ['proyecto_acta']

class TemaForm(ModelForm):
    class Meta:
        model = Tema
        exclude = ['acta_tema']

class ElementoForm(ModelForm):
    class Meta:
        model = Elemento
        exclude = ['usuario_responsable']


"""
from django import forms
from chosen import forms as chosenforms

class BookForm(forms.Form):
    name = forms.CharField(max_length=100)
    quality = chosenforms.ChosenChoiceField(overlay="Select book quality...",
        choices=(('New', 'new'), ('Used', 'used')))
    authors = chosenforms.ChosenModelMultipleChoiceField(queryset=Author.objects.all())
"""