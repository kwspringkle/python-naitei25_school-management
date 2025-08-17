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


@register.filter
def count_present(records):
    """
    Count number of present records
    Usage: {{ records|count_present }}
    """
    if not records:
        return 0
    return sum(1 for record in records if record.status)


@register.filter
def count_absent(records):
    """
    Count number of absent records
    Usage: {{ records|count_absent }}
    """
    if not records:
        return 0
    return sum(1 for record in records if not record.status)


@register.filter
def calculate_percentage(present_count, total_count):
    """
    Calculate attendance percentage
    Usage: {{ present_count|calculate_percentage:total_count }}
    """
    if not total_count or total_count == 0:
        return 0
    return round((present_count / total_count) * 100, 1)