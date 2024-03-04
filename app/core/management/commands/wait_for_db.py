"""
Django command to wait for the Database to be available.
"""
import time

from django.core.management.base import BaseCommand
from django.db.utils import OperationalError

from psycopg2 import OperationalError as Psycopg2Error


class Command(BaseCommand):
    """Django command to wait for Database"""
    def handle(self, *args, **options):
        """Entry-point for command"""
        self.stdout.write('Waiting for Database...')
        db_up = False
        while db_up is False:
            try:
                self.check(databases=['default'])
                db_up = True
            except (OperationalError, Psycopg2Error):
                self.stdout.write(
                    self.style.NOTICE(
                        'Database not Available, waiting for a second...'
                    )
                )
                time.sleep(1)
        self.stdout.write(self.style.SUCCESS('Database Available!'))
