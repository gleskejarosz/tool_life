from django.db import models


LI = "Pokoj dzienny"
BA = "Łazienka"
TO = "Toaleta"
CO = "Korytarz"
BE = "Sypialnia"
R2 = "Mały pokój"

ROOM_CHOICES = (
    (LI, "Pokój dzienny"),
    (BA, "Łazienka"),
    (TO, "Toaleta"),
    (CO, "Korytarz"),
    (BE, "Sypialnia"),
    (R2, "Mały pokój")
)


class Table(models.Model):
    cost_date = models.DateField("cost_date")
    desc = models.CharField(max_length=256)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    room = models.CharField(max_length=32, choices=ROOM_CHOICES, default="Pokój dzienny")

    def __str__(self):
        return f"{self.desc}"

