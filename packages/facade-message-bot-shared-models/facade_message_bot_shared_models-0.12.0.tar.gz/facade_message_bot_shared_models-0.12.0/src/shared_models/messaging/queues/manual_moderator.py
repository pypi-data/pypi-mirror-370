from faststream.rabbit import RabbitQueue, QueueType
from faststream.rabbit.schemas.queue import QuorumQueueArgs


manual_moderator_queue = RabbitQueue(
    "moderator.manual",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "dlx.moderator.manual",
            "x-dead-letter-strategy": "at-least-once",
            "x-overflow": "reject-publish",
        }
    ),
)

manual_moderator_dlx_queue = RabbitQueue(
    "dlx.moderator.manual",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)

second_manual_moderator_queue = RabbitQueue(
    "moderator.manual.second",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "dlx.moderator.manual.second",
            "x-dead-letter-strategy": "at-least-once",
            "x-overflow": "reject-publish",
        }
    ),
)

second_manual_moderator_dlx_queue = RabbitQueue(
    "dlx.moderator.manual.second",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)
