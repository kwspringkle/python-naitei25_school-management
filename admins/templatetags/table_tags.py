from django import template
from urllib.parse import urlencode

register = template.Library()

@register.inclusion_tag('admins/partials/sortable_column.html', takes_context=True)
def sortable_column(context, column_name, display_name):
    request = context['request']
    get_params = request.GET.copy()
    current_sort = get_params.get('sort')
    current_dir = get_params.get('dir', 'asc')

    next_dir = 'desc' if current_sort == column_name and current_dir == 'asc' else 'asc'
    get_params['sort'] = column_name
    get_params['dir'] = next_dir

    url = f"?{urlencode(get_params)}"

    return {
        'display_name': display_name,
        'url': url,
        'is_sorted': current_sort == column_name,
        'current_dir': current_dir,
    }