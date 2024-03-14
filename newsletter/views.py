from django.urls import reverse
from django.template.loader import get_template
from django.core.mail import EmailMessage
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Subscriber

def subscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subscriber, created = Subscriber.objects.get_or_create(email=email)
        
        if created or not subscriber.verified:
            # Send verification email for new subscription or unverified subscription
            send_verification_email(request, subscriber)
            messages.success(request, 'A verification email has been sent. Please verify your email address.')
        else:
            messages.info(request, 'You are already subscribed.')
        
        return redirect('subscribe')
    
    return render(request, 'newsletter/subscribe.html')

def unsubscribe(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        subscriber = Subscriber.objects.filter(email=email).first()
        
        if subscriber:
            if subscriber.verified:
                # Send unsubscribe verification email for verified subscribers
                send_unsubscribe_verification_email(request, subscriber)
                messages.success(request, 'A verification email has been sent for unsubscribing. Please verify to unsubscribe.')
            else:
                messages.info(request, 'You are not subscribed.')
        else:
            messages.info(request, 'No subscription found with this email address.')
        
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

def send_unsubscribe_verification_email(request, subscriber):
    subject = 'Unsubscribe confirmation'
    unsubscribe_link = request.build_absolute_uri(reverse('verify_unsubscribe', args=[subscriber.verification_token]))
    template = get_template('newsletter/confirmation_emails/unsubscribe_confirmation_email_body.txt')
    context = {'subscriber': subscriber, 'unsubscribe_link': unsubscribe_link}
    message = template.render(context)
    email = EmailMessage(subject, message, to=[subscriber.email])
    email.send()

def verify_email(request, verification_token):
    subscriber = get_object_or_404(Subscriber, verification_token=verification_token)
    subscriber.verified = True
    subscriber.save()
    
    messages.success(request, 'Your email address has been verified. You will now receive our newsletters.')
    
    return redirect('subscribe')

def verify_unsubscribe(request, verification_token):
    subscriber = get_object_or_404(Subscriber, verification_token=verification_token)
    # When subscribed user verify to unsubscribe, subscriber is removed
    subscriber.delete()
    messages.success(request, 'You have been unsubscribed successfully.')
    return redirect('subscribe')