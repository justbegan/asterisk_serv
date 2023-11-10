from rest_framework.views import APIView, Response, status
from django.core.mail import send_mail
from .models import Statements
from rest_framework.authentication import SessionAuthentication
import logging
from django.shortcuts import render

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'mail.html')


class CsrfExemptSessionAuthentication(SessionAuthentication):
    def enforce_csrf(self, request):
        return None


class Send_email(APIView):
    authentication_classes = (CsrfExemptSessionAuthentication,)

    def post(self, request):
        try:
            text = request.data.get('text')
            phone = request.data.get('phone')
        except:
            logger.error("Нет данных")
            return Response({"status": False}, status=status.HTTP_400_BAD_REQUEST)

        subject = phone
        message = text
        from_email = 'noreply@sakha.gov.ru'
        recipient_list = ['rpgu@sakha.gov.ru']
        try:
            st = Statements(text=text, phone=phone)
            st.save()
        except:
            logger.error("Ошибка сохранения")
            return Response({"status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except NameError as e:
            logger.error("Ошибка отправки сообщения")
            logger.error(e)
            return Response({"status": False}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        return Response({"status": True})
