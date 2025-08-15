from django.db import models

from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from wagtail.models import Page
from wagtail.admin.panels import FieldPanel

from wagtail.fields import RichTextField

class NewsArticle(Page):
    title = models.CharField(max_length=255)  
    publication_date = models.DateField()
    summary = models.TextField(max_length=200)
    source_url = models.URLField()

    # Define admin panels for Wagtail admin interface
    content_panels = Page.content_panels + [
        FieldPanel('publication_date'),
        FieldPanel('summary'),
        FieldPanel('source_url'),
    ]

    # Ensure articles are sorted by publication date in queries
    class Meta:
        ordering = ['-publication_date']

    def __str__(self):
        return self.title

class NewsListPage(Page):
    # Optional: Add a field for introductory text
    intro = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('intro'),
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        # Get all published NewsArticle pages
        articles = NewsArticle.objects.live().descendant_of(self)

        # Add pagination
        paginator = Paginator(articles, 10)  # 10 articles per page
        page = request.GET.get('page')
        try:
            articles = paginator.page(page)
        except PageNotAnInteger:
            articles = paginator.page(1)
        except EmptyPage:
            articles = paginator.page(paginator.num_pages)

        context['articles'] = articles
        return context

