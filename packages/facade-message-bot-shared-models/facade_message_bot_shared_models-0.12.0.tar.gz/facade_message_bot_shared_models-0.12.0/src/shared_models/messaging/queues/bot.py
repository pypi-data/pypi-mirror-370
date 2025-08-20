from faststream.rabbit import RabbitQueue, QueueType
from faststream.rabbit.schemas.queue import QuorumQueueArgs


bot_moderate_response_queue = RabbitQueue(
    "bot.moderate.response",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "dlx.bot.moderate.response",
            "x-dead-letter-strategy": "at-least-once",
            "x-overflow": "reject-publish",
        }
    ),
)

bot_moderate_response_dlx_queue = RabbitQueue(
    "dlx.bot.moderate.response",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)

bot_message_shown_queue = RabbitQueue(
    "bot.message.shown",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
    arguments=QuorumQueueArgs(
        {
            "x-dead-letter-exchange": "dlx",
            "x-dead-letter-routing-key": "dlx.bot.message.shown",
            "x-dead-letter-strategy": "at-least-once",
            "x-overflow": "reject-publish",
        }
    ),
)

bot_message_shown_dlx_queue = RabbitQueue(
    "dlx.bot.message.shown",
    queue_type=QueueType.QUORUM,
    durable=True,
    declare=True,
)
