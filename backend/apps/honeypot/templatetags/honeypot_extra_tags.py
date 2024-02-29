from django import template
from urllib.parse import urljoin, urlparse

register = template.Library()


@register.filter(name="slash")
def slash(value):
    return str(value) + "/" if not str(value).endswith("/") else str(value)


@register.filter(name="strip")
def strip(value, arg):
    return value.strip(arg)


@register.filter(name="strip_query")
def strip_query(value):
    # we want to delete the query here
    # we parse the URL and keep everything but the query
    parsed_url = urlparse(value)
    joined = urljoin(value, parsed_url.path)  # retain the path
    joined = urljoin(joined, parsed_url.fragment)  # retain the fragment
    return joined


@register.filter(name="cut")
def cut(value, arg):
    """Removes all values of arg from the given string"""
    return value.replace(arg, '')
