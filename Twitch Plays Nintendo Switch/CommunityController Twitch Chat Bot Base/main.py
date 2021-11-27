from twitchio.ext import commands

import socket
import time
from dotenv import dotenv_values
from twitchio.ext.commands import errors
from twitchio.ext.commands.errors import CommandNotFound


class Bot(commands.Bot):
    config = dotenv_values(".env")

    def __init__(self):
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # Make sure token is non-empty
        if 'OAUTH_TOKEN' not in self.config.keys():
            raise ValueError('OAUTH_TOKEN is not set')
        if 'CHANNEL_NAME' not in self.config.keys():
            raise ValueError('CHANNEL_NAME is not set')

        token = self.config.get("OAUTH_TOKEN")
        channel = self.config.get("CHANNEL_NAME")

        super().__init__(token, prefix="!", initial_channels=[channel])

    async def sendCommand(self, content):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("localhost", 6000))
        print('Twitch pressed a button!', content)

        content += '\r\n'  # important for the parser on the switch side
        s.sendall(content.encode())

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        print(f'Logged in as | {self.nick}')
        print('Connected to Nintendo Switch')

    # uppercase right joycon Buttons
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

    # Left Joystick
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

    # lowercase right joycon buttons
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

    async def run_command(self, command: str, ctx: commands.Context):
        # Programmatically execute Twitch commands
        #
        # command: twitch command string
        # ctx: command context
        return await self.commands[command](ctx)

    async def command_parser(self, message):
        # message: the message object passed from the event_message event
        #
        # We want to allow command chaining. So, we want to parse valid
        # commands separated by spaces.
        message_content = message.content
        message_parts = message_content.split("!")

        if message_content[0] != "!": # If the message doesn't start with !, ignore it
            return

        message_context = await self.get_context(message)

        if len(message_parts) > 2: # If there are more than 2 parts, we have a command chain
            for part in message_parts:
                if len(part) > 0:
                    if part in self.commands:
                        await self.run_command(part, message_context)
                        time.sleep(1)
        else: # If there are only 2 parts, we have a single command ({before}!{after} where {after} 
            # is the command. {before} is always empty because we enforce a first character of !)
            if message_parts[1] in self.commands:
                await self.run_command(message_parts[1], message_context)
        
    async def event_command_error(self, context: commands.Context, error):
        # Handle command errors
        # Set DEBUG in .env to True to see errors
        #
        # context: the error context
        # error: the error object
        if "DEBUG" in self.config and self.config["DEBUG"] == "True":
            print(error)
        return

    async def event_message(self, message):
        # Handles messages sent in the chat
        # message: the message object passed from the event_message event

        # If the bot is the sender, ignore it
        if message.echo:
            return
        await self.command_parser(message)

bot = Bot()
bot.run()
# bot.run() is blocking and will stop execution of any below code here until stopped or closed.
