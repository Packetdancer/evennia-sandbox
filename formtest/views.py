from __future__ import unicode_literals
from .form import TestForm
from django.shortcuts import render


def formtest_request(request):
    if not request.user.is_authenticated:
        raise Http404("Not logged in.")

    paxform = TestForm()
    webform_class = paxform.web_form

    if request.method == "POST":
        form = webform_class(request.POST)
        if not form.is_valid():
            render(request, 'formtest.html', {'form': form, 'form_errors': error})

        valid, error = paxform.from_web_form(form)
        if not valid:
            render(request, 'formtest.html', {'form': form, 'form_errors': error})

        values = paxform.serialize()
        paxform.submit(request.user, values)
        return render(request, 'formthanks.html', {'thanks_msg':
                                                   '# Thank you!\n\nYour form **' + values['one'] + '** has been submitted!\n\n'},
                      content_type="text/html")

    form = webform_class(initial=paxform.serialize())
    return render(request, 'formtest.html', {'form': form}, content_type="text/html")