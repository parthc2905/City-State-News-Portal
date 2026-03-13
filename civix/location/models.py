from django.db import models

# Create your models here.
class State(models.Model):
    state_name = models.CharField(max_length=100, null=False, unique=True)
    REGION_TYPES = [
        ("state", "State"),
        ("ut", "Union Territory"),
    ]
    region_type = models.CharField(
        max_length=10,
        choices=REGION_TYPES,
        default="state"
    )
    class Meta:
        db_table = "state"

    def __str__(self):
        return self.state_name
    
class City(models.Model):
    city_name = models.CharField(max_length=100, null=False)
    state_id = models.ForeignKey(State, on_delete=models.CASCADE)

    class Meta:
        db_table = "city"

    def __str__(self):
        return self.city_name