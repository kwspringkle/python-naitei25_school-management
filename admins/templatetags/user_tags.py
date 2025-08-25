from django import template

register = template.Library()

@register.inclusion_tag('admins/partials/role_badge.html', takes_context=True)
def user_role_badge(context, user):
    return {
        'user': user,
    }