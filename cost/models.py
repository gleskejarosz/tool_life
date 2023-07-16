from django.db import models


LI = "Salon"
KU = "Kuchnia"
BA = "Łazienka"
TO = "WC"
CO = "Korytarz"
BE = "Sypialnia"
R2 = "Mały pokój"
TR = "Transport"
OT = "Rożne"

ROOM_CHOICES = (
    (LI, "Salon"),
    (KU, "Kuchnia"),
    (BA, "Łazienka"),
    (TO, "WC"),
    (CO, "Korytarz"),
    (BE, "Sypialnia"),
    (R2, "Mały pokój"),
    (TR, "Transport"),
    (OT, "Rożne"),
)


class Table(models.Model):
    cost_date = models.DateField("cost_date")
    desc = models.CharField(max_length=256)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cat = models.CharField(max_length=32, choices=ROOM_CHOICES, default="Salon")

    def __str__(self):
        return f"{self.desc}"

    class Meta:
        verbose_name = "Cost"


class Contents(models.Model):
    num = models.IntegerField()
    desc = models.CharField(max_length=256)
    weight = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.desc}"

    class Meta:
        verbose_name = "Content"

