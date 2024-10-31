from django.shortcuts import render
from shop.models import products
from django.db.models import Q
def search_products(request):
    if(request.method=="POST"):
        query=""
        p=None
        query=request.POST['q']
        print(query)
        if(query):
            p=products.objects.filter(Q(name__icontains=query) | Q(desc__icontains=query))

    return render(request,'search.html',{'product':p,'q':query})
