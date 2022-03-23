from django.shortcuts import render


# Create your views here.
def index(request):
    name = request.POST
    context = {'name': name}
    return render(request, 'config/index.html', context)
