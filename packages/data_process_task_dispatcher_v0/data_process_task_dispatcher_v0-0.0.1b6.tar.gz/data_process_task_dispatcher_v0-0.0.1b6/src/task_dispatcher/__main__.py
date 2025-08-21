"""
Main entry point for starting message queue consumers.
"""

from task_dispatcher.consumers.paper_match import paper_match_consumer
from task_dispatcher.mq_v1.config import ConfigurationManager, MQConfig
from task_dispatcher.mq_v1.consumer_manager import start_multiple_consumers
from task_dispatcher.config import settings
from task_dispatcher.logger import logger
import time

config = MQConfig(
    connection_url=settings.rabbitmq.APP_MQ_CONNECTION_URL,
    aggregator_url=settings.rabbitmq.APP_MQ_AGGREGATOR_URL,
    prefetch_count=1,
    message_ttl=86400
)
ConfigurationManager.init(config=config)

def main():
    # consumers = [
    #     paper_match_consumer,
    #     # run_add_new_paper_match.main,
    # ]

    # start_multiple_consumers(consumers, wait=True)
    """Start all message queue consumers."""
    print("hello")
    while True:
        logger.info("hello")
        time.sleep(1)
    # Start all consumers
    # paper_match_consumer.start()


if __name__ == "__main__":
    main()
