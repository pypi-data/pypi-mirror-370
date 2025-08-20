import os


def get_tortoise_orm_config(
    user: str, password: str, database: str, host: str = "localhost", port: int = 5432
) -> dict:
    """Get Tortoise ORM configuration.

    Args:
        user (str): Database user name.
        password (str): Database user password.
        database (str): Database name.
        host (str, optional): Database host. Defaults to "localhost".
        port (int, optional): Database port. Defaults to 5432.

    Returns:
        dict: Tortoise ORM configuration dictionary.
    """
    return {
        "connections": {
            "default": {
                "engine": "tortoise.backends.asyncpg",
                "credentials": {
                    "host": host,
                    "port": port,
                    "user": user,
                    "password": password,
                    "database": database,
                },
            },
        },
        "apps": {
            "models": {
                "models": ["shared_models.database.models", "aerich.models"],
                "default_connection": "default",
            }
        },
    }


TORTOISE_ORM_FROM_ENV = {
    "connections": {
        "default": {
            "engine": "tortoise.backends.asyncpg",
            "credentials": {
                "host": os.getenv("DB_HOST", "localhost"),
                "port": int(os.getenv("DB_PORT", 5432)),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME"),
            },
        },
    },
    "apps": {
        "models": {
            "models": ["shared_models.database.models", "aerich.models"],
            "default_connection": "default",
        }
    },
}
