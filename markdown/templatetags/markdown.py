from django import template
from django.utils.html import urlize
from ..parser import MarkdownParser
import re

register = template.Library()


@register.filter
def markdown(value):
    if not value:
        return value

    md = MarkdownParser(value)

    return md.as_html()


@register.filter
def safe_urlize(text, trim_url_limit=None, nofollow=False, autoescape=False):
    result = urlize(text, trim_url_limit=trim_url_limit, nofollow=nofollow, autoescape=autoescape)

    result = re.sub(r'<a href="<a href="([^\"]*)">([^\<]*)</a>">',
                    r'<a href="\1">', result)

    return result