from django.core.management import BaseCommand

from django_ai_agent.services import ToolService


class Command(BaseCommand):

    def handle(self, *args, **options):
        synced, inactive = ToolService.sync()

        self.stdout.write(self.style.SUCCESS(f'Successfully synced {synced} tools.'))
        self.stdout.write(self.style.SUCCESS(f'Successfully deactivated {inactive} tools.'))
