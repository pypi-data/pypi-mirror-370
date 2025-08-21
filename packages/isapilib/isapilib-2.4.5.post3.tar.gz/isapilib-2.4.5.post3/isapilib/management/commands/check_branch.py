from django.core.management import BaseCommand
from django.db import connections

from isapilib.api.models import SepaBranch
from isapilib.external.connection import create_conn


class Command(BaseCommand):
    help = 'Check connection to external database'

    def add_arguments(self, parser):
        parser.add_argument(
            "branch",
            nargs="?",
            help="id branch",
        )

    def handle(self, *args, **options):
        branch = SepaBranch.objects.filter(id=options["branch"]).first()

        if branch:
            db_name = f'external-{branch.id}'
            connections.databases[db_name] = create_conn(branch)

            try:
                connection = connections[db_name]
                cursor = connection.cursor()
                cursor.execute('SELECT 1')
                self.stdout.write(self.style.SUCCESS(f'Connection to database {db_name} was successful.'))
            except Exception as e:
                self.stdout.write(self.style.SUCCESS(f'Failed to connect to database {db_name}: {e}'))
        else:
            self.stdout.write(self.style.SUCCESS(f"Branch doesn't exist."))
