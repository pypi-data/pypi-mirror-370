"""
Makes ``consume_events`` management command available.
"""
import json
import logging

from django.core.management.base import BaseCommand

from openedx_events.event_bus import make_single_consumer
from openedx_events.tooling import load_all_signals

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Management command for consumer workers in the event bus.
    """

    help = """
    Consume messages from a topic and emit their data with the correct signal.

    Example::

        python manage.py consume_events -t user-login -g user-activity-service

        # send extra args, for example pass check_backlog flag to redis consumer
        python manage.py cms consume_events -t user-login -g user-activity-service  --extra '{"check_backlog": true}'

        # send extra args, for example replay events from specific redis msg id.
        python manage.py cms consume_events -t user-login -g user-activity-service \
            --extra '{"last_read_msg_id": "1679676448892-0"}'
    """

    def add_arguments(self, parser):
        """
        Add arguments for parsing topic, group, and extra args.
        """
        parser.add_argument(
            '-t', '--topic',
            nargs=1,
            required=True,
            help='Topic to consume (without environment prefix)'
        )
        parser.add_argument(
            '-g', '--group_id',
            nargs=1,
            required=True,
            help='Consumer group id'
        )
        parser.add_argument(
            '--extra',
            nargs='?',
            type=str,
            required=False,
            help='JSON object to pass additional arguments to the consumer.'
        )

    def handle(self, *args, **options):
        """
        Create consumer based on django settings and consume events.
        """
        try:
            # load additional arguments specific for the underlying implementation of event_bus.
            extra = json.loads(options.get('extra') or '{}')
            load_all_signals()
            event_consumer = make_single_consumer(
                topic=options['topic'][0],
                group_id=options['group_id'][0],
                **extra,
            )
            event_consumer.consume_indefinitely()
        except Exception:  # pylint: disable=broad-except
            logger.exception("Error consuming events")
