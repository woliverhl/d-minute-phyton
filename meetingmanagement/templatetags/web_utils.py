from django import template
from django.conf import settings
from django.db.models import Q

register = template.Library()

@register.filter(name='get_codigo_tipo')
def get_codigo_tipo(value):
    if value == 'Compromiso':
        return 'CO'
    elif value == 'Acuerdo':
        return 'AC'
    elif value == 'Desacuerdo':
        return 'DC'
    elif value == 'Duda':
        return 'DU'
    else:
        return 'UNK'