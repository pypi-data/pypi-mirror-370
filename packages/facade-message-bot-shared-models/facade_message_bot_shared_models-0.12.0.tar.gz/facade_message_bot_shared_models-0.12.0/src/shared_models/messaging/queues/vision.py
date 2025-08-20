from faststream.rabbit import RabbitQueue, QueueType
from faststream.rabbit.schemas.queue import QuorumQueueArgs


vision_notification_queue = RabbitQueue(
    "vision.notification",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "dlx.vision.notification",
            "x-dead-letter-strategy": "at-least-once",
            "x-overflow": "reject-publish",
        }
    ),
)

vision_notification_dlx_queue = RabbitQueue(
    "dlx.vision.notification",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)
