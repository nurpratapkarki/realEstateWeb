from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from app.models import CustomerMessage, CustomerDocument, Agent, Property
from django.core.files.base import ContentFile
import io

User = get_user_model()


class Command(BaseCommand):
    help = 'Create sample customer messages and documents for testing'

    def handle(self, *args, **options):
        # Get or create a customer user
        customer, created = User.objects.get_or_create(
            username='testcustomer',
            defaults={
                'email': 'customer@test.com',
                'first_name': 'Test',
                'last_name': 'Customer',
                'role': 'customer'
            }
        )
        
        if created:
            customer.set_password('testpass123')
            customer.save()
            self.stdout.write(f'Created customer user: {customer.username}')
        else:
            self.stdout.write(f'Using existing customer user: {customer.username}')

        # Get an agent (create one if none exists)
        agent = Agent.objects.first()
        if not agent:
            agent = Agent.objects.create(
                first_name='Sarah',
                last_name='Johnson',
                email='sarah@realestate.com',
                phone='+1234567890',
                title='Senior Real Estate Agent',
                bio='Experienced agent specializing in luxury properties.',
                experience_years=5,
                license_number='RE123456'
            )
            self.stdout.write(f'Created agent: {agent.full_name}')

        # Get a property (create one if none exists)
        property_obj = Property.objects.first()
        if not property_obj:
            from app.models import PropertyType
            property_type, _ = PropertyType.objects.get_or_create(
                name='Apartment',
                defaults={'description': 'Modern apartments'}
            )
            property_obj = Property.objects.create(
                title='Luxury Downtown Apartment',
                description='Beautiful 2-bedroom apartment in the heart of downtown.',
                property_type=property_type,
                price=750000,
                bedrooms=2,
                bathrooms=2,
                area=1200,
                location='Downtown',
                address='123 Main Street, Downtown'
            )
            self.stdout.write(f'Created property: {property_obj.title}')

        # Create sample messages
        messages_data = [
            {
                'subject': 'Property Viewing Request',
                'message': "Hi! I'm very interested in the luxury apartment listing. Could we arrange a viewing this weekend?",
                'is_from_customer': True,
            },
            {
                'subject': 'Re: Property Viewing Request',
                'message': "Hi! I'd love to schedule a viewing for the downtown apartment. Are you available this Saturday afternoon around 2 PM?",
                'is_from_customer': False,
            },
            {
                'subject': 'Financing Options',
                'message': "Could you provide more information about financing options for this property?",
                'is_from_customer': True,
            },
            {
                'subject': 'Re: Financing Options',
                'message': "I've attached a financing guide with various options. We can also connect you with our preferred lenders.",
                'is_from_customer': False,
            }
        ]

        created_messages = 0
        for msg_data in messages_data:
            message, created = CustomerMessage.objects.get_or_create(
                customer=customer,
                agent=agent,
                property=property_obj,
                subject=msg_data['subject'],
                defaults={
                    'message': msg_data['message'],
                    'is_from_customer': msg_data['is_from_customer']
                }
            )
            if created:
                created_messages += 1

        self.stdout.write(f'Created {created_messages} new messages')

        # Create sample documents
        documents_data = [
            {
                'title': 'Property Brochure - Luxury Downtown Apartment',
                'description': 'Detailed brochure with photos and specifications',
                'document_type': 'brochure',
            },
            {
                'title': 'Financing Options Guide',
                'description': 'Complete guide to available financing options',
                'document_type': 'guide',
            },
            {
                'title': 'Neighborhood Report',
                'description': 'Comprehensive report about the downtown area',
                'document_type': 'report',
            }
        ]

        created_documents = 0
        for doc_data in documents_data:
            # Create a simple text file content
            file_content = f"Sample document: {doc_data['title']}\n\n{doc_data['description']}\n\nThis is a sample document for testing purposes."
            
            document, created = CustomerDocument.objects.get_or_create(
                customer=customer,
                property=property_obj,
                title=doc_data['title'],
                defaults={
                    'description': doc_data['description'],
                    'document_type': doc_data['document_type'],
                    'file': ContentFile(file_content.encode(), name=f"{doc_data['title'].lower().replace(' ', '_')}.txt")
                }
            )
            if created:
                created_documents += 1

        self.stdout.write(f'Created {created_documents} new documents')
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Sample data creation complete!\n'
                f'Customer: {customer.username} (password: testpass123)\n'
                f'Messages: {CustomerMessage.objects.filter(customer=customer).count()}\n'
                f'Documents: {CustomerDocument.objects.filter(customer=customer).count()}'
            )
        )
