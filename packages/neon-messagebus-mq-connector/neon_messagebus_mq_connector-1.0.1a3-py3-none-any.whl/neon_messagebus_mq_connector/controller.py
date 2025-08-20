# NEON AI (TM) SOFTWARE, Software Development Kit & Application Framework
# All trademark and other rights reserved by their respective owners
# Copyright 2008-2025 Neongecko.com Inc.
# Contributors: Daniel McKnight, Guy Daniels, Elon Gasper, Richard Leeds,
# Regina Bloomstine, Casimiro Ferreira, Andrii Pernatii, Kirill Hrymailo
# BSD-3 License
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
# 1. Redistributions of source code must retain the above copyright notice,
#    this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from this
#    software without specific prior written permission.
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO,
# THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
# PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR
# CONTRIBUTORS  BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
# EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
# PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS;  OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE,  EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import time
import pika

from typing import Optional
from ovos_bus_client.client import MessageBusClient
from ovos_bus_client.message import Message
from ovos_utils.log import LOG, log_deprecation
from ovos_utils import create_daemon
from neon_utils.metrics_utils import Stopwatch
from neon_utils.socket_utils import b64_to_dict
from ovos_config.config import Configuration
from neon_mq_connector.connector import MQConnector, ConsumerThreadInstance
from pydantic import ValidationError
from neon_data_models.models.api.mq.neon import NeonApiMessage
from neon_data_models.models.base.contexts import MQContext
from neon_messagebus_mq_connector.enums import NeonResponseTypes


