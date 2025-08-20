from faststream.rabbit import RabbitExchange, ExchangeType


moderator_exchange = RabbitExchange(
    "moderator",
    type=ExchangeType.DIRECT,
    durable=True,
)

bot_exchange = RabbitExchange(
    "bot",
    type=ExchangeType.DIRECT,
    durable=True,
)

vision_exchange = RabbitExchange(
    "vision",
    type=ExchangeType.DIRECT,
    durable=True,
)

dlx_exchange = RabbitExchange(
    "dlx",
    type=ExchangeType.DIRECT,
    durable=True,
)
