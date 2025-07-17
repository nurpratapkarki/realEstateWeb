from django.core.management.base import BaseCommand
from app.models import Organization


class Command(BaseCommand):
    help = 'Create or update sample organization data'

    def handle(self, *args, **options):
        # Get or create the organization
        org, created = Organization.objects.get_or_create(
            id=1,
            defaults={
                'name': 'Premier Properties',
                'description': 'Premier Properties is a leading real estate company specializing in luxury properties, investment consulting, and comprehensive property management services. With over 15 years of experience in the market, we help clients find their dream homes and make smart investment decisions.',
                'phone': '+1 (555) 123-4567',
                'email': 'info@premierproperties.com',
                'address': '123 Luxury Avenue, Beverly Hills, CA 90210',
                'whatsapp': '+1 (555) 123-4567',
                'facebook': 'https://facebook.com/premierproperties',
                'instagram': 'https://instagram.com/premierproperties',
                'linkedin': 'https://linkedin.com/company/premierproperties',
                'twitter': 'https://twitter.com/premierprops'
            }
        )
        
        if not created:
            # Update existing organization with better data
            org.name = 'Premier Properties'
            org.description = 'Premier Properties is a leading real estate company specializing in luxury properties, investment consulting, and comprehensive property management services. With over 15 years of experience in the market, we help clients find their dream homes and make smart investment decisions.'
            org.phone = '+1 (555) 123-4567'
            org.email = 'info@premierproperties.com'
            org.address = '123 Luxury Avenue, Beverly Hills, CA 90210'
            org.whatsapp = '+1 (555) 123-4567'
            org.facebook = 'https://facebook.com/premierproperties'
            org.instagram = 'https://instagram.com/premierproperties'
            org.linkedin = 'https://linkedin.com/company/premierproperties'
            org.twitter = 'https://twitter.com/premierprops'
            org.save()
            
            self.stdout.write(
                self.style.SUCCESS(f'Updated organization: {org.name}')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Created organization: {org.name}')
            )
        
        self.stdout.write(
            self.style.SUCCESS('Organization data is ready for SEO meta tags!')
        )
        self.stdout.write(
            self.style.WARNING('Note: You can upload a logo through the admin dashboard at /admin-dashboard')
        )
