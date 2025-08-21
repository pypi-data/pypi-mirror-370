import json
import logging
import time
import threading
import uuid

import casbin
import pika
from pika.exchange_type import ExchangeType

LOGGER = logging.getLogger(__name__)


class RabbitWatcher:
    def __init__(
        self,
        host="localhost",
        port=5672,
        virtual_host="/",
        username="guest",
        password="guest",
        key="casbin-policy-updated",
        local_id=None,
        **kwargs,
    ):
        self.connection = None
        self.pub_channel = None
        self.key = key
        self.callback = None
        self.local_id = local_id if local_id is not None else str(uuid.uuid4())
        self.mutex = threading.Lock()
        self.subscribe_event = threading.Event()
        self.subscribe_thread = threading.Thread(target=self.start_watch, daemon=True)
        credentials = pika.PlainCredentials(username, password)
        self.rabbit_config = pika.ConnectionParameters(
            host=host,
            port=port,
            virtual_host=virtual_host,
            credentials=credentials,
            **kwargs,
        )

    def create_client(self):
        self.connection = pika.BlockingConnection(self.rabbit_config)
        self.pub_channel = self.connection.channel()
        self.pub_channel.exchange_declare(
            exchange=self.key, exchange_type=ExchangeType.fanout
        )

    def close(self):
        self.pub_channel.close()
        self.connection.close()

    def set_update_callback(self, callback):
        """
        sets the callback function to be called when the policy is updated
        :param callable callback: callback(event)
            - event: event received from the rabbitmq
        :return:
        """
        self.mutex.acquire()
        self.callback = callback
        self.mutex.release()

    def update(self):
        """
        update the policy
        """
        msg = MSG("Update", self.local_id, "", "", "")
        self.pub_channel.basic_publish(
            exchange=self.key, routing_key="", body=msg.marshal_binary()
        )
        return True

    def update_for_add_policy(self, section, ptype, *params):
        """
        update for add policy
        :param section: section
        :param ptype:   policy type
        :param params:  other params
        :return:    True if updated
        """

        def func():
            msg = MSG("UpdateForAddPolicy", self.local_id, section, ptype, params)
            return self.pub_channel.basic_publish(
                exchange=self.key, routing_key="", body=msg.marshal_binary()
            )

        return self.log_record(func)

    def update_for_remove_policy(self, section, ptype, *params):
        """
        update for remove policy
        :param section: section
        :param ptype:   policy type
        :param params:  other params
        :return:    True if updated
        """

        def func():
            msg = MSG("UpdateForRemovePolicy", self.local_id, section, ptype, params)
            return self.pub_channel.basic_publish(
                exchange=self.key, routing_key="", body=msg.marshal_binary()
            )

        return self.log_record(func)

    def update_for_remove_filtered_policy(self, section, ptype, field_index, *params):
        """
        update for remove filtered policy
        :param section: section
        :param ptype:   policy type
        :param field_index: field index
        :param params: other params
        :return:
        """

        def func():
            msg = MSG(
                "UpdateForRemoveFilteredPolicy",
                self.local_id,
                section,
                ptype,
                f"{field_index} {' '.join(params)}",
            )
            return self.pub_channel.basic_publish(
                exchange=self.key, routing_key="", body=msg.marshal_binary()
            )

        return self.log_record(func)

    def update_for_save_policy(self, model: casbin.Model):
        """
        update for save policy
        :param model: casbin model
        :return:
        """

        def func():
            msg = MSG(
                "UpdateForSavePolicy",
                self.local_id,
                "",
                "",
                model.to_text(),
            )
            return self.pub_channel.basic_publish(
                exchange=self.key, routing_key="", body=msg.marshal_binary()
            )

        return self.log_record(func)

    def update_for_add_policies(self, section, ptype, *params):
        """
        update for add policies
        :param section: section
        :param ptype:   policy type
        :param params:  other params
        :return:
        """

        def func():
            msg = MSG("UpdateForAddPolicies", self.local_id, section, ptype, params)
            return self.pub_channel.basic_publish(
                exchange=self.key, routing_key="", body=msg.marshal_binary()
            )

        return self.log_record(func)

    def update_for_remove_policies(self, section, ptype, *params):
        """
        update for remove policies
        :param section: section
        :param ptype:   policy type
        :param params:  other params
        :return:
        """

        def func():
            msg = MSG("UpdateForRemovePolicies", self.local_id, section, ptype, params)
            return self.pub_channel.basic_publish(
                exchange=self.key, routing_key="", body=msg.marshal_binary()
            )

        return self.log_record(func)

    @staticmethod
    def log_record(f: callable):
        try:
            result = f()
        except Exception as e:
            print(f"Casbin RabbitMQ Watcher error: {e}")
        else:
            return result

    def start_watch(self):
        """
        starts the watch thread
        :return:
        """

        def _watch_callback(ch, method, properties, body):
            self.mutex.acquire()
            if self.callback is not None:
                self.callback(body)
            self.mutex.release()
            if ch.is_open:
                ch.basic_ack(method.delivery_tag)
            else:
                LOGGER.warning("sub channel has closed.")

        while True:
            try:
                sub_connection = pika.BlockingConnection(self.rabbit_config)
                sub_channel = sub_connection.channel()
                sub_channel.exchange_declare(
                    exchange=self.key, exchange_type=ExchangeType.fanout
                )
                result = sub_channel.queue_declare(queue="", exclusive=True)
                queue_name = result.method.queue
                sub_channel.queue_bind(exchange=self.key, queue=queue_name)
                sub_channel.basic_consume(
                    queue=queue_name, on_message_callback=_watch_callback
                )
                try:
                    if not self.subscribe_event.is_set():
                        self.subscribe_event.set()
                    sub_channel.start_consuming()

                except KeyboardInterrupt:
                    sub_channel.stop_consuming()

                print("sub connection close")
                sub_connection.close()
                break
                # Do not recover if connection was closed by broker
            except pika.exceptions.ConnectionClosedByBroker:
                break
                # Do not recover on channel errors
            except pika.exceptions.AMQPChannelError:
                break
                # Recover on all other connection errors
            except pika.exceptions.AMQPConnectionError:
                continue


class MSG:
    def __init__(self, method="", id="", sec="", ptype="", *params):
        self.method: str = method
        self.id: str = id
        self.sec: str = sec
        self.ptype: str = ptype
        self.params = params

    def marshal_binary(self):
        return json.dumps(self.__dict__)

    @staticmethod
    def unmarshal_binary(data: bytes):
        loaded = json.loads(data)
        return MSG(**loaded)


def new_watcher(
    host="localhost",
    port=5672,
    virtual_host="/",
    username="guest",
    password="guest",
    key="casbin-policy-updated",
    **kwargs,
):
    """
    creates a new watcher
    :param host:
    :param port:
    :param virtual_host:
    :param username:
    :param password:
    :param key:
    :return: a new watcher
    """
    rabbit = RabbitWatcher(
        host=host,
        port=port,
        virtual_host=virtual_host,
        username=username,
        password=password,
        key=key,
        **kwargs,
    )
    rabbit.subscribe_thread.start()
    rabbit.subscribe_event.wait(timeout=5)
    rabbit.create_client()
    LOGGER.info("Rabbitmq watcher started")
    return rabbit
