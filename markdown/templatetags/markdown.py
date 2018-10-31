from django import template
import markdown2

register = template.Library()


@register.filter
def markdown(value):
    if not value:
        return value
    return markdown2.markdown(value)
