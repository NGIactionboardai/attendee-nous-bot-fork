import os
import requests
import logging

logger = logging.getLogger(__name__)

class FlyBotLauncher:
    def launch(self, bot):
        fly_api_token = os.getenv("FLY_API_TOKEN")
        if not fly_api_token:
            raise RuntimeError("FLY_API_TOKEN is not set")

        app_name = os.getenv("FLY_BOT_APP", "attendee-worker")
        region = os.getenv("FLY_REGION", "iad")

        payload = {
            "name": f"bot-{bot.id}",
            "region": region,
            "config": {
                "image": "registry.fly.io/attendee-worker:deployment-01KDFHDWJX9GZ160KMY2D1DFHV",
                "env": {
                    "BOT_ID": str(bot.id),
                    "DJANGO_SETTINGS_MODULE": "attendee.settings.production",
                },
                "init": {
                    "cmd": [
                        "python",
                        "manage.py",
                        "run_bot",
                        "--botid",
                        str(bot.id)
                    ]
                },
                "restart": {
                    "policy": "no"
                },
                "auto_destroy": True,
                "guest": {
                    "cpu_kind": "shared",
                    "cpus": 4,
                    "memory_mb": 2048
                }
            }
        }

        resp = requests.post(
            f"https://api.machines.dev/v1/apps/{app_name}/machines",
            headers={
                "Authorization": f"Bearer {fly_api_token}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=10,
        )

        if resp.status_code >= 300:
            logger.error("Fly machine launch failed: %s", resp.text)
            resp.raise_for_status()

        logger.info("Launched Fly machine for bot %s", bot.id)
