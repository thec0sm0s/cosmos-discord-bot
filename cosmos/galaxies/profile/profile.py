from .. import Cog


class Profile(Cog):

    def __init__(self, plugin):
        super().__init__()
        self.plugin = plugin
