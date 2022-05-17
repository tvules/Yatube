from django.utils import timezone


def year(request):
    """Возвращает переменную с текущим годом."""
    return {
        'year': timezone.now().year
    }
