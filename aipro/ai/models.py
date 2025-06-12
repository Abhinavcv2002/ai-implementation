from django.db import models
from django.contrib.auth.models import User
from .constants import PaymentStatus
from django.db.models.fields import CharField
from django.utils.translation import gettext_lazy as _


# Create your models here.

class category(models.Model):
    name = models.CharField(max_length=250)
    
    def __str__(self):
        return str(self.name)  # ✅ This returns a string

class Gender(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return str(self.name)  # ✅ This returns a string

class Material(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return str(self.name)  # ✅ This returns a string

class FrameType(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return str(self.name)  # ✅ This returns a string

    
class FrameShape(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return str(self.name)  # ✅ This returns a string

    
class FrameStyle(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return str(self.name)  # ✅ This returns a string

    
class Product(models.Model):
    name= models.CharField(max_length=250)
    price= models.FloatField()
    color= models.CharField(max_length=250)
    image= models.ImageField(upload_to='product/')
    image1 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    image2 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    image3 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    image4 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    image5 = models.ImageField(upload_to='path/to/upload/', null=True, blank=True)
    description= models.TextField()
    categorys= models.ForeignKey(category, on_delete=models.CASCADE,null=True)
    gender= models.ForeignKey(Gender, on_delete=models.CASCADE,null=True)
    material= models.ForeignKey(Material, on_delete=models.CASCADE,null=True)
    frameType= models.ForeignKey(FrameType, on_delete=models.CASCADE,null=True)
    frameShape= models.ForeignKey(FrameShape, on_delete=models.CASCADE,null=True)
    frameStyle= models.ForeignKey(FrameStyle, on_delete=models.CASCADE,null=True)
    rating=models.FloatField(default=0)
    vector_data=models.TextField(null=True)

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product= models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity= models.IntegerField()
    totalprice= models.FloatField()

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=225)
    address=models.TextField()
    city=models.CharField(max_length=225)
    state=models.CharField(max_length=225)
    pincode=models.CharField(max_length=225)
    phone=models.CharField(max_length=12)

class users(models.Model):
    name=models.ForeignKey(User,on_delete=models.CASCADE)
    vector_data=models.TextField(null=True)
    def __str__(self):
        return self.name.username
class SearchHistory(models.Model):
    query = models.CharField(max_length=255)
    user = models.ForeignKey(users, on_delete=models.CASCADE)

class ViewHistory(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(users,on_delete=models.CASCADE) 

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    
    amount = models.FloatField(_("Amount"), null=False, blank=False)
    status = CharField(
        _("Payment Status"),
        default=PaymentStatus.PENDING,
        max_length=254,
        blank=False,
        null=False,
    )
    provider_order_id = models.CharField(_("Order ID"), max_length=40,null=True)
    payment_id = models.CharField(_("Payment ID"), max_length=36,null=True)
    signature_id = models.CharField(_("Signature ID"), max_length=128,null=True)

    def __str__(self):
        return f"{self.user.username} - {self.product.title} ({self.quantity})"

class reviews(models.Model):
    rating=models.IntegerField()
    description=models.TextField()
    uname=models.ForeignKey(users,on_delete=models.CASCADE)
    pname = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='product_reviews')