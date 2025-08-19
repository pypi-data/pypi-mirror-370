import json
import logging

import pika
from base_api_utils.utils import config
from celery import shared_task
from pika.adapters.utils.connection_workflow import AMQPConnectorStackTimeout
from pika.exceptions import AMQPConnectionError


@shared_task(bind=True,
             autoretry_for=(AMQPConnectionError,AMQPConnectorStackTimeout,),
             retry_backoff=True,
             retry_kwargs={'max_retries': 5})
def publish_to_exchange(self, message, routing_key, exchange = None):
    logging.getLogger('api').debug(f'calling publish_to_exchange task (id: {self.request.id})...')

    rabbit_host = config('RABBIT.HOST')
    rabbit_port = config('RABBIT.PORT')
    rabbit_exchange = exchange if not exchange is None else config('RABBIT.EXCHANGE')
    rabbit_default_routing_key = routing_key if not routing_key is None else config('RABBIT.DEFAULT_ROUTING_KEY')

    credentials = pika.PlainCredentials(config('RABBIT.USER'), config('RABBIT.PASSWORD'))
    cnn = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host,
                                                            port=rabbit_port,
                                                            credentials=credentials))
    channel = cnn.channel()
    channel.exchange_declare(exchange=rabbit_exchange, exchange_type='direct', durable=True)

    message_body = json.dumps(message).encode('utf-8')

    channel.basic_publish(
        exchange=rabbit_exchange,
        routing_key=rabbit_default_routing_key,
        body=message_body,
        properties=pika.BasicProperties(
            delivery_mode=2,  # persistent message
        ),
    )
    cnn.close()
    logging.getLogger('api').debug(f'Message sent to exchange {rabbit_exchange} using routing_key {rabbit_default_routing_key}')
    return
