"""
Cosmos: A General purpose Discord bot.
Copyright (C) 2020 thec0sm0s

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

from image_processor_client import Client as ImageProcessorClient

from discordDB import DiscordDB
from discord import Intents
from discord.ext import commands

from .functions import *
from .utilities import *


class InitialTasks(commands.Bot):

    @classmethod
    def __get_prefix(cls, bot, message):
        prefixes = bot.configs.cosmos.prefixes.copy()
        if message.guild:
            try:
                prefixes = bot.guild_cache.prefixes.get(message.guild.id) or prefixes
            except AttributeError:
                if bot.guild_cache.prefixes is None:
                    raise AttributeError("Attribute self.guild_cache isn't overridden by guild galaxy.")
        return commands.when_mentioned_or(*prefixes)(bot, message)

    def __init__(self, *, version=str(), release=str()):
        self.time = None
        self.configs = None
        self.eh = None
        self.log = None
        self.cache = None
        self.db_client = None
        self.db = None
        self.emotes = None
        self.plugins = None
        self.theme = None
        self.image_processor = None
        self.scheduler = None
        self.server = None
        self.profile_cache = None    # Intended to be overridden by PROFILE galaxy.
        self.guild_cache = None    # Intended to be overridden by GUILD galaxy.
        self.version = version
        self.release = release
        self._init_time()
        self._init_configs()
        self._init_utilities()
        super().__init__(
            command_prefix=self.__get_prefix, case_insensitive=True, help_command=CosmosHelp(), intents=Intents.all()
        )
        self._init_logger()
        self._init_exception_handler()
        self._init_database()
        self._init_caches()
        self._init_emotes()
        self._init_scheduler()
        self._init_plugins()
        self._init_theme()
        self._init_image_processor()
        self._init_misc_tasks()
        self._init_server()

    @Time.calc_time
    def _init_time(self):
        print("Initialising Cosmos time.")
        self.time = Time()

    @Time.calc_time
    def _init_utilities(self):
        print("Initialising utilities.")
        self.utilities = Utility(self)

    @Time.calc_time
    def _init_configs(self):
        print("Initialising configs.")
        self.configs = ConfigHandler()
        release = f"v{self.version}-{self.release}"
        self.configs.sentry.release = release
        self.configs.sentry.raw["release"] = release

    @Time.calc_time
    def _init_logger(self):
        print("Initialising logger.")
        self.log = LoggerHandler(self)

    @Time.calc_time
    def _init_exception_handler(self):
        self.log.info("Initialising exception handler.")
        self.eh = ExceptionHandler(self)
        try:
            self.eh.sentry.init(**self.configs.sentry.raw)
        except self.eh.sentry.utils.BadDsn:
            self.log.error("Invalid sentry DSN provided.")

    @Time.calc_time
    def _init_database(self):
        self.log.info("Initialising database.")
        self.db_client = DatabaseClient(self)
        self.db = self.db_client.db
        self.discordDB = DiscordDB(self, self.configs.db.channel_id)

    @Time.calc_time
    def _init_caches(self):
        self.log.info("Initialising caches.")
        self.cache = CacheHandler(self)

    @Time.calc_time
    def _init_emotes(self):
        self.log.info("Initialising cosmos emotes.")
        self.emotes = CosmosEmotes(self)

    @Time.calc_time
    def _init_plugins(self):
        self.log.info("Initialising plugins.")
        self.plugins = PluginHandler(self)
        self.plugins.load_all()    # Here since Plugin requires self.bot.plugins to load itself.

    @Time.calc_time
    def _init_theme(self):
        self.log.info("Initialising cosmos theme.")
        self.theme = CosmosTheme(self)

    @Time.calc_time
    def _init_image_processor(self):
        self.log.info("Initialising image processor client.")
        self.image_processor = ImageProcessorClient(
            self.configs.image_processor.base_url, loop=self.loop)

    @Time.calc_time
    def _init_scheduler(self):
        self.log.info("Initializing schedulers.")
        self.scheduler = Scheduler(self)

    @Time.calc_time
    def _init_server(self):
        self.log.info("Initializing cosmos server.")
        self.server = CosmosServer(self)

    def _init_misc_tasks(self):
        self.get_command("help").inescapable = True    # Dynamically mark help command as inescapable.
