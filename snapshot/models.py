from django.db import models


class BaseModel(models.Model):
    created_date = models.DateTimeField(auto_now_add=True)
    modified_date = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Car(BaseModel):
    first_name = models.CharField(max_length=200)
    last_name = models.CharField(max_length=200)
    car = models.TextField()
    license_plate = models.CharField(max_length=200, unique=True)
    phone = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return '{name} {last_name} - {plate} - {phone} - {car}'.format(
            name=self.first_name,
            last_name=self.last_name,
            plate=self.license_plate,
            phone=self.phone,
            car=self.car,
        )
