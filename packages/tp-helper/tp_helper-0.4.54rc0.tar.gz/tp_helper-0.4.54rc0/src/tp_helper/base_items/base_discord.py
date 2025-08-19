from tp_helper.discord_helper import DiscordHelper


class BaseDiscord:
    def __init__(self, discord: DiscordHelper):
        self.discord = discord