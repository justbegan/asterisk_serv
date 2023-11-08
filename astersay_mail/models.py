from django.db import models


class Statements(models.Model):
    text = models.TextField(blank=True, null=True)
    phone = models.TextField(blank=True, null=True)
    create_time = models.DateTimeField('Дата добавления', auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.phone}"

    class Meta:
        verbose_name = "Заявка"
        verbose_name_plural = "Заявки"
