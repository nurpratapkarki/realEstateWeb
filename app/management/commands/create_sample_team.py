from django.core.management.base import BaseCommand
from app.models import Team


class Command(BaseCommand):
    help = 'Create sample team members'

    def handle(self, *args, **options):
        # Clear existing team members
        Team.objects.all().delete()
        
        team_members = [
            {
                'name': 'Sarah Johnson',
                'position': 'CEO & Founder',
                'bio': 'With over 15 years of experience in real estate, Sarah founded Premier Properties with a vision to revolutionize the property market. She leads our team with passion and expertise.',
                'email': 'sarah.johnson@premierproperties.com',
                'phone': '+1 (555) 123-4567',
                'linkedin': 'https://linkedin.com/in/sarahjohnson',
                'order': 1,
                'is_active': True
            },
            {
                'name': 'Michael Rodriguez',
                'position': 'Head of Sales',
                'bio': 'Michael brings 12 years of sales excellence to our team. His dedication to client satisfaction and market knowledge makes him an invaluable asset.',
                'email': 'michael.rodriguez@premierproperties.com',
                'phone': '+1 (555) 234-5678',
                'linkedin': 'https://linkedin.com/in/michaelrodriguez',
                'order': 2,
                'is_active': True
            },
            {
                'name': 'Emily Chen',
                'position': 'Marketing Director',
                'bio': 'Emily leads our marketing initiatives with creativity and strategic thinking. Her innovative campaigns have helped establish our brand in the market.',
                'email': 'emily.chen@premierproperties.com',
                'phone': '+1 (555) 345-6789',
                'linkedin': 'https://linkedin.com/in/emilychen',
                'twitter': 'https://twitter.com/emilychen',
                'order': 3,
                'is_active': True
            },
            {
                'name': 'David Thompson',
                'position': 'Operations Manager',
                'bio': 'David ensures smooth operations across all our departments. His attention to detail and organizational skills keep our company running efficiently.',
                'email': 'david.thompson@premierproperties.com',
                'phone': '+1 (555) 456-7890',
                'linkedin': 'https://linkedin.com/in/davidthompson',
                'order': 4,
                'is_active': True
            },
            {
                'name': 'Lisa Park',
                'position': 'Customer Relations Manager',
                'bio': 'Lisa is dedicated to ensuring exceptional customer experiences. Her friendly approach and problem-solving skills make her a favorite among clients.',
                'email': 'lisa.park@premierproperties.com',
                'phone': '+1 (555) 567-8901',
                'linkedin': 'https://linkedin.com/in/lisapark',
                'order': 5,
                'is_active': True
            },
            {
                'name': 'James Wilson',
                'position': 'Technology Lead',
                'bio': 'James drives our digital transformation initiatives. His expertise in PropTech solutions helps us stay ahead in the competitive real estate market.',
                'email': 'james.wilson@premierproperties.com',
                'phone': '+1 (555) 678-9012',
                'linkedin': 'https://linkedin.com/in/jameswilson',
                'twitter': 'https://twitter.com/jameswilson',
                'order': 6,
                'is_active': True
            }
        ]
        
        for member_data in team_members:
            team_member = Team.objects.create(**member_data)
            self.stdout.write(
                self.style.SUCCESS(f'Created team member: {team_member.name} - {team_member.position}')
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {len(team_members)} team members')
        )
