from django.shortcuts import render
from django.http import HttpResponseRedirect
from . import util
from markdown2 import Markdown
from django import forms
from django.urls import reverse
from random import randint
from django.utils.safestring import mark_safe

class WikiEntry(forms.Form):
    title = forms.CharField(widget=forms.TextInput(attrs={'placeholder': "Title"}))
    content = forms.CharField(widget=forms.Textarea(attrs={'placeholder': "Markdown content..."}))
    edit_type = forms.CharField(widget=forms.HiddenInput())

def index(request):
    return render(request, "encyclopedia/index.html", {
        "entries": util.list_entries()
    })

def wiki_pages(request, title):
    entry = util.get_entry(title)
    if entry is None:
        context = {
            'title': 'Error! Page Not Found',
            'message_title': 'Error! Page Not Found',
            'message': mark_safe(f'A page with the name <em>{title}</em> could not be found.')
        }
        return render(request, 'encyclopedia/messages.html', context)
    else:
        all_titles = util.list_entries()
        all_titles_lower = [x.lower() for x in all_titles]
        title = all_titles[all_titles_lower.index(title.lower())]        

        context = {
            'title': title,
            'body': mark_safe(Markdown().convert(entry))
        }
    return render(request, 'encyclopedia/entries.html', context)

def add_edit_entry(request):
    if request.method == 'GET':
        form = WikiEntry(initial={'edit_type':'add'})
        form.fields['title'].widget.attrs['placeholder'] = "Title"
        form.fields['content'].widget.attrs['placeholder'] = "Markdown content..."
        return render(request, 'encyclopedia/add_edit_entry.html', {
        'form': form
            })
    else:
        form = WikiEntry(request.POST)

        if form.is_valid():
            title = form.cleaned_data['title']
            content = form.cleaned_data['content']
            edit_type = form.cleaned_data['edit_type']

            if edit_type == 'edit':
                if not util.get_entry(title):
                    context = {
                        'title': 'Failed To Edit Entry',
                        'message_title': 'Error: Entry Not Edited',
                        'message': mark_safe(f'Entry could not be edited in the encyclopedia as an entry with the name <em>{title}</em> does not exist.')
                    }
                else:
                    util.save_entry(title, content)
                    return HttpResponseRedirect(reverse('wiki_pages', args=(title,)))
            else:
                if util.get_entry(title):
                    
                    context = {
                        'title': 'Failed To Add New Entry',
                        'message_title' : 'Error: Entry Not Added',
                        'message' : mark_safe(f'Entry could not be added to the encyclopedia as an entry with the name <em>{title}</em> already exists.')
                    }
                else:
                    content = f'# {title}\n' + content
                    util.save_entry(title, content)
                    return HttpResponseRedirect(reverse('wiki_pages', args=(title,)))
        else:
            context = {  
                'title': 'Failed To Add New Entry',              
                'message_title' : 'Opps!',
                'message' : f'Something went wrong storing the entry to the encyclopedia.'
            }

        return render(request, 'encyclopedia/messages.html', context)

def edit(request, page_title):
    if request.method == 'GET':  
        page_content = util.get_entry(page_title)
        edit_form = WikiEntry(initial={'title': page_title, 'content': page_content, 'edit_type': 'edit'})
        edit_form.fields['title'].widget.attrs['readonly'] = True

        return render(request, 'encyclopedia/add_edit_entry.html', {
            'form': edit_form,
            'title': page_title + ' - edit'
        })

def random_page(request):
    random_page_title = util.list_entries()[randint(0,len(util.list_entries()) - 1)]
    return HttpResponseRedirect(reverse('wiki_pages', args=(random_page_title,)))

def search(request):
    if request.method == 'POST':
        search_query = request.POST['q']
        entry = util.get_entry(search_query)

        if entry is not None:
            return HttpResponseRedirect(reverse('wiki_pages', args=(search_query,)))

        else:
            similar_entries = [title for title in util.list_entries() if search_query.lower() in title.lower()]
            context = {
                'search_query': search_query,
                'similar_entries': similar_entries
                }
            return render(request, 'encyclopedia/search_results.html', context)

    