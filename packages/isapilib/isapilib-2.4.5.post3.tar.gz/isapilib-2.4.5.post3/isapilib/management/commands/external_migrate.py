from django.core.management.base import CommandError
from django.core.management.commands.migrate import Command as MigrateCommand
from django.db import connections

from isapilib.api.models import SepaBranch
from isapilib.external.connection import create_conn


class Command(MigrateCommand):
    help = 'Migrate from external database'
    exclude_apps = ['admin', 'auth', 'contenttypes', 'oauth2_provider', 'sessions']

    def add_arguments(self, parser):
        parser.add_argument(
            "branch",
            nargs="?",
            help="id branch",
        )
        super().add_arguments(parser)

    def handle(self, *args, **options):
        branch = SepaBranch.objects.get(id=options["branch"])
        connections.databases['external'] = create_conn(branch)
        options['database'] = 'external'

        if not options['app_label']:
            raise CommandError('you must specified app_name')
        elif options['app_label'] in self.exclude_apps:
            raise CommandError(f'You can´t migrate {options["app_label"]} app')

        db_host = connections[options['database']].settings_dict['HOST']
        db_name = connections[options['database']].settings_dict['NAME']
        self.stdout.write(self.style.SUCCESS(f'Running migrations on {db_host} {db_name}:'))
        super().handle(*args, **options)
