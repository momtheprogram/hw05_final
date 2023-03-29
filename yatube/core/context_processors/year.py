# Для времени в джанге используй `django.utils.timezone`, тогда будет учитываться часовой пояс. Время и разница в часовых поясах это извечная проблема приложений, работающих с пользователями в различных часовых поясах. На первый взгляд подобная мелочь может вызвать довольно много ошибок.
# https://docs.djangoproject.com/en/4.1/ref/utils/#module-django.utils.timezone
# https://stackoverflow.com/questions/10783864/django-1-4-timezone-now-vs-datetime-datetime-now
from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': datetime.now().year
    }
