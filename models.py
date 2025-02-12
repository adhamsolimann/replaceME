from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import DecimalRangeField
from django.db.models import constraints
from django.db.models.deletion import CASCADE
from django.db.models.query_utils import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
import logging
from psycopg2.extras import NumericRange
from django.contrib.postgres.serializers import RangeSerializer
from django.db.migrations.writer import MigrationWriter

MigrationWriter.register_serializer(NumericRange, RangeSerializer)

# make User field email unique and required
User._meta.get_field('email')._unique = True
User._meta.get_field('email').blank = False
User._meta.get_field('email').null = False

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=CASCADE)
    unternehmen = models.CharField(max_length=50, default= '')
    address = models.CharField(max_length=50, default='')
    city = models.CharField(max_length=50, default='')
    postalCode = models.CharField(max_length= 10, default='')

    # create Customer Object when User is created
    @receiver(post_save, sender=User)
    def create_customer_profile(sender, instance, created, **kwargs):
        if created:
            Customer.objects.create(user=instance)

    # Update Customer when User is changed
    @receiver(post_save, sender=User)
    def save_customer_profile(sender, instance, **kwargs):
        instance.customer.save()

    def __str__(self):
        return f"{self.user.username}"

class Material(models.Model):
# Model representing an material
    HOLZ = 'Holz'
    POLYMER = 'Polymer'
    LEICHTMETALL = 'Leichtmetall'
    SCHWERMETALL = 'Schwermetall'
    STAHL = 'Stahl'
    VERBUNDWERKSTOFF = 'Verbundwerkstoff'
    GLAS = 'Glas'


    MATERIALCLASS = [
        (HOLZ,'Holz'),
        (POLYMER, 'Polymer'),
        (LEICHTMETALL, 'Leichtmetall'),
        (SCHWERMETALL, 'Schwermetall'),
        (STAHL, 'Stahl'),
        (VERBUNDWERKSTOFF, 'Verbundwerkstoff'),
        (GLAS, 'Glas')
    ]
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    material_class = models.CharField(max_length=200, choices=MATERIALCLASS, default=HOLZ)
    heat_conductivity = models.FloatField(null=True, blank=True)
    tensile_strength = models.FloatField(null=True, blank=True)
    hardness = models.FloatField(null=True, blank=True)
    heat_capacity = models.FloatField(null=True, blank=True)
    electric_conductivity = models.FloatField(null=True, blank=True)
    magnetism = models.BooleanField()
    density = models.FloatField(null=True, blank=True)
    water_cunsumption = models.FloatField(null=True, blank=True)
    co2 = models.FloatField(null=True, blank=True)
    price = models.FloatField(null=True, blank=True, verbose_name='Preis in € pro kg')

    def __str__(self):
        return f"{self.name}"


    def calculate_sustainability(self):
        sustainability_index = (self.co2 + self.water_cunsumption)/2
        return sustainability_index

class Usecase(models.Model):
# Model representing an usecase
    name = models.CharField(max_length=200)
    description = models.CharField(max_length=200)
    heat_conductivity = DecimalRangeField(null=True, blank=True, default=NumericRange(0,None))
    tensile_strength = DecimalRangeField(null=True,blank=True,default=NumericRange(0,None))
    hardness = DecimalRangeField(null=True,blank=True,default=NumericRange(0,None))
    heat_capacity = DecimalRangeField(null=True,blank=True,default=NumericRange(0,None))
    electric_conductivity = DecimalRangeField(null=True,blank=True,default=NumericRange(0,None))
    magnetism = models.BooleanField()
    density = DecimalRangeField(null=True,blank=True,default=NumericRange(0,None))

    

    def __str__(self):
        return f"{self.name}"

class Item(models.Model):
    # Model representing a specific product
    height = models.FloatField()
    width = models.FloatField()
    depth = models.FloatField()
    description = models.CharField(max_length=200)
    inStock = models.PositiveIntegerField()
    material = models.ForeignKey(Material, on_delete=models.CASCADE)

    def __str__(self):
        return f"Produkt {self.id}"

    def get_price(self):
            volume = self.height * self.width * self.depth
            material_density = self.material.density
            material_price = self.material.price
            weight = volume * material_density
            item_price = round(((weight/1000) * material_price * self.inStock), 2)    
            return item_price

class Order(models.Model):
 # Model representing an order
    AUFGEGEBEN = "Aufgegeben"
    IN_BEARBEITUNG = "In Bearbeitung"
    ABGESCHLOSSEN = "Abgeschlossen"
    STATUS_CHOICES = [
    (AUFGEGEBEN, 'Aufgegeben'),
    (IN_BEARBEITUNG, 'In Bearbeitung'),
    (ABGESCHLOSSEN, 'Abgeschlossen'),
    ]
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    status = models.CharField(max_length=50,choices=STATUS_CHOICES,default="Aufgegeben")
    comments = models.CharField(max_length=200, blank=True)
    total_price = models.DecimalField(null=True, max_digits=19, decimal_places=2)

    def __str__(self):
        return f" Bestellnummer {self.id}"

class OrderDetail(models.Model):
    # Model representing an orderdetail --> on item from an order
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    item = models.ForeignKey(Item, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.DecimalField(null=True, max_digits=19, decimal_places=2)

    def __str__(self):
        return f"{self.id}"

class ContactMessage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    Email = models.EmailField(max_length=50, default='')
    Titel = models.CharField(max_length=50, default='')
    Beschreibung = models.TextField(max_length=500, default='')

    @receiver(post_save, sender=User)
    def create_message(sender, instance, created, **kwargs):
        if created:
           ContactMessage.objects.create(user=instance, Email=instance.email, Titel="Neue Registrierung")

    

    def __str__(self):
        return f"{self.Beschreibung}"
