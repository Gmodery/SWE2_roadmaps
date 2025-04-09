from django import template

register = template.Library()

@register.filter
def index(sequence, pos):
    try:
        return sequence[pos]
    except (IndexError, TypeError):
        return None
