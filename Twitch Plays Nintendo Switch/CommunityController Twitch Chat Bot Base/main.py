from twitchio.ext import commands
import socket
import time

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        super().__init__(token='token', prefix="!", initial_channels=['channelName'])

    async def sendCommand(self, content):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("192.168.1.179", 6000))
        print('Twitch pressed a button!')

        content += '\r\n'  # important for the parser on the switch side
        s.sendall(content.encode())

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print('Connected to Nintendo Switch')

#uppercase right joycon Buttons
    @commands.command()
    async def A(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click A")

    @commands.command()
    async def B(self, ctx: commands.Context):
            # Clicks the A Button
            # example !A
        await self.sendCommand("click B")

    @commands.command()
    async def X(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click X")

    @commands.command()
    async def Y(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click Y")

    @commands.command()
    async def ZR(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click ZR")

    @commands.command()
    async def ZL(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click ZL")

#lowercase right joycon buttons
    @commands.command()
    async def a(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click A")

    @commands.command()
    async def b(self, ctx: commands.Context):
            # Clicks the A Button
            # example !A
        await self.sendCommand("click B")

    @commands.command()
    async def x(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click X")

    @commands.command()
    async def y(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click Y")

    @commands.command()
    async def zr(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click ZR")

    @commands.command()
    async def zl(self, ctx: commands.Context):
        # Clicks the A Button
        # example !A
        await self.sendCommand("click ZL")
bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.