from datetime import datetime


def year(request):
    """Добавляет переменную с текущим годом."""
    return {
        'year': datetime.now().year
    }
