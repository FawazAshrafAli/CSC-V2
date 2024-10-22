from django.db import models
import uuid

class State(models.Model):
    state = models.CharField(max_length=150)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.state


class District(models.Model):
    district = models.CharField(max_length=150)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.district


class Block(models.Model):
    block = models.CharField(max_length=150)
    district = models.CharField(max_length=150)
    state = models.ForeignKey(State, on_delete=models.CASCADE)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.block
    

class Service(models.Model):
    csc_id = models.CharField(max_length=50)
    service = models.CharField(max_length=150)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.service

def generate_csc_id():
    uuid_str = str(uuid.uuid4().int)
    return uuid_str[:12]


class CommonServiceCenter(models.Model):
    csc_id = models.CharField(max_length=50, primary_key=True, default=generate_csc_id)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)
    alternative_number = models.CharField(max_length=15)
    email = models.EmailField(max_length=254)
    service = models.ManyToManyField(Service)
    state = models.ForeignKey(State, on_delete=models.CASCADE)
    district = models.ForeignKey(District, on_delete=models.CASCADE)
    block = models.ForeignKey(Block, on_delete=models.CASCADE)
    address = models.TextField(null=True, blank=True)

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


    def __str__(self):
        return self.name