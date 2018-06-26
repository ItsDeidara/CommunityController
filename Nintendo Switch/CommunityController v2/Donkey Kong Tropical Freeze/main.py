#!/usr/bin/python3

import re
import socket
import sqlite3
import asyncore
import os
import json
from os.path import isfile
from time import sleep, time
from threading import Thread, Timer

#external libraries
from lib.switch_controller import *

TWITCH_HOST = "irc.chat.twitch.tv"
TWITCH_PORT = 6667

SERIAL_DEVICE = "COM5"
SERIAL_BAUD = 9600

MAX_COMMANDS_PER_MESSAGE = 8

CONFIG_FILE = "config.json"
VOTES_FILE  = "votes.json"
DATABASE_FILE = "data.db"

#game mode
GAME_MODE = MODE_SIDESCROLLER

#button shortcuts
JUMP_BUTTON = BUTTON_A

#last command timestamp
LAST_COMMAND = None

#keep-alive threshold in seconds
KEEP_ALIVE_DIFFERENTIAL = 60

#True = Anarchy mode
#False= Democracy mode
ANARCHY_MODE = False

#Democracy voting time in seconds
DEMOCRACY_VOTE_TIME = 15.0 #no longer needed

DEMOCRACY_MIN_INPUT = 5    #amount of votes needed to execute a command/sequence

DEMOCRACY_PAUSE_BUTTON = BUTTON_PLUS   #not being used currently

DEMOCRACY_PAUSE_ENABLED = False

DEMOCRACY_IS_IN_PAUSE = False

VOTE_YEA_COUNT = 0    #used to log the amount of vote yeas

VOTE_NAY_COUNT = 0    #used to log the amount of vote nays

VOTE_USERS = []

VOTE_CMDS  = {}

IRC_CLIENT = 0

HAS_MADE_ANNOUNCEMENT = False

#1 = username
#2 = command
#3 = channel
#4 = message
CHAT_EXP = re.compile(r"^:([\w\W]{0,}?)![\w\W]{0,}?@[\w\W]{0,}?\.tmi\.twitch\.tv\s([A-Z]{0,}?)\s#([\w\W]{0,}?)\s:([\w\W]{0,}?)$")

CURRENT_THREAD = None

def prevent_timeout():
    Timer(KEEP_ALIVE_DIFFERENTIAL, keep_alive).start()

def keep_alive():
    global LAST_COMMAND
    global CURRENT_THREAD
    #compute difference in current timestamp and last command
    if isinstance(CURRENT_THREAD, Thread) and not CURRENT_THREAD.is_alive() and isinstance(LAST_COMMAND, int) and (timestamp() - LAST_COMMAND) >= KEEP_ALIVE_DIFFERENTIAL:
        print('CommunityController used an awakening!')
        controller.push_dpad(DPAD_LEFT)
    prevent_timeout()

def timestamp():
    return int(time.time())

def write_votes() -> None:
    global ANARCHY_MODE
    global VOTE_YEA_COUNT
    global VOTE_NAY_COUNT
    global VOTE_USERS
    global VOTE_CMDS
    global VOTES_FILE
    global DEMOCRACY_IS_IN_PAUSE
    votesDict = {"AnarchyMode" : ANARCHY_MODE, "VoteYeaCount" : VOTE_YEA_COUNT, "VoteNayCount" : VOTE_NAY_COUNT, "VotesUsers" : VOTE_USERS, "VotesCmds" : VOTE_CMDS, "DemocracyIsInPause" : DEMOCRACY_IS_IN_PAUSE}
    json.dump(votesDict, open(VOTES_FILE, "w"))

def load_votes() -> None:
    global ANARCHY_MODE
    global VOTE_YEA_COUNT
    global VOTE_NAY_COUNT
    global VOTE_USERS
    global VOTE_CMDS
    global VOTES_FILE
    global DEMOCRACY_IS_IN_PAUSE
    if not isfile(VOTES_FILE):
        write_votes()
    votesDict      = json.load(open(VOTES_FILE, "r"))
    ANARCHY_MODE   = votesDict["AnarchyMode"]
    VOTE_YEA_COUNT = votesDict["VoteYeaCount"]
    VOTE_NAY_COUNT = votesDict["VoteNayCount"]
    VOTE_USERS     = votesDict["VotesUsers"]
    VOTE_CMDS      = votesDict["VotesCmds"]
    DEMOCRACY_IS_IN_PAUSE = votesDict["DemocracyIsInPause"]

def create_database() -> None:
    """
    A, B, X, Y, L, R, ZL, ZR, up, down, left, right, left joystick, right joystick, select
    """
    with sqlite3.connect(DATABASE_FILE) as db:
        c = db.cursor()
        c.execute("CREATE TABLE IF NOT EXISTS buttons (name TEXT PRIMARY KEY, presses INT)")
        for button_name in [
            "A", "B", "X", "Y",  #ABXY
            "L", "R", "ZL", "ZR",  #bumpers and triggers
            "LCLICK", "RCLICK",  #L3 and R3
            "UP", "DOWN", "LEFT", "RIGHT",  #D-Pad
            "LX MIN", "LX MAX", "LY MIN", "LY MAX",  #left analog stick
            "RX MIN", "RX MAX", "RY MIN", "RY MAX",  #right analog stick
            "START", "SELECT",  #start and select
            "CAPTURE"  #capture button
        ]:
            c.execute("INSERT INTO buttons (name, presses) VALUES ('" + button_name + "', 0)")
        db.commit()

def increment_button_count(name: str) -> None:
    with sqlite3.connect(DATABASE_FILE) as db:
        c = db.cursor()
        c.execute("SELECT * FROM buttons WHERE name=:name", {"name": name})
        button = c.fetchone()
        c.execute("UPDATE buttons SET presses=:presses WHERE name=:name", {"presses": button[1] + 1, "name": name})
        db.commit()

def send_message(msg: str) -> None:
    global IRC_CLIENT
    IRC_CLIENT.send(bytes("PRIVMSG #" + IRC_CLIENT.channel + " :" + msg + "\r\n", "utf8"))

def update_message_mode() -> None:
    load_votes()
    global ANARCHY_MODE
    currMode = "Democracy"
    nextMode = "Anarchy"
    if ANARCHY_MODE:
        currMode = "Anarchy"
        nextMode = "Democracy"
    send_message("We're currently in " + currMode + " Mode. To switch to " + nextMode + " Mode, use VoteYea. If you want to stay, use VoteNay.")

#Switches between Anarchy/Democracy mode
def switch_modes() -> None:
    global ANARCHY_MODE
    global VOTE_YEA_COUNT
    global VOTE_NAY_COUNT
    global VOTE_USERS
    if ANARCHY_MODE:
        ANARCHY_MODE = False
        send_message("Switching to Democracy Mode!")
        print("Switching to Democracy Mode...")
    else:
        ANARCHY_MODE = True
        send_message("Switching to Anarchy Mode!")
        print("Switching to Anarchy Mode...")
    send_message("Should we change modes? If yes use VoteYea. Else, use VoteNay.")
    VOTE_YEA_COUNT = 0
    VOTE_NAY_COUNT = 0
    VOTE_USERS = []
    write_votes()

def use_button(name: str):
    print("use_button(" + str(name) + ")")
    # A, B, X, and Y
    if name in ["A", "B", "X", "Y"]:
        increment_button_count(name)
        if name == "A":
            controller.push_button(BUTTON_A)
        elif name == "B":
            controller.push_button(BUTTON_B)
        elif name == "X":
            controller.push_button(BUTTON_X)
        elif name == "Y":
            controller.push_button(BUTTON_Y)
    # LB, LT, RB, and RT
    elif name in ["L", "LB"]:
        increment_button_count("L")
        controller.push_button(BUTTON_L)
    elif name in ["R", "RB"]:
        increment_button_count("R")
        controller.push_button(BUTTON_R)
    elif name in ["LT", "ZL"]:
        increment_button_count("ZL")
        controller.push_button(BUTTON_ZL)
    elif name in ["RT", "ZR"]:
        increment_button_count("ZR")
        controller.push_button(BUTTON_ZR)
    #L3 and R3
    elif name in ["LCLICK", "L3"]:
        increment_button_count("LCLICK")
        controller.push_button(BUTTON_LCLICK)
    elif name in ["RCLICK", "R3"]:
        increment_button_count("RCLICK")
        controller.push_button(BUTTON_RCLICK)
    # start and select
    elif name in ["START", "SELECT"]:
        if name == "STARTISDISABLEDINAVERYFANCYWAY":
           increment_button_count("START")
           controller.push_button(BUTTON_PLUS)
        if name == "SELECTWASNEVERENABLED":
            increment_button_count("SELECT")
            controller.push_button(BUTTON_MINUS)
    elif name in ["UP", "DOWN", "LEFT", "RIGHT"]:  # D-Pad
        if name == "UP":
            increment_button_count("UP")
            controller.push_dpad(DPAD_UP)
        elif name == "DOWN":
            increment_button_count("DOWN")
            controller.push_dpad(DPAD_DOWN)
        elif name == "LEFT":
            increment_button_count("LEFT")
            controller.push_dpad(DPAD_LEFT)
        elif name == "RIGHT":
            increment_button_count("RIGHT")
            controller.push_dpad(DPAD_RIGHT)
    elif name in ["MOVE_FORWARD", "MOVE_BACK", "MOVE_LEFT", "MOVE_RIGHT"]:  # left stick
        if name == "MOVE_FORWARD":
            increment_button_count("LY MIN")
            controller.move_forward(GAME_MODE)
            sleep(0.5)
            controller.release_left_stick()
        elif name == "MOVE_BACK":
            increment_button_count("LY MAX")
            controller.move_backward(GAME_MODE)
            sleep(0.5)
            controller.release_left_stick()
        elif name == "MOVE_LEFT":
            increment_button_count("LX MIN")
            controller.move_left()
            sleep(0.5)
            controller.release_left_stick()
        elif name == "MOVE_RIGHT":
            increment_button_count("LX MAX")
            controller.move_right()
            sleep(0.5)
            controller.release_left_stick()
    elif name in ["LOOK_UP", "LOOK_DOWN", "LOOK_LEFT", "LOOK_RIGHT"]:  # right stick
        if name == "LOOK_UP":
            increment_button_count("RY MIN")
            controller.look_up()
            sleep(0.5)
            controller.release_right_stick()
        elif name == "LOOK_DOWN":
            increment_button_count("RY MAX")
            controller.look_down()
            sleep(0.5)
            controller.release_right_stick()
        elif name == "LOOK_LEFT":
            increment_button_count("RX MIN")
            controller.look_left()
            sleep(0.5)
            controller.release_right_stick()
        elif name == "LOOK_RIGHT":
            increment_button_count("RX MAX")
            controller.look_right()
            sleep(0.5)
            controller.release_right_stick()
    #game sensitive
    elif name == "JUMP":
        controller.move_forward(GAME_MODE)
        controller.hold_buttons(JUMP_BUTTON)
        sleep(1.0)
        controller.release_buttons(JUMP_BUTTON)
        controller.release_left_stick()
        command_executed = True
    elif name == "JUMP":
        controller.move_forward(GAME_MODE)
        controller.hold_buttons(JUMP_BUTTON)
        sleep(1.0)
        controller.release_buttons(JUMP_BUTTON)
        controller.release_left_stick()
        command_executed = True
    elif name == "JUMP_BACK":
        controller.move_backward(GAME_MODE)
        controller.hold_buttons(JUMP_BUTTON)
        sleep(1.0)
        controller.release_buttons(JUMP_BUTTON)
        controller.release_left_stick()
        command_executed = True
        #commands for holding down each face button for 1 second
    elif name == "HOLD_DOWN":
        controller.hold_dpad(DPAD_DOWN)
        sleep(1.0)
        controller.release_dpad()
    elif name == "ADJUST_BACKWARD":
        increment_button_count("LY MAX")
        controller.move_backward(GAME_MODE)
        sleep(0.3)
        controller.release_left_stick()
    elif name == "ADJUST_BACK":
        increment_button_count("LY MAX")
        controller.move_backward(GAME_MODE)
        sleep(0.3)
        controller.release_left_stick()
    elif name == "HOLD_UP":
        controller.hold_dpad(DPAD_UP)
        sleep(1.0)
        controller.release_dpad()
    elif name == "ADJUST_FORWARD":
        increment_button_count("LY MIN")
        controller.move_forward(GAME_MODE)
        sleep(0.3)
        controller.release_left_stick()
    elif name == "ADJUST_DOWN":
        increment_button_count("DOWN")
        controller.hold_dpad(DPAD_DOWN)
        sleep(0.3)
        controller.release_dpad()
    elif name == "HOLD_LEFT":
        controller.hold_dpad(DPAD_LEFT)
        sleep(1.0)
        controller.release_dpad()
    elif name == "ADJUST_LEFT":
        increment_button_count("LX MIN")
        controller.move_left()
        sleep(0.3)
        controller.release_left_stick()
    elif name == "HOLD_RIGHT":
        controller.hold_dpad(DPAD_RIGHT)
        sleep(1.0)
        controller.release_dpad()
    elif name == "ADJUST_RIGHT":
        increment_button_count("LX MAX")
        controller.move_right()
        sleep(0.3)
        controller.release_left_stick()
    elif name == "HOLD_LB":
        controller.hold_buttons(BUTTON_L)
        sleep(1.0)
        controller.release_buttons(BUTTON_L)
    elif name == "HOLD_RB":
        controller.hold_buttons(BUTTON_R)
        sleep(1.0)
        controller.release_buttons(BUTTON_R)
    elif name == "HOLD_ZL":
        controller.hold_buttons(BUTTON_ZL)
        sleep(1.0)
        controller.release_buttons(BUTTON_ZL)
    elif name == "HOLD_ZR":
        controller.hold_buttons(BUTTON_ZR)
        sleep(1.0)
        controller.release_buttons(BUTTON_ZR)
    elif name == "HOLD_A":
        controller.hold_buttons(BUTTON_A)
        sleep(1.0)
        controller.release_buttons(BUTTON_A)    
    elif name == "HOLD_B":
        controller.hold_buttons(BUTTON_B)
        sleep(1.0)
        controller.release_buttons(BUTTON_B)
    elif name == "HOLD_X":
        controller.hold_buttons(BUTTON_X)
        sleep(1.0)
        controller.release_buttons(BUTTON_X)
    elif name == "HOLD_Y":
        controller.hold_buttons(BUTTON_Y)
        sleep(1.0)
        controller.release_buttons(BUTTON_Y)
        #game specific commands
    elif name == "KONG_POW":
        increment_button_count("L")
        controller.hold_buttons(BUTTON_L)
        controller.hold_buttons(BUTTON_R)
        sleep(1.0)
        controller.release_buttons(BUTTON_L)
        controller.release_buttons(BUTTON_R)
        command_executed = True
    elif name == "POW":
        increment_button_count("L")
        controller.hold_buttons(BUTTON_L)
        controller.hold_buttons(BUTTON_R)
        sleep(1.0)
        controller.release_buttons(BUTTON_L)
        controller.release_buttons(BUTTON_R)
        command_executed = True
    elif name == "KP":
        increment_button_count("L")
        controller.hold_buttons(BUTTON_L)
        controller.hold_buttons(BUTTON_R)
        sleep(1.0)
        controller.release_buttons(BUTTON_L)
        controller.release_buttons(BUTTON_R)
        command_executed = True
    elif name == "GRAB":
        increment_button_count("ZL")
        controller.push_button(BUTTON_ZL)
        sleep(0.5)
        command_executed = True
    elif name == "THROW":
        increment_button_count("ZL")
        controller.push_button(BUTTON_ZL)
        sleep(0.5)
        command_executed = True
    elif name == "PLUCK":
        increment_button_count("ZL")
        controller.push_button(BUTTON_ZL)
        sleep(0.5)
        command_executed = True
    elif name == "COMBINE":
        increment_button_count("ZL")
        controller.push_button(BUTTON_ZL)
        sleep(0.5)
        command_executed = True
    elif name == "DISMOUNT":
        increment_button_count("ZL")
        controller.push_button(BUTTON_ZL)
        sleep(0.5)
        command_executed = True
    elif name == "GROUND_POUND":
        increment_button_count("X")
        controller.push_button(BUTTON_X)
        sleep(0.5)
        command_executed = True
    elif name == "ROLL_ATTACK":
        increment_button_count("X")
        controller.push_button(BUTTON_X)
        sleep(0.5)
        command_executed = True
    elif name == "ATTACK":
        increment_button_count("X")
        controller.push_button(BUTTON_X)
        sleep(0.5)
        command_executed = True
    elif name == "CORKSCREW":
        increment_button_count("X")
        controller.push_button(BUTTON_X)
        sleep(0.5)
        command_executed = True
    elif name == "SWIM":
        increment_button_count("A")
        controller.push_button(BUTTON_A)
        sleep(0.5)
        command_executed = True
    elif name == "MOVE_UP":
        controller.hold_dpad(DPAD_UP)
        sleep(1.0)
        controller.release_dpad()
    elif name == "KEEP_HOLD_ZL":
        controller.hold_buttons(BUTTON_ZL)
        command_executed = True
    elif name == "RELEASE_ZL":
        controller.release_buttons(BUTTON_ZL)
        command_executed = True
    elif name == "MOVE_DOWN":
        controller.hold_dpad(DPAD_DOWN)
        sleep(1.0)
        controller.release_dpad()
    elif name == "CONNECT":  #connect the controller to the console
        controller.connect()
    # Custom commands
    if single[0:7] == "CUSTOM(" and single.find(")") > 7:  # single == "CUSTOM(smthg)"
        tmpr = single[7:single.find(")")].strip().replace("_", " ")  # tmpr == "smthg"

        combine = []

        if tmpr[0:1] == "[" and tmpr.find("]") > 0:  # tmpr == "a[b, ...]c"
            combine = tmpr[tmpr.find("[") + 1:tmpr.find("]")].split(";")  # combine == ["b", "..."]

            tmpr = tmpr[tmpr.find("]") + 1:]  # tmpr == "c"
        elif tmpr.find(";") > -1:  # tmpr == "x,y"
            combine = [tmpr[0:tmpr.find(";")]]  # combine == ["x"]
        else:  # tmpr = "x"
            combine = [tmpr]  # combine == ["x"]

            tmpr = ""

        tmpr = tmpr[tmpr.find(";") + 1:].strip()

        # At this point...
        # combine is an array of commands
        # tmpr is a string supposedly containing the duration of the custom command

        duration = 0.02
        try:
            duration = float(tmpr)

            if duration > 0 and duration <= 1:  # the duration has to be between 0 and 1 second
                duration = duration
            else:
                duration = 0.02

        except:
            0

        cmd = []  # array of the commands to execute, again...

        for i in combine:
            i = i.strip().replace(" ", "_")

            if i in ["PLUS", "START"]:
                increment_button_count("START")
                cmd.append(BUTTON_PLUS)
            elif i in ["MINUS", "SELECT"]:
                increment_button_count("SELECT")
                cmd.append(BUTTON_MINUS)

            elif i == "A":
                increment_button_count("A")
                cmd.append(BUTTON_A)
            elif i == "B":
                increment_button_count("B")
                cmd.append(BUTTON_B)
            elif i == "X":
                increment_button_count("X")
                cmd.append(BUTTON_X)
            elif i == "Y":
                increment_button_count("Y")
                cmd.append(BUTTON_Y)

            elif i in ["UP", "DUP", "D_UP"]:
                increment_button_count("UP")
                cmd.append(DPAD_UP)
            elif i in ["DOWN", "DDOWN", "D_DOWN"]:
                increment_button_count("DOWN")
                cmd.append(DPAD_DOWN)
            elif i in ["LEFT", "DLEFT", "D_LEFT"]:
                increment_button_count("LEFT")
                cmd.append(DPAD_LEFT)
            elif i in ["RIGHT", "DRIGHT", "D_RIGHT"]:
                increment_button_count("RIGHT")
                cmd.append(DPAD_RIGHT)

            elif i in ["L", "LB"]:
                increment_button_count("L")
                cmd.append(BUTTON_L)
            elif i in ["R", "RB"]:
                increment_button_count("R")
                cmd.append(BUTTON_R)
            elif i in ["ZL", "LT"]:
                increment_button_count("ZL")
                cmd.append(BUTTON_ZL)
            elif i in ["ZR", "RT"]:
                increment_button_count("ZR")
                cmd.append(BUTTON_ZR)

            elif i in ["LCLICK", "L3"]:
                increment_button_count("LCLICK")
                cmd.append(BUTTON_LCLICK)
            elif i in ["RCLICK", "R3"]:
                increment_button_count("RCLICK")
                cmd.append(BUTTON_RCLICK)

            elif i in ["LUP", "L_UP"]:
                increment_button_count("LY MIN")
                cmd.append("L_UP")
            elif i in ["LDOWN", "L_DOWN"]:
                increment_button_count("LY MAX")
                cmd.append("L_DOWN")
            elif i in ["LLEFT", "L_LEFT"]:
                increment_button_count("LX MIN")
                cmd.append("L_LEFT")
            elif i in ["LRIGHT", "L_RIGHT"]:
                increment_button_count("LX MAX")
                cmd.append("L_RIGHT")

            elif i in ["RUP", "R_UP"]:
                increment_button_count("RY MIN")
                cmd.append("R_UP")
            elif i in ["RDOWN", "R_DOWN"]:
                increment_button_count("RY MAX")
                cmd.append("R_DOWN")
            elif i in ["RLEFT", "R_LEFT"]:
                increment_button_count("RX MIN")
                cmd.append("R_LEFT")
            elif i in ["RRIGHT", "R_RIGHT"]:
                increment_button_count("RX MAX")
                cmd.append("R_RIGHT")

            elif i == "WAIT":
                cmd.append("WAIT")

        for i in cmd:  # buttons to hold
            if i in [BUTTON_PLUS, BUTTON_MINUS, BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y, BUTTON_L, BUTTON_R, BUTTON_ZL,
                     BUTTON_ZR, BUTTON_LCLICK, BUTTON_RCLICK]:
                controller.hold_buttons(i)
                command_executed = True
            elif i in [DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT]:
                controller.hold_dpad(i)
                command_executed = True
            elif i == "L_UP":
                controller.move_forward(GAME_MODE)
                command_executed = True
            elif i == "L_DOWN":
                controller.move_backward(GAME_MODE)
                command_executed = True
            elif i == "L_LEFT":
                controller.move_left()
                command_executed = True
            elif i == "L_RIGHT":
                controller.move_right()
                command_executed = True
            elif i == "R_UP":
                controller.look_up()
                command_executed = True
            elif i == "R_DOWN":
                controller.look_down()
                command_executed = True
            elif i == "R_LEFT":
                controller.look_left()
                command_executed = True
            elif i == "R_RIGHT":
                controller.look_right()
                command_executed = True
            elif i == "WAIT":
                command_executed = True

        if command_executed:  # sleep if any command has been executed
            sleep(duration)

        for i in cmd:  # release the buttons
            if i in [BUTTON_PLUS, BUTTON_MINUS, BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y, BUTTON_L, BUTTON_R, BUTTON_ZL,
                     BUTTON_ZR, BUTTON_LCLICK, BUTTON_RCLICK]:
                controller.release_buttons(i)
            elif i in [DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT]:
                controller.release_dpad()
            elif i in ["L_UP", "L_DOWN", "L_LEFT", "L_RIGHT"]:
                controller.release_left_stick()
            elif i in ["R_UP", "R_DOWN", "R_LEFT", "R_RIGHT"]:
                controller.release_right_stick()

    else:
        return False
    return True

def execute_command(message: str, data: str) -> None:
    #db = sqlite3.connect("data.db")
    print("Received message!")
    load_votes()
    global HAS_MADE_ANNOUNCEMENT
    if not HAS_MADE_ANNOUNCEMENT:
        update_message_mode()
        HAS_MADE_ANNOUNCEMENT = True
    global ANARCHY_MODE
    global MAX_COMMANDS_PER_MESSAGE
    mod = data.find('mod=')
    subscriber = data.find('subscriber=')
    if mod != -1 and subscriber != -1:
        mod = bool(int(data[mod+4]))
        subscriber = bool(int(data[subscriber+11]))
        if mod:
            MAX_COMMANDS_PER_MESSAGE = 10
            print("Mod " + str(MAX_COMMANDS_PER_MESSAGE))
        elif subscriber:
            MAX_COMMANDS_PER_MESSAGE = 8
            print("Sub "+ str(MAX_COMMANDS_PER_MESSAGE))
        else:
            MAX_COMMANDS_PER_MESSAGE = 8
            print("Non-Sub " + str(MAX_COMMANDS_PER_MESSAGE))
    
    global VOTE_YEA_COUNT
    global VOTE_NAY_COUNT
    global VOTE_USERS
    if "PRIVMSG" in data:
        userId = data[0:data.find("PRIVMSG")]
        if "cheuble" in data:
            print("userId: " + userId)
            print("VoteNay count * 2", VOTE_NAY_COUNT * 2)
            print("VoteYea count", VOTE_YEA_COUNT)
            print("Message: " + message)
        if ("VOTEYEA" in message.upper()) and not ("Zuccerbot3000" in data):# and not (userId in VOTE_USERS): #We don't want the bot to parse itself.
            VOTE_YEA_COUNT += 1
            print("Voted Yea")
            write_votes()
        if ("VOTENAY" in message.upper()) and not ("Zuccerbot3000" in data):# and not (userId in VOTE_USERS):
            VOTE_NAY_COUNT += 1
            print("Voted Nay")
            write_votes()
        if VOTE_YEA_COUNT >= 5 and VOTE_YEA_COUNT >= 2 * VOTE_NAY_COUNT:
            switch_modes()
        elif ("VOTEYEA" in message.upper() or "VoteNay" in message.upper()) and not ("Zuccerbot3000" in data):# and not (userId in VOTE_USERS):
            currMode = "Democracy"
            nextMode = "Anarchy"
            if ANARCHY_MODE:
                currMode = "Anarchy"
                nextMode = "Democracy"
            if VOTE_YEA_COUNT >= 5:
                send_message("Only " + str(VOTE_NAY_COUNT * 2 - VOTE_YEA_COUNT) + " more VoteYea to switch from " + currMode + " Mode to " + nextMode + " Mode.")
                print("Only " + str(VOTE_NAY_COUNT * 2 - VOTE_YEA_COUNT) + " more VoteYea to switch from " + currMode + " Mode to " + nextMode + " Mode.")
            else:
                send_message("We currently have " + str(VOTE_YEA_COUNT) + " VoteYea and " + str(VOTE_NAY_COUNT) + " VoteNay to switch from " + currMode + " Mode to " + nextMode + " Mode.")
                print("We currently have " + str(VOTE_YEA_COUNT) + " VoteYea and " + str(VOTE_NAY_COUNT) + " VoteNay to switch from " + currMode + " Mode to " + nextMode + " Mode.")
            VOTE_USERS.append(userId)

    message = message.strip().upper()
    if message[-1] == ",": #Removes the comma at the end of the message if there's one
        message = message[:-1]
    split_message = message.split(",")
    #print("Commands:", split_message)
    command_executed = False
    if len(split_message) <= MAX_COMMANDS_PER_MESSAGE:
        for single in split_message:
            single = single.strip().replace(" ", "_")
            if ANARCHY_MODE:
                #print("Anarchy mode: pressing button.")
                simultaneous_commands = single.split("_&_")
                threadsArr = []
                for cmd in simultaneous_commands:
                    threadsArr.append(Thread(target=use_button, args=[cmd]))
                    threadsArr[-1].start()
                for t in threadsArr:
                    t.join()
            else:
                #print("Democracy mode: voting")
                global VOTE_CMDS
                global DEMOCRACY_MIN_INPUT
                if single in VOTE_CMDS:
                    VOTE_CMDS[single][0] += 1
                    if split_message.count(single) > VOTE_CMDS[single][1]:
                        VOTE_CMDS[single][1] += 1
                else:
                    VOTE_CMDS[single] = [1, 1]
                if VOTE_CMDS[single][0] >= DEMOCRACY_MIN_INPUT and VOTE_CMDS[single][1] >= 1:
                    global DEMOCRACY_IS_IN_PAUSE
                    global DEMOCRACY_PAUSE_BUTTON
                    global DEMOCRACY_PAUSE_ENABLED
                    if DEMOCRACY_IS_IN_PAUSE and DEMOCRACY_PAUSE_ENABLED:
                        controller.push_button(DEMOCRACY_PAUSE_BUTTON)
                        sleep(1.0)
                        DEMOCRACY_IS_IN_PAUSE = False
                    simultaneous_commands = single.split("_&_")
                    threadsArr = []
                    for cmd in simultaneous_commands:
                        threadsArr.append(Thread(target=use_button, args=[cmd]))
                        threadsArr[-1].start()
                    for t in threadsArr:
                        t.join()
                    if not DEMOCRACY_IS_IN_PAUSE and DEMOCRACY_PAUSE_ENABLED:
                        controller.push_button(DEMOCRACY_PAUSE_BUTTON)
                        DEMOCRACY_IS_IN_PAUSE = True
                    VOTE_CMDS[single][0] -= DEMOCRACY_MIN_INPUT
                    VOTE_CMDS[single][1] -= 1
                if VOTE_CMDS[single][0] >= DEMOCRACY_MIN_INPUT and VOTE_CMDS[single][1] == 0:
                    VOTE_CMDS[single][1] = 1
                write_votes()

    if command_executed:
        global LAST_COMMAND
        LAST_COMMAND = timestamp()

class TwitchIRC(asyncore.dispatcher):
    username = None
    password = None
    channel = None

    authenticated = False

    def __init__(self, username: str, password: str, channel: str) -> None:
        assert username is not None, "No username specified!"
        assert password is not None, "No password specified!"
        assert channel is not None, "No channel specified!"

        self.username = username
        self.password = password
        self.channel = channel

        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((TWITCH_HOST, TWITCH_PORT))
        self.buffer = bytes("PASS %s\r\nNICK %s\r\n" % (password, username), "utf8")

        prevent_timeout()
        global DEMOCRACY_IS_IN_PAUSE
        global ANARCHY_MODE
        global DEMOCRACY_PAUSE_BUTTON
        global DEMOCRACY_PAUSE_ENABLED
        if DEMOCRACY_PAUSE_ENABLED and not DEMOCRACY_IS_IN_PAUSE and not ANARCHY_MODE:
            controller.push_button(DEMOCRACY_PAUSE_BUTTON)
            sleep(0.6)
        write_votes()

    def handle_connect(self):
        pass

    def handle_close(self):
        self.close()

    def handle_read(self):
        data = self.recv(2048).decode("utf8", errors="ignore").rstrip()
        if "Welcome, GLHF!" in data and not self.authenticated:
            self.authenticated = True
            self.buffer += bytes("JOIN #%s\r\n" % (self.channel), "utf8")
        elif data == "PING :tmi.twitch.tv":
            print("PING!")
            self.buffer += b"PONG :tmi.twitch.tv\r\n"
            print("PONG!")
        elif "%s.tmi.twitch.tv" % (self.channel) not in data or self.username in data:  #chat messages here
            global CURRENT_THREAD
            matches = CHAT_EXP.match(data)
            if matches:
                (username, command, channel, message) = matches.groups()
                print(username + " --> " + message)
                if CURRENT_THREAD is None or not CURRENT_THREAD.is_alive():
                    CURRENT_THREAD = Thread(target=execute_command, args=[message, data])
                    CURRENT_THREAD.start()
                    
    def readable(self):
        return True

    def writable(self):
        return (len(self.buffer) > 0)

    def handle_write(self):
        sent = self.send(self.buffer)
        self.buffer = self.buffer[sent:]

if __name__ == "__main__":
    #load or create config
    if isfile(CONFIG_FILE):
        cfg = json.load(open(CONFIG_FILE, "r"))
    else:
        cfg = {"username": "", "password": ""}
        json.dump(cfg, open(CONFIG_FILE, "w"))
        print("Sample config created!")
        raise Exception("Please edit the configuration file to reflect your Twitch API settings")

    #check if database exists
    if not isfile(DATABASE_FILE):
        create_database()
        print("Database created!")
    load_votes()
    with Controller() as controller:
        try:
            print("https://www.twitch.tv/" + cfg["username"])
            IRC_CLIENT = TwitchIRC(cfg["username"], cfg["password"], "communitycontroller")
        except KeyboardInterrupt:
            update_message_mode()
            controller.reset().wait()
            exit(0)
        asyncore.loop()
