# What even is this?

This is the start of the new and updated source code for the CommunityController Project! From this point forward, I am ditching the old arduino dependency, and moving towards using [sysBotBase](https://github.com/olliz0r/sys-botbase)

## What can I do with this?

This version of the script is the base of the project moving forward, Acting as a simple and basic script to allow Twitch chat to press each individual button on your joycons. Using both TwitchIO and sysBotBase

## Bot installation

**Note:** These instructions have only been tested on Python 3.8.x, but running it on most versions of Python 3 should work fine. In addition, it is assumed that your Python 3 and PIP 3 commands are `python3` and `pip3`, though they may differ depending on your environment.

First, install the requisite Python libraries through PIP:

    pip3 install twitchio
    pip3 install python-dotenv

Then, copy `.env.example` to `.env`. Edit `.env` and fill the fields as required:
- `OAUTH_TOKEN` is your Twitch OAuth token
- `CHANNEL_NAME` is your Twitch channel name
- `DEBUG` controls debug output and takes a value `True` or `False`
- `SWITCH_HOST` is your Switch IP address

Lastly, you should be able to start the bot by simply running `python3 main.py`. 

## Commands

See `main.py` for command examples. Examples:
- To press `A`, send the message `!A`
- To press `A` then `B`, send the message `!A!B`
