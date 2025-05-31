from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from ojt_tracker.models import OJTRequest, Student, UserRole

class Command(BaseCommand):
    help = 'Test OJT request approval functionality'

    def handle(self, *args, **options):
        self.stdout.write('Testing OJT Request Approval Functionality...')
        
        # Find a pending OJT request
        pending_request = OJTRequest.objects.filter(status='pending').first()
        
        if not pending_request:
            self.stdout.write(self.style.WARNING('No pending OJT requests found.'))
            return
        
        # Find an admin user
        admin_user = User.objects.filter(role__role='admin').first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('No admin user found.'))
            return
        
        self.stdout.write(f'Found pending request: {pending_request}')
        self.stdout.write(f'Admin user: {admin_user.get_full_name()}')
        
        # Test approval
        try:
            result = pending_request.approve(admin_user, "Test approval via management command")
            if result:
                self.stdout.write(self.style.SUCCESS(f'Successfully approved request {pending_request.id}'))
                
                # Verify the status changed
                pending_request.refresh_from_db()
                self.stdout.write(f'New status: {pending_request.status}')
                self.stdout.write(f'Reviewed by: {pending_request.reviewed_by}')
                self.stdout.write(f'Admin response: {pending_request.admin_response}')
            else:
                self.stdout.write(self.style.ERROR('Failed to approve request'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error during approval: {str(e)}')) 