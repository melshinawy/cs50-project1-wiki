from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path('wiki/<str:title>', views.wiki_pages, name='wiki_pages'),
    path('add_edit_entry', views.add_edit_entry, name='add_edit_entry'),
    path('random_page', views.random_page, name='random_page'),
    path('search', views.search, name='search'),
    path('edit/<str:page_title>', views.edit, name='edit'),
]
