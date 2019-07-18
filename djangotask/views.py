from django.shortcuts import render
from .form import RaterForm


def main_view(request):
    if request.method == 'POST':
        form = RaterForm(request.POST)
        form.save()
        return render(request, 'djangotask/main.html', {'rater': 'done'})
    else:
        form = RaterForm()

    return render(request, 'djangotask/main.html', {'form': form})

