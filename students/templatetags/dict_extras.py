from django import template

register = template.Library()

@register.filter
def lookup(dictionary, key):
    """
    Template filter to lookup a key in a dictionary
    Usage: {{ dict|lookup:key }}
    """
    if dictionary and key:
        return dictionary.get(key)
    return None