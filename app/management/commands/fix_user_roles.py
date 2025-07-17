from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()


class Command(BaseCommand):
    help = 'Fix user roles for existing staff/superuser accounts'

    def handle(self, *args, **options):
        # Find users who are staff/superuser but have role='customer'
        staff_users_with_wrong_role = User.objects.filter(
            is_staff=True,
            role='customer'
        )
        
        superusers_with_wrong_role = User.objects.filter(
            is_superuser=True,
            role='customer'
        )
        
        # Combine and get unique users
        users_to_fix = (staff_users_with_wrong_role | superusers_with_wrong_role).distinct()
        
        if not users_to_fix.exists():
            self.stdout.write(
                self.style.SUCCESS('No users found with incorrect roles.')
            )
            return
        
        self.stdout.write(
            f'Found {users_to_fix.count()} users with incorrect roles:'
        )
        
        for user in users_to_fix:
            self.stdout.write(
                f'  - {user.username} (is_staff: {user.is_staff}, is_superuser: {user.is_superuser}, current role: {user.role})'
            )
        
        # Ask for confirmation
        confirm = input('\nDo you want to fix these users? (y/N): ')
        if confirm.lower() != 'y':
            self.stdout.write('Operation cancelled.')
            return
        
        # Fix the roles
        updated_count = 0
        for user in users_to_fix:
            old_role = user.role
            user.role = 'admin'
            user.save()
            updated_count += 1
            self.stdout.write(
                f'Updated {user.username}: {old_role} -> admin'
            )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} users.')
        )
