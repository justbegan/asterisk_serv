from rest_framework.views import APIView
from .services.synthesis import create_voice


class Get_file(APIView):
    def get(self, request):
        text = request.GET.get("text")
        return create_voice(text)
