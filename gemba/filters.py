from django import template

register = template.Library()


@register.filter
def total_scrap(value):
    temp_val = value.split(' ')
    total = 0

    for val in temp_val:
        total += int(val[:-1])

    return str(total)