class ChatAPIProxy(MQConnector):
    """
    Proxy module for establishing connection between Neon Core and an MQ Broker
    """

    def __init__(self, config: dict, service_name: str, error_callback: Optional[callable] = None):
        config = config or Configuration()
        mq_config = config.get("MQ", config)
        super().__init__(mq_config, service_name)
        self.bus_config = config.get("websocket")
        if config.get("MESSAGEBUS"):
            log_deprecation("MESSAGEBUS config is deprecated. use `websocket`",
                            "1.0.0")
            self.bus_config = config.get("MESSAGEBUS")
        self._vhost = '/neon_chat_api'
        self._bus = None
        self.connect_bus()
        error_callback = error_callback or self.default_error_handler
        self.register_consumer(name=f'neon_api_request_{self.service_id}',
                               vhost=self.vhost,
                               queue=f'neon_chat_api_request_{self.service_id}',
                               callback=self.handle_user_message,
                               on_error=error_callback,
                               auto_ack=False,
                               restart_attempts=0)
        self.register_consumer(name='neon_request_consumer',
                               vhost=self.vhost,
                               queue='neon_chat_api_request',
                               callback=self.handle_user_message,
                               on_error=error_callback,
                               auto_ack=False,
                               restart_attempts=0)
        self.response_timeouts = {
            NeonResponseTypes.TTS: 60,
            NeonResponseTypes.STT: 60
        }

    def register_bus_handlers(self):
        """Convenience method to gather message bus handlers"""
        self._bus.on('klat.response', self.handle_neon_message)
        self._bus.on('complete.intent.failure', self.handle_neon_message)
        self._bus.on('intent_aborted', self.handle_neon_message)
        self._bus.on('neon.profile_update', self.handle_neon_profile_update)
        self._bus.on('neon.clear_data', self.handle_neon_message)
        self._bus.on('neon.audio_input.response', self.handle_neon_message)
        self._bus.on('neon.get_tts.response', self.handle_neon_message)
        self._bus.on('neon.get_stt.response', self.handle_neon_message)
        self._bus.on('ovos.languages.stt.response', self.handle_neon_message)
        self._bus.on('ovos.languages.tts.response', self.handle_neon_message)
        self._bus.on('neon.languages.skills.response', self.handle_neon_message)
        self._bus.on('neon.languages.get.response', self.handle_neon_message)
        self._bus.on('neon.alert_expired', self.handle_neon_message)
        self._bus.on('neon.skill_api.get.response', self.handle_neon_message)

    def connect_bus(self, refresh: bool = False):
        """
        Convenience method for establishing connection to message bus
        :param refresh: To refresh existing connection
        """
        if not self._bus or refresh:
            self._bus = MessageBusClient(host=self.bus_config['host'],
                                         port=int(self.bus_config.get('port',
                                                                      8181)),
                                         route=self.bus_config.get('route',
                                                                   '/core'))
            self.register_bus_handlers()
            self._bus.run_in_thread()

    @property
    def bus(self) -> MessageBusClient:
        """
        Connects to Message Bus if no connection was established
        :return: connected message bus client instance
        """
        if not self._bus:
            self.connect_bus()
        return self._bus

    def handle_neon_message(self, message: Message):
        """
        Handles responses from Neon Core, optionally reformatting response data
        before forwarding to the MQ bus.
        :param message: Received Message object
        """
        response_handled = time.time()
        _stopwatch = Stopwatch()
        with _stopwatch:
            try:
                response_message = NeonApiMessage(msg_type=message.msg_type,
                                                  data=message.data,
                                                  context=message.context)
                response_message.routing_key = response_message.routing_key or \
                    "neon_chat_api_response"
            except ValidationError as e:
                if message.context.get("mq"):
                    LOG.info(f"message={message}")
                    LOG.error(f"Failed to parse response message: {e}")
                return
            except TypeError as e:
                LOG.error(f"Failed to parse message: {message.serialize()}")
                LOG.exception(e)
                return

        LOG.debug(f'Processed neon response: {message.msg_type} in '
                  f'{_stopwatch.time}s')

        # Add timing metrics
        if response_message.context.timing.response_sent:
            response_message.context.timing.mq_from_core = response_handled - \
                response_message.context.timing.response_sent.timestamp()
        response_message.context.timing.mq_response_handler = _stopwatch.time

        LOG.debug(f"Sending message ({message.msg_type}) with "
                  f"routing_key={response_message.routing_key}")
        self.send_message(request_data=response_message.model_dump(),
                           queue=response_message.routing_key)
        LOG.debug(
            f"Sent message with routing_key={response_message.routing_key}")

    def handle_neon_profile_update(self, message: Message):
        """
        Handles profile updates from Neon Core. Ensures routing_key is defined
        to avoid publishing private profile values to a shared queue
        :param message: Message containing the updated user profile
        """
        if message.context.get('mq', {}).get('routing_key'):
            LOG.info(f"handling profile update for "
                     f"user={message.data['profile']['user']['username']}")
            self.handle_neon_message(message)
        else:
            # No mq context means this is probably local
            LOG.debug(f"ignoring profile update for "
                      f"user={message.data['profile']['user']['username']}")

    @classmethod
    def validate_request(cls, msg_data: dict):
        """
        Fetches the relevant template models and validates provided message data
        iteratively through them
        :param msg_data: message data for validation
        :return: validation details(None if validation passed),
                 input data with proper data types and filled default fields
        """
        log_deprecation("This method is deprecated without replacement", 
                        "2.0.0")
        return None, msg_data

    @staticmethod
    def validate_message_context(message: Message) -> bool:
        """
        Validates message context so its relevant data could be fetched once
        a response is received
        """
        log_deprecation("This method is deprecated without replacement", 
                        "2.0.0")
        return True

    def handle_user_message(self,
                            channel: pika.channel.Channel,
                            method: pika.spec.Basic.Return,
                            properties: pika.spec.BasicProperties,
                            body: bytes):
        """
        Transfers requests from MQ API to Neon Message Bus API

        :param channel: MQ channel object (pika.channel.Channel)
        :param method: MQ return method (pika.spec.Basic.Return)
        :param properties: MQ properties (pika.spec.BasicProperties)
        :param body: request body (bytes)

        """
        input_received = time.time()
        LOG.debug(f"Handle delivery_tag={method.delivery_tag}")
        if not isinstance(body, bytes):
            channel.basic_nack(method.delivery_tag)
            raise TypeError(f'Invalid body received, expected: bytes;'
                            f' got: {type(body)}')
        channel.basic_ack(method.delivery_tag)
        _stopwatch = Stopwatch()
        _stopwatch.start()
        dict_data = b64_to_dict(body)
        LOG.info(f'Received user message: {dict_data.get("msg_type")}|'
            f'data={dict_data["data"].keys()}|'
            f'context={dict_data["context"].keys()}')
        try:
            # TODO: Klat context was previously required for audio responses.
            # These are now handled for any response with `MQ` context.
            dict_data['context'].setdefault('klat_data', {"cid": "", "sid": ""})
            neon_api_message = NeonApiMessage(**dict_data)
            if not neon_api_message.context.mq:
                # backwards-compat parsing
                LOG.warning(f"Handling legacy message from "
                            f"client={neon_api_message.context.client}. Please "
                            f"update to include `mq` context")
                neon_api_message.context.mq = MQContext(**dict_data)

        except ValidationError as e:
            LOG.error(e)
            # This Message is malformed
            context = dict_data.pop("context")
            response = Message("klat.error", {"error": repr(e),
                                              "data": dict_data},
                               context)
            response.context.setdefault("klat_data", {})
            response.context['klat_data'].setdefault('routing_key',
                                                     'neon_chat_api_error')
            self.handle_neon_message(response)
            _stopwatch.stop()
            return

        # Add timing metrics
        if neon_api_message.context.timing.client_sent:
            neon_api_message.context.timing.mq_from_client = \
                input_received - neon_api_message.context.timing.client_sent.timestamp()

        _stopwatch.stop()
        neon_api_message.context.timing.mq_input_handler = _stopwatch.time
        message = neon_api_message.as_messagebus_message()
        if message.context.get('ident') and \
                message.msg_type in ("neon.get_stt", "neon.get_tts",
                                     "neon.audio_input"):
            # If there's an ident in context, API methods will emit that.
            # This isn't explicitly defined but this pattern is often used
            # to associate responses with the original request.

            # This is here for backwards-compat. Modules implementing
            # `neon-data-models` will not send an `ident` key
            create_daemon(self._get_messagebus_response, args=(message,),
                            autostart=True)
        elif neon_api_message.msg_type in ("neon.skill_api.call"):
            # The Skill API uses arbitrary message types; this translation 
            # allows for a simplified MQ API that maps onto the Messagebus
            # per-method Message types.
            response_msg_type = f"{message.msg_type}.response"
            create_daemon(self._get_messagebus_response, args=(message, response_msg_type),
                          autostart=True)
        else:
            # No ident means we'll get a plain `msg_type.response` which has
            # a handler already registered. `wait_for_response` is not used
            # because multiple concurrent requests can cause responses to be
            # disassociated with the request message.
            self.bus.emit(message)
        LOG.debug(f"Handler Complete in {time.time() - input_received}s")

    def _get_messagebus_response(self, message: Message, 
                                 response_type: Optional[str] = None):
        """
        Helper method to get a response on the Messagebus that can be threaded
        so as not to block MQ handling.
        @param message: Message object to get a response for
        """
        response_type = response_type or message.context['ident']
        resp = self.bus.wait_for_response(message,
                                          response_type, 30)
        if resp:
            # Override msg_type for handler; context contains routing
            resp.msg_type = f"{message.msg_type}.response"
            self.handle_neon_message(resp)
        else:
            LOG.warning(f"No response to: {message.msg_type}")

    def format_response(self, response_type: NeonResponseTypes,
                        message: Message) -> dict:
        """
        Reformat received response by Neon API for Klat based on type
        :param response_type: response type from NeonResponseTypes Enum
        :param message: Neon MessageBus Message object
        :returns formatted response dict
        """
        log_deprecation("This method is deprecated without replacement",
                        "2.0.0")
        msg_error = message.data.get('error')
        if msg_error:
            LOG.error(f'Failed to fetch data for context={message.context} - '
                      f'{msg_error}')
            return {}
        timeout = self.response_timeouts.get(response_type, 30)
        if int(time.time()) - message.context.get('created_on', 0) > timeout:
            LOG.warning(f'Message = {message} received timeout on '
                        f'{response_type} (>{timeout} seconds)')
            return {}
        if response_type == NeonResponseTypes.TTS:
            lang = list(message.data)[0]
            gender = message.data[lang].get('genders', ['female'])[0]
            audio_data_b64 = message.data[lang]['audio'][gender]

            response_data = {
                'audio_data': audio_data_b64,
                'lang': lang,
                'gender': gender,
                'context': message.context
            }
        elif response_type == NeonResponseTypes.STT:
            transcripts = message.data.get('transcripts', [''])
            LOG.info(f'transcript candidates received - {transcripts}')
            response_data = {
                'transcript': transcripts[0],
                'other_transcripts': [transcript for transcript in
                                      transcripts if
                                      transcript != transcripts[0]],
                'lang': message.context.get('lang', 'en-us'),
                'context': message.context
            }
        else:
            LOG.warning(f'Failed to response response type -> '
                        f'{response_type}')
            response_data = {}
        return response_data
