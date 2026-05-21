import datetime
from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from core.models import User
from news.models import News_article

class Command(BaseCommand):
    help = 'Sends a morning newsletter with the latest article to all users'

    def handle(self, *args, **kwargs):
        # 1. Fetch the latest approved article
        latest_article = News_article.objects.filter(status='approved').order_by('-created_at').first()
        
        if not latest_article:
            self.stdout.write(self.style.WARNING("No approved articles found to send."))
            return

        # 2. Prepare the email content
        subject = f"Morning Digest: {latest_article.title}"
        
        # Build a simple HTML/Text body
        # In a real app, you'd use a template
        article_url = f"{settings.SITE_URL}/article/{latest_article.slug}/" if hasattr(settings, 'SITE_URL') else f"Check it out on CIVIX!"
        
        body = f"""
Hello Reader,

Here is your morning update from CIVIX:

{latest_article.title}
------------------
{latest_article.excerpt or latest_article.content[:200] + '...'}

Read the full story here: {article_url}

Best regards,
The CIVIX Team
        """

        # 3. Fetch all active users
        users = User.objects.filter(is_active=True)
        recipient_list = [user.email for user in users]

        if not recipient_list:
            self.stdout.write(self.style.WARNING("No active users found."))
            return

        self.stdout.write(self.style.SUCCESS(f"Sending newsletter to {len(recipient_list)} users..."))

        # 4. Send emails in batches to avoid server limits
        try:
            send_mail(
                subject=subject,
                message=body,
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=recipient_list,
                fail_silently=False,
            )
            self.stdout.write(self.style.SUCCESS("Newsletter sent successfully!"))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to send newsletter: {e}"))
