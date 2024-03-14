from django.urls import reverse
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect
from django.contrib import messages
from django.shortcuts import get_object_or_404
from .models import Subscriber

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subscriber, created = Subscriber.objects.get_or_create(email=email)
        if not subscriber.verified:
            # Send verification email
            send_verification_email(request, subscriber)
            messages.success(request, 'A verification email has been sent. Please verify your email address.')
        else:
            messages.info(request, 'You are already subscribed.')
        return redirect('subscribe')
    return render(request, 'newsletter/subscribe.html')

def send_verification_email(request, subscriber):
    subject = 'Verify your email address'
    verification_link = request.build_absolute_uri(reverse('verify_email', args=[subscriber.verification_token]))
    template = get_template('newsletter/confirmation_emails/confirmation_email_body.txt')
    context = {'subscriber': subscriber, 'verification_link': verification_link}
    message = template.render(context)
    email = EmailMessage(subject, message, to=[subscriber.email])
    email.send()

def verify_email(request, verification_token):
    subscriber = get_object_or_404(Subscriber, verification_token=verification_token)
    subscriber.verified = True
    subscriber.save()
    messages.success(request, 'Your email address has been verified. You will now receive our newsletters.')
    return redirect('subscribe')