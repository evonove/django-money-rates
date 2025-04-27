from django.core.management.base import BaseCommand, CommandError

from ...settings import money_rates_settings, import_from_string


class Command(BaseCommand):
    help = 'Update rates for configured source'

    def add_arguments(self, parser):
        parser.add_argument('backend_path', nargs='?')

    def handle(self, *args, **options):
        if 'backend_path' in options and options['backend_path']:
            try:
                backend_class = import_from_string(options['backend_path'], "")
            except ImportError:
                raise CommandError("Cannot find custom backend {}. Is it correct".format(options['backend_path']))
        else:
            backend_class = money_rates_settings.DEFAULT_BACKEND

        try:
            backend = backend_class()
            backend.update_rates()
        except Exception as e:
            raise CommandError(f"Error during rate update: {e}")

        self.stdout.write(f'Successfully updated rates for "{backend_class}"')
