from django.shortcuts import render


def page_not_found(request, exception):
    # Переменная exception содержит отладочную информацию;
    # выводить её в шаблон пользовательской страницы 404 мы не станем
    return render(request, 'core/404.html', {'path': request.path}, status=404)

# добавить сттус 403
def csrf_failure(request, reason=''):
    return render(request, 'core/403csrf.html')

# должны быть еще вьюхи:
#  1. на обработку 500 ошибки, server_error
#  2. на обработку 403 ошибки, permission_denied
#   соответственно, на обе вьюхи кастомные шаблоны