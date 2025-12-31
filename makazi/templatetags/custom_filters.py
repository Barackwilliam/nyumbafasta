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





# makazi/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def only_digits(value):
    """Extract only digits from a string"""
    if value is None:
        return ""
    
    # If it's already a number, return it
    if isinstance(value, (int, float)):
        return str(value)
    
    # Extract digits from string
    return ''.join(filter(str.isdigit, str(value)))

@register.filter
def format_currency(value):
    """Format number as currency with commas"""
    if value is None:
        return "0"
    
    try:
        # Try to convert to int
        num = int(''.join(filter(str.isdigit, str(value))))
        return f"{num:,}"
    except:
        return str(value)






# makazi/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def dict_lookup(dictionary, key):
    """Get value from dictionary by key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key, key)
    
    # If it's a list of tuples like AMENITIES_CHOICES
    if isinstance(dictionary, (list, tuple)):
        for k, v in dictionary:
            if k == key:
                return v
    return key



# makazi/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    """Divide the value by the argument"""
    try:
        return float(value) / float(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0

@register.filter
def percentage(value, total=100):
    """Convert to percentage"""
    try:
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError, ZeroDivisionError):
        return 0