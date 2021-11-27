from twitchio.ext import commands
import socket
import time
from dotenv import dotenv_values

class Bot(commands.Bot):

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        config = dotenv_values(".env")
        # Make sure token is non-empty
        if 'OAUTH_TOKEN' not in config.keys():
            raise ValueError('OAUTH_TOKEN is not set')
        if 'CHANNEL_NAME' not in config.keys():
            raise ValueError('CHANNEL_NAME is not set')

        token = config.get("OAUTH_TOKEN")
        channel = config.get("CHANNEL_NAME")

        super().__init__(token, prefix="!", initial_channels=[channel])

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
        # twitch command = !A
        await self.sendCommand("click A")

    @commands.command()
    async def B(self, ctx: commands.Context):
            # Clicks the B Button
            # twitch command = !B
        await self.sendCommand("click B")

    @commands.command()
    async def X(self, ctx: commands.Context):
        # Clicks the X Button
        # twitch command = !X
        await self.sendCommand("click X")

    @commands.command()
    async def Y(self, ctx: commands.Context):
        # Clicks the Y Button
        # twitch command = !Y
        await self.sendCommand("click Y")

    @commands.command()
    async def ZR(self, ctx: commands.Context):
        # Clicks the ZR Button
        # twitch command = !ZR
        await self.sendCommand("click ZR")

    @commands.command()
    async def ZL(self, ctx: commands.Context):
        # Clicks the ZL Button
        # twitch command = !ZL
        await self.sendCommand("click ZL")

    @commands.command()
    async def L(self, ctx: commands.Context):
        # Clicks the L Button
        # twitch command = !L
        await self.sendCommand("click L")

    @commands.command()
    async def R(self, ctx: commands.Context):
        # Clicks the R Button
        # twitch command = !R
        await self.sendCommand("click R")

    @commands.command()
    async def DLEFT(self, ctx: commands.Context):
        # Clicks the DPAD LEDT
        # twitch command = !DLEFT
        await self.sendCommand("click DLEFT")
    @commands.command()
    async def DRIGHT(self, ctx: commands.Context):
        # Clicks the DPAD RIGHT
        # twitch command = !DLEFT
        await self.sendCommand("click DRIGHT")
    @commands.command()
    async def DDOWN(self, ctx: commands.Context):
        # Clicks DPAD DOWN
        # twitch command = !DLEFT
        await self.sendCommand("click DDOWN")
    @commands.command()
    async def DUP(self, ctx: commands.Context):
        # Clicks DPAD UP
        # twitch command = !DLEFT
        await self.sendCommand("click DUP")
    @commands.command()
    async def CAPTURE(self, ctx: commands.Context):
        # Captures a screenshot
        # twitch command = !capture
        await self.sendCommand("click CAPTURE")
    @commands.command()
    async def PLUS(self, ctx: commands.Context):
        # Clicks Plus
        # twitch command = !PLUS
        await self.sendCommand("click PLUS")
    @commands.command()
    async def MINUS(self, ctx: commands.Context):
        # Clicks MINUS
        # twitch command = !MINUS
        await self.sendCommand("click MINUS")


    #Left Joystick
    @commands.command()
    async def up(self, ctx: commands.Context):
        # Presses UP on the left joystick
        # twitch command = !DLEFT
        await self.sendCommand("setStick LEFT 0x0000 0x7FFF")
        time.sleep(1)
        await self.sendCommand("setStick LEFT 0x0000 0x0000")
    @commands.command()
    async def left(self, ctx: commands.Context):
        # Presses LEFT on the left joystick
        # twitch command = !left
        await self.sendCommand("setStick LEFT -0x8000 0x0000")
        time.sleep(1)
        await self.sendCommand("setStick LEFT 0x0000 0x0000")
    @commands.command()
    async def down(self, ctx: commands.Context):
        # Presses DOWN on the left joystick
        # twitch command = !down
        await self.sendCommand("setStick LEFT 0x0000 -0x8000")
        time.sleep(1)
        await self.sendCommand("setStick LEFT 0x0000 0x0000")
    @commands.command()
    async def right(self, ctx: commands.Context):
        # Presses RIGHT on the left joystick
        # twitch command = !right
        await self.sendCommand("setStick LEFT 0x7FFF 0x0000")
        time.sleep(1)
        await self.sendCommand("setStick LEFT 0x0000 0x0000")

#lowercase right joycon buttons
    @commands.command()
    async def a(self, ctx: commands.Context):
        # Clicks the A Button
        # twitch command = !a
        await self.sendCommand("click A")

    @commands.command()
    async def b(self, ctx: commands.Context):
            # Clicks the B Button
            # twitch command = !b
        await self.sendCommand("click B")

    @commands.command()
    async def x(self, ctx: commands.Context):
        # Clicks the X Button
        # twitch command = !x
        await self.sendCommand("click X")

    @commands.command()
    async def y(self, ctx: commands.Context):
        # Clicks the Y Button
        # twitch command = !y
        await self.sendCommand("click Y")

    @commands.command()
    async def zr(self, ctx: commands.Context):
        # Clicks the ZR Button
        # twitch command = !zr
        await self.sendCommand("click ZR")

    @commands.command()
    async def capture(self, ctx: commands.Context):
        # Captures a screenshot
        # twitch command = !capture
        await self.sendCommand("click CAPTURE")
    @commands.command()
    async def plus(self, ctx: commands.Context):
        # Clicks Plus
        # twitch command = !plus
        await self.sendCommand("click PLUS")
    @commands.command()
    async def minus(self, ctx: commands.Context):
        # Clicks MINUS
        # twitch command = !minus
        await self.sendCommand("click MINUS")

    @commands.command()
    async def zl(self, ctx: commands.Context):
        # Clicks the ZL Button
        # twitch command = !zl
        await self.sendCommand("click ZL")

    @commands.command()
    async def dleft(self, ctx: commands.Context):
        # Clicks the DPAD LEDT
        # twitch command = !dleft
        await self.sendCommand("click DLEFT")
    @commands.command()
    async def dright(self, ctx: commands.Context):
        # Clicks the DPAD RIGHT
        # twitch command = !dright
        await self.sendCommand("click DRIGHT")
    @commands.command()
    async def ddown(self, ctx: commands.Context):
        # Clicks DPAD DOWN
        # twitch command = !ddown
        await self.sendCommand("click DDOWN")
    @commands.command()
    async def dup(self, ctx: commands.Context):
        # Clicks DPAD UP
        # twitch command = !dup
        await self.sendCommand("click DUP")
bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.