"""
Test for producer configuration.
"""
from unittest.mock import Mock, patch

import ddt
import pytest
from django.apps import apps
from django.test import TestCase, override_settings

from openedx_events.content_authoring.data import XBlockData
from openedx_events.content_authoring.signals import XBLOCK_DELETED, XBLOCK_PUBLISHED
from openedx_events.exceptions import ProducerConfigurationError


@ddt.ddt
class ProducerConfiguratonTest(TestCase):
    """
    Tests to make sure EVENT_BUS_PRODUCER_CONFIG setting connects required signals to appropriate handlers.

    Attributes:
        xblock_info: dummy XBlockData.
    """
    def setUp(self) -> None:
        super().setUp()
        self.xblock_info = XBlockData(
            usage_key='block-v1:edx+DemoX+Demo_course+type@video+block@UaEBjyMjcLW65gaTXggB93WmvoxGAJa0JeHRrDThk',
            block_type='video',
        )

    @patch('openedx_events.apps.get_producer')
    def test_enabled_disabled_events(self, mock_producer):
        """
        Check whether XBLOCK_PUBLISHED is connected to the handler and the handler only produces enabled events.

        Args:
            mock_producer: mock get_producer to inspect the arguments.
        """
        mock_send = Mock()
        mock_producer.return_value = mock_send
        # XBLOCK_PUBLISHED has three configurations where 2 configurations have set enabled as True.
        XBLOCK_PUBLISHED.send_event(xblock_info=self.xblock_info)
        mock_send.send.assert_called()
        mock_send.send.call_count = 2
        expected_call_args = [
            {'topic': 'enabled_topic_a', 'event_key_field': 'xblock_info.usage_key'},
            {'topic': 'enabled_topic_b', 'event_key_field': 'xblock_info.usage_key'}
        ]

        # check that call_args_list only consists of enabled topics.
        call_args = mock_send.send.call_args_list[0][1]
        self.assertEqual(call_args, {**call_args, **expected_call_args[0]})
        call_args = mock_send.send.call_args_list[1][1]
        self.assertEqual(call_args, {**call_args, **expected_call_args[1]})

    @patch("openedx_events.apps.logger")
    @patch('openedx_events.apps.get_producer')
    def test_send_events_with_custom_metadata_not_replayed_by_handler(self, mock_producer, mock_logger):
        """
        Check wheter XBLOCK_PUBLISHED is connected to the handler and the handler
        do not send any events as the signal is marked "from_event_bus".

        Args:
            mock_producer: mock get_producer to inspect the arguments.
            mock_logger: mock logger to inspect the arguments.
        """
        mock_send = Mock()
        mock_producer.return_value = mock_send
        metadata = XBLOCK_PUBLISHED.generate_signal_metadata()

        XBLOCK_PUBLISHED.send_event_with_custom_metadata(metadata, xblock_info=self.xblock_info)

        mock_send.send.assert_not_called()
        mock_logger.debug.assert_called_once_with(
            "Declining to send signal to the Event Bus since that's "
            f"where it was sent from: {XBLOCK_PUBLISHED.event_type} (preventing recursion)"
        )

    @patch('openedx_events.apps.get_producer')
    @override_settings(EVENT_BUS_PRODUCER_CONFIG={})
    def test_events_not_in_config(self, mock_producer):
        """
        Check whether events not included in the configuration are not published as expected.

        Args:
            mock_producer: mock get_producer to inspect the arguments.
        """
        mock_send = Mock()
        mock_producer.return_value = mock_send
        XBLOCK_PUBLISHED.send_event(xblock_info=self.xblock_info)
        mock_producer.assert_not_called()
        mock_send.send.assert_not_called()

    def test_configuration_is_validated(self):
        """
        Check whether EVENT_BUS_PRODUCER_CONFIG setting is validated before connecting handlers.
        """
        with override_settings(EVENT_BUS_PRODUCER_CONFIG=[]):
            with pytest.raises(ProducerConfigurationError, match="should be a dictionary"):
                apps.get_app_config("openedx_events").ready()

        with override_settings(EVENT_BUS_PRODUCER_CONFIG={"invalid.event.type": {}}):
            with pytest.raises(ProducerConfigurationError, match="No OpenEdxPublicSignal of type"):
                apps.get_app_config("openedx_events").ready()

        with override_settings(EVENT_BUS_PRODUCER_CONFIG={"org.openedx.content_authoring.xblock.deleted.v1": ""}):
            with pytest.raises(ProducerConfigurationError, match="should be a dict"):
                apps.get_app_config("openedx_events").ready()

        with override_settings(EVENT_BUS_PRODUCER_CONFIG={"org.openedx.content_authoring.xblock.deleted.v1":
                                                          {"topic": ""}}):
            with pytest.raises(ProducerConfigurationError, match="One of the configuration objects is not a"
                                                                 " dictionary"):
                apps.get_app_config("openedx_events").ready()

        with override_settings(
            EVENT_BUS_PRODUCER_CONFIG={
                "org.openedx.content_authoring.xblock.deleted.v1": {"topic": {"enabled": True}}
            }
        ):
            with pytest.raises(ProducerConfigurationError, match="missing 'event_key_field' key."):
                apps.get_app_config("openedx_events").ready()

        with override_settings(
            EVENT_BUS_PRODUCER_CONFIG={
                "org.openedx.content_authoring.xblock.deleted.v1":
                {
                    "some": {"enabled": 1, "event_key_field": "some"}
                }
            }
        ):
            with pytest.raises(
                ProducerConfigurationError,
                match="Expected type: <class 'bool'> for 'enabled', found: <class 'int'>"
            ):
                apps.get_app_config("openedx_events").ready()

    @patch('openedx_events.apps.get_producer')
    def test_event_data_key_in_handler(self, mock_producer):
        """
        Check whether event_data is constructed properly in handlers.
        """
        mock_send = Mock()
        mock_producer.return_value = mock_send
        XBLOCK_DELETED.send_event(xblock_info=self.xblock_info)
        mock_send.send.assert_called_once()

        call_args = mock_send.send.call_args_list[0][1]
        self.assertIn("xblock_info", call_args["event_data"])
