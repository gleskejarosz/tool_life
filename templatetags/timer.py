# from datetime import timedelta
# from django import template
#
# register = template.Library()
#
#
# @register.inclusion_tag('gemba/timer.html')
# def render_timer(timer):
#     return {'timer': timer}
#
#
# @register.filter
# def hhmmss(value):
#     if not value:
#         return '00:00'
#     if isinstance(value, timedelta):
#         value = value.total_seconds()
#     minutes, seconds = divmod(round(value), 60)
#     hours, minutes = divmod(minutes, 60)
#     if hours:
#         return '{:n}:{:02n}:{:02n}'.format(hours, minutes, seconds)
#     return '{:02n}:{:02n}'.format(minutes, seconds)
