from django.http import HttpResponse
from django.views import View


class OrderAcceptView(View):
    def get(self, request, *args, **kwargs):
        return HttpResponse("something")

