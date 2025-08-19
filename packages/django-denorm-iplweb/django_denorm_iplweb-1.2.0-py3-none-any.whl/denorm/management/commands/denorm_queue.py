import logging
import select
import sys

import psycopg2.extensions
from django.core.management.base import BaseCommand
from django.db import connection

from denorm.db import const
from denorm.tasks import flush_single

logger = logging.getLogger(__name__)


class Command(BaseCommand):

    help = "Runs a process that checks for dirty fields and updates them in regular intervals."

    def add_arguments(self, parser):
        parser.add_argument(
            "--run-once",
            action="store_true",
            help="Used for testing. Causes event loop to run once. ",
        )

    def handle(self, run_once=False, **options):
        ran_once = False

        crs = (
            connection.cursor()
        )  # get the cursor and establish the connection.connection
        pg_con = connection.connection
        pg_con.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        crs.execute(f"LISTEN {const.DENORM_QUEUE_NAME}")

        logger.info("Starting, running initial flush...")

        logger.info(
            f"waiting for notifications on channel '{const.DENORM_QUEUE_NAME}'..."
        )
        while True:
            if ran_once and run_once:
                break
            ran_once = True

            try:
                if select.select([pg_con], [], [], None) == ([], [], []):
                    logger.warning("timeout")
                else:
                    pg_con.poll()

                    try:
                        res = pg_con.notifies.pop()
                    except IndexError:
                        continue

                    if res.payload is None:
                        raise ValueError("Payload is None")

                    try:
                        pk = int(res.payload)
                    except (TypeError, ValueError):
                        raise ValueError("Unable to convert payload to int")

                    # Payload is the ID in the django_denorm table of the newly created dirty instance,
                    # one needs just to call the task of rebuilding it somewhere to a woker's queue:

                    flush_single.delay(pk)

            except KeyboardInterrupt:
                sys.exit()
