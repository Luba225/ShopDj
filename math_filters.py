from django import template

register = template.Library()

@register.filter
def mul(value, arg):
    """Множить значення на аргумент."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def add(value, arg):
    """Додає аргумент до значення."""
    try:
        return float(value) + float(arg)
    except (ValueError, TypeError):
        return ''