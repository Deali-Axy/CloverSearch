from django.core.management.base import BaseCommand, CommandError
from ... import index_builder
from ... import config
import time


class Command(BaseCommand):
    help = '{}: create Model index config files'.format(config.MODULE_NAME)

    def handle(self, *args, **options):
        try:
            start_time = time.time()
            index_builder.create_model_config()
            end_time = time.time()
            took_time = end_time - start_time
        except Exception as e:
            raise CommandError(e)
        else:
            self.stdout.write(self.style.SUCCESS('Create model index config finished. Took {} seconds'.format(took_time)))
