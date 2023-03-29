from django.views.generic.base import TemplateView

# не должно оставаться учебных комментариев. засоряется код
class AboutAuthorView(TemplateView):
    # В переменной template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
