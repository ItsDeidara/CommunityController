#!/usr/bin/python3

import re
import socket
import sqlite3
import asyncore
import os
from os.path import isfile
from json import load, dump
from time import sleep, time
from threading import Thread, Timer

#external libraries
from lib.switch_controller import *

TWITCH_HOST = "irc.chat.twitch.tv"
TWITCH_PORT = 6667

SERIAL_DEVICE = "COM5"
SERIAL_BAUD = 9600

MAX_COMMANDS_PER_MESSAGE = 6

CONFIG_FILE = "config.json"
DATABASE_FILE = "data.db"

#game mode
GAME_MODE = MODE_SIDESCROLLER

#button shortcuts
JUMP_BUTTON = BUTTON_A

#last command timestamp
LAST_COMMAND = None

#keep-alive threshold in seconds
KEEP_ALIVE_DIFFERENTIAL = 60

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

def execute_command(message: str) -> None:
    #db = sqlite3.connect("data.db")
    message = message.strip().upper()
    split_message = message.split(",")
    command_executed = False
    if len(split_message) <= MAX_COMMANDS_PER_MESSAGE:
        for single in split_message:
            single = single.strip().replace(" ", "_")
            # A, B, X, and Y
            if single in ["A", "B", "X", "Y"]:
                increment_button_count(single)
                if single == "A":
                    controller.push_button(BUTTON_A)
                elif single == "B":
                    controller.push_button(BUTTON_B)
                elif single == "X":
                    controller.push_button(BUTTON_X)
                elif single == "Y":
                    controller.push_button(BUTTON_Y)
                command_executed = True
            # LB, LT, RB, and RT
            elif single in ["L", "LB"]:
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                command_executed = True
            elif single in ["R", "RB"]:
                increment_button_count("R")
                controller.push_button(BUTTON_R)
                command_executed = True
            elif single in ["LT", "ZL"]:
                increment_button_count("ZL")
                controller.push_button(BUTTON_ZL)
                command_executed = True
            elif single in ["RT", "ZR"]:
                increment_button_count("ZR")
                controller.push_button(BUTTON_ZR)
                command_executed = True
            #L3 and R3
            elif single in ["LCLICK", "L3"]:
                increment_button_count("LCLICK")
                controller.push_button(BUTTON_LCLICK)
                command_executed = True
            elif single in ["RCLICK", "R3"]:
                increment_button_count("RCLICK")
                controller.push_button(BUTTON_RCLICK)
                command_executed = True
            # start and select
            elif single in ["START", "SELECT"]:
                #if single == "START":
                #   increment_button_count("START")
                #   controller.push_button(BUTTON_PLUS)
                if single == "SELECT":
                    increment_button_count("SELECT")
                    controller.push_button(BUTTON_MINUS)
                command_executed = True
            elif single in ["UP", "DOWN", "LEFT", "RIGHT"]:  # D-Pad
                if single == "UP":
                    increment_button_count("UP")
                    controller.push_dpad(DPAD_UP)
                elif single == "DOWN":
                    increment_button_count("DOWN")
                    controller.push_dpad(DPAD_DOWN)
                elif single == "LEFT":
                    increment_button_count("LEFT")
                    controller.push_dpad(DPAD_LEFT)
                elif single == "RIGHT":
                    increment_button_count("RIGHT")
                    controller.push_dpad(DPAD_RIGHT)
                command_executed = True
            elif single in ["MOVE_FORWARD", "MOVE_BACK", "MOVE_LEFT", "MOVE_RIGHT"]:  # left stick
                if single == "MOVE_FORWARD":
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    sleep(0.5)
                    controller.release_left_stick()
                elif single == "MOVE_BACK":
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    sleep(0.5)
                    controller.release_left_stick()
                elif single == "MOVE_LEFT":
                    increment_button_count("LX MIN")
                    controller.move_left()
                    sleep(0.5)
                    controller.release_left_stick()
                elif single == "MOVE_RIGHT":
                    increment_button_count("LX MAX")
                    controller.move_right()
                    sleep(0.5)
                    controller.release_left_stick()
                command_executed = True
            elif single in ["LOOK_UP", "LOOK_DOWN", "LOOK_LEFT", "LOOK_RIGHT"]:  # right stick
                if single == "LOOK_UP":
                    increment_button_count("RY MIN")
                    controller.look_up()
                    sleep(0.5)
                    controller.release_right_stick()
                elif single == "LOOK_DOWN":
                    increment_button_count("RY MAX")
                    controller.look_down()
                    sleep(0.5)
                    controller.release_right_stick()
                elif single == "LOOK_LEFT":
                    increment_button_count("RX MIN")
                    controller.look_left()
                    sleep(0.5)
                    controller.release_right_stick()
                elif single == "LOOK_RIGHT":
                    increment_button_count("RX MAX")
                    controller.look_right()
                    sleep(0.5)
                    controller.release_right_stick()
                command_executed = True
            elif single == "CAPTURE":  #capture button
                increment_button_count("CAPTURE")
                controller.push_button(BUTTON_CAPTURE)
                command_executed = True
            #game sensitive
            elif single == "JUMP_FORWARD":
                controller.move_forward(GAME_MODE)
                controller.hold_buttons(JUMP_BUTTON)
                sleep(1.0)
                controller.release_buttons(JUMP_BUTTON)
                controller.release_left_stick()
                command_executed = True
            elif single == "JUMP":
                controller.move_forward(GAME_MODE)
                controller.hold_buttons(JUMP_BUTTON)
                sleep(1.0)
                controller.release_buttons(JUMP_BUTTON)
                controller.release_left_stick()
                command_executed = True
            elif single == "JUMP_BACK":
                controller.move_backward(GAME_MODE)
                controller.hold_buttons(JUMP_BUTTON)
                sleep(1.0)
                controller.release_buttons(JUMP_BUTTON)
                controller.release_left_stick()
                command_executed = True
            elif single == "UNFRIEND":
                controller.hold_buttons(BUTTON_Y)
                sleep(2.5)
                controller.release_buttons(BUTTON_Y)
                command_executed = True
            elif single == "SWALLOW":
                controller.push_dpad(DPAD_DOWN)
                command_executed = True
            elif single == "SUCK":
                controller.hold_buttons(BUTTON_B)
                sleep(1.0)
                controller.release_buttons(BUTTON_B)
                command_executed = True
            elif single == "SUCC":
                controller.hold_buttons(BUTTON_B)
                sleep(1.0)
                controller.release_buttons(BUTTON_B)
                command_executed = True
            elif single == "FLY":
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                sleep(0.1)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                command_executed = True
            elif single == "FLY_FORWARD":
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                sleep(0.1)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.move_right()
                sleep(0.5)
                controller.release_left_stick()
                command_executed = True
            elif single == "FLY_RIGHT":
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                sleep(0.1)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.move_right()
                sleep(0.5)
                controller.release_left_stick()
            elif single == "FLY_LEFT":
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                sleep(0.1)
                controller.push_button(BUTTON_A)
                controller.push_button(BUTTON_A)
                controller.move_left()
                sleep(0.5)
                controller.release_left_stick()
            elif single == "POWER_UP":
                controller.hold_dpad(DPAD_UP)
                sleep(1.5)
                controller.release_dpad()
                command_executed = True
                #commands for holding down each face button for 1 second
            elif single == "HOLD_DOWN":
                controller.hold_dpad(DPAD_DOWN)
                sleep(1.0)
                controller.release_dpad()
                command_executed = True
            elif single == "MOVE_DOWN":
                controller.hold_dpad(DPAD_DOWN)
                sleep(1.0)
                controller.release_dpad()
                command_executed = True
            elif single == "ADJUST_DOWN":
                controller.hold_dpad(DPAD_DOWN)
                sleep(0.3)
                controller.release_dpad()
                command_executed = True
            elif single == "HOLD_UP":
                controller.hold_dpad(DPAD_UP)
                sleep(1.0)
                controller.release_dpad()
                command_executed = True
            elif single == "MOVE_UP":
                controller.hold_dpad(DPAD_UP)
                sleep(1.0)
                controller.release_dpad()
                command_executed = True
            elif single == "ADJUST_UP":
                controller.hold_dpad(DPAD_UP)
                sleep(0.3)
                controller.release_dpad()
                command_executed = True
            elif single == "HOLD_LEFT":
                controller.hold_dpad(DPAD_LEFT)
                sleep(1.0)
                controller.release_dpad()
                command_executed = True
            elif single == "ADJUST_LEFT":
                controller.hold_dpad(DPAD_LEFT)
                sleep(0.3)
                controller.release_dpad()
                command_executed = True
            elif single == "MOVE_LEFT":
                controller.hold_dpad(DPAD_LEFT)
                sleep(1.0)
                controller.release_dpad()
                command_executed = True
            elif single == "HOLD_RIGHT":
                controller.hold_dpad(DPAD_RIGHT)
                sleep(1.5)
                controller.release_dpad()
                command_executed = True
            elif single == "ADJUST_RIGHT":
                controller.hold_dpad(DPAD_RIGHT)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "MOVE_RIGHT":
                controller.hold_dpad(DPAD_RIGHT)
                sleep(1.0)
                controller.release_dpad()
                command_executed = True
            elif single == "HOLD_A":
                controller.hold_buttons(BUTTON_A)
                sleep(1.0)
                controller.release_buttons(BUTTON_A)
                command_executed = True
            elif single == "HOLD_B":
                controller.hold_buttons(BUTTON_B)
                sleep(1.0)
                controller.release_buttons(BUTTON_B)
                command_executed = True
            elif single == "HOLD_X":
                controller.hold_buttons(BUTTON_A)
                sleep(1.0)
                controller.release_buttons(BUTTON_X)
                command_executed = True
            elif single == "HOLD_Y":
                controller.hold_buttons(BUTTON_Y)
                sleep(1.0)
                controller.release_buttons(BUTTON_Y)
                command_executed = True
            elif single == "ATTACK":
                controller.push_button(BUTTON_B)
                command_executed = True
            elif single == "BFF":
                controller.hold_buttons(BUTTON_X)
                sleep(0.1)
                controller.release_buttons(BUTTON_X)
                command_executed = True
            elif single == "DASH_KICK":
                increment_button_count("LY MAX")
                controller.move_down()
                sleep(0.5)
                controller.push_button(BUTTON_A)
                sleep(0.5)
                controller.release_left_stick()
            elif single == "DROP_ABILITY":
                controller.hold_buttons(BUTTON_Y)
                sleep(2.0)
                controller.release_buttons(BUTTON_Y)
                command_executed = True
            elif single == "CONNECT":  #connect the controller to the console
                controller.connect()
                command_executed = True
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
            print(data)
            if matches:
                (username, command, channel, message) = matches.groups()
                print(username + " --> " + message)
                if CURRENT_THREAD is None or not CURRENT_THREAD.is_alive():
                    CURRENT_THREAD = Thread(target=execute_command, args=[message])
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
        cfg = load(open(CONFIG_FILE, "r"))
    else:
        cfg = {"username": "", "password": ""}
        dump(cfg, open(CONFIG_FILE, "w"))
        print("Sample config created!")
        raise Exception("Please edit the configuration file to reflect your Twitch API settings")

    #check if database exists
    if not isfile(DATABASE_FILE):
        create_database()
        print("Database created!")

    with Controller() as controller:
        try:
            print("https://www.twitch.tv/" + cfg["username"])
            irc = TwitchIRC(cfg["username"], cfg["password"], cfg["username"])
        except KeyboardInterrupt:
            controller.reset().wait()
            exit(0)
        asyncore.loop()
