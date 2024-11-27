from django import template
from django.utils.timesince import timesince
from django.utils.timezone import now

register = template.Library()


@register.filter
def custom_timesince(value):
    if not value:
        return ''
    now_time = now()
    time_diff = now_time - value
    if time_diff.days == 0:
        if time_diff.seconds < 60:
            return "Just now"
        elif time_diff.seconds < 3600:
            return f"{int(time_diff.seconds // 60)} minutes ago"
        else:
            return f"{int(time_diff.seconds // 3600)} hours ago"
    elif time_diff.days == 1:
        return "Yesterday"
    elif time_diff.days < 7:
        return f"{int(time_diff.days)} days ago"
    else:
        return timesince(value)

