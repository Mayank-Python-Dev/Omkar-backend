from django.shortcuts import render



# def home(request):
#     return render_nextjs_page_sync(request)


def home(request):
    # return render_nextjs_page_sync(request)
    return render(request, 'index.html')



# def dashboard(request):
#     # return render_nextjs_page_sync(request)
#     return render(request, 'dashboard.html')
