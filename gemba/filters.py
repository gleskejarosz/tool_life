from django import template

register = template.Library()

#not used
@register.filter
def takt_time(target):
    '''
    Divides the value; target is the divisor.
    Returns empty string on any error.
    '''
    try:
        value = 60
        if target:
            return value / target
    except:
        return ''
