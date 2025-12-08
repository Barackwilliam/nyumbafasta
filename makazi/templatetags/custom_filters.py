# makazi/templatetags/custom_filters.py
import re
from django import template

register = template.Library()

@register.filter(name='only_digits')
def only_digits(value):
    """
    Return only digits (0-9) from the given value.
    Example: "Tsh 350,000 /=" -> "350000"
    """
    if value is None:
        return ''
    return re.sub(r'[^0-9]', '', str(value))
