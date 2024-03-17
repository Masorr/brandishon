import uuid
from django.db import models


class Subscriber(models.Model):
    '''
    Stores subscriber to the newsletter

    verification_token (universally unique identifier) (UUID) is used for email
    verification.
    
    It is automatically generated using uuid.uuid4 and is tied to
    the subscriber's verification when it is first stored.
    '''
    email = models.EmailField(unique=True)
    verified = models.BooleanField(default=False)
    verification_token = models.UUIDField(default=uuid.uuid4, editable=False)

    def __str__(self):
        return self.email
