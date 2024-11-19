from django.shortcuts import render


class Review:
    def reviews_page(self, request):
        return render(request, 'dummy.html')
