from __future__ import unicode_literals

from django.core.management.base import BaseCommand, CommandError

from ...settings import money_rates_settings, import_from_string


class Command(BaseCommand):
    args = '<backend_path>'
    help = 'Update rates for configured source'

    def handle(self, *args, **options):
        if args:
            try:
                backend_class = import_from_string(args[0], "")
            except ImportError:
                raise CommandError("Cannot find custom backend %s. Is it correct" % args[0])
        else:
            backend_class = money_rates_settings.DEFAULT_BACKEND

        try:
            backend = backend_class()
            backend.update_rates()
        except Exception as e:
            raise CommandError("Error during rate update: %s" % e)

        self.stdout.write('Successfully updated rates for "%s"' % backend_class)
