import uuid
from django.db import models

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.email