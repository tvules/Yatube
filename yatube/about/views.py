from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    """View-class для статичной страницы 'Об авторе'."""
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    """View-class для статичной страницы 'Технологии'."""
    template_name = 'about/tech.html'
