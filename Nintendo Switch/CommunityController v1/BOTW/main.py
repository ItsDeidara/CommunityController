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

MAX_COMMANDS_PER_MESSAGE = 8

CONFIG_FILE = "config.json"
DATABASE_FILE = "data.db"

#game mode
GAME_MODE = MODE_BACK_VIEW

#button shortcuts
JUMP_BUTTON = BUTTON_X

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
            elif single in ["START", "SELECT", "PLUS", "+", "MINUS", "-"]:
                if single in ["START", "PLUS", "+"]:
                   increment_button_count("START")
                   controller.push_button(BUTTON_PLUS)
                if single in ["SELECT", "MINUS", "-"]:
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
                    sleep(1.0)
                    controller.release_left_stick()
                elif single == "MOVE_BACK":
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    sleep(1.0)
                    controller.release_left_stick()
                elif single == "MOVE_LEFT":
                    increment_button_count("LX MIN")
                    controller.move_left()
                    sleep(1.0)
                    controller.release_left_stick()
                elif single == "MOVE_RIGHT":
                    increment_button_count("LX MAX")
                    controller.move_right()
                    sleep(1.0)
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
            #commands for holding down each face button for 1 second
            elif single in ["HOLD_A", "HOLD_B", "HOLD_X", "HOLD_Y"]:
                if single == "HOLD_A":
                    increment_button_count("A")
                    controller.hold_buttons(BUTTON_A)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_A)
                elif single == "HOLD_B":
                    increment_button_count("B")
                    controller.hold_buttons(BUTTON_B)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_B)
                elif single == "HOLD_X":
                    increment_button_count("X")
                    controller.hold_buttons(BUTTON_X)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_X)
                elif single == "HOLD_Y":
                    increment_button_count("Y")
                    controller.hold_buttons(BUTTON_Y)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_Y)
                command_executed = True
            elif single in ["HOLD_L", "HOLD_LB", "HOLD_R", "HOLD_RB", "HOLD_ZL", "HOLD_LT", "HOLD_ZR", "HOLD_RT", "HOLD_LCLICK", "HOLD_L3", "HOLD_RCLICK", "HOLD_R3"]:
                if single in ["HOLD_L", "HOLD_LB"]:
                    increment_button_count("L")
                    controller.hold_buttons(BUTTON_L)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_L)
                elif single in ["HOLD_R", "HOLD_RB"]:
                    increment_button_count("R")
                    controller.hold_buttons(BUTTON_R)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_R)
                elif single in ["HOLD_ZL", "HOLD_LT"]:
                    increment_button_count("ZL")
                    controller.hold_buttons(BUTTON_ZL)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_ZL)
                elif single in ["HOLD_ZR", "HOLD_RT"]:
                    increment_button_count("ZR")
                    controller.hold_buttons(BUTTON_ZR)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_ZR)
                elif single in ["HOLD_LCLICK", "HOLD_L3"]:
                    increment_button_count("LCLICK")
                    controller.hold_buttons(BUTTON_LCLICK)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_LCLICK)
                elif single in ["HOLD_RCLICK", "HOLD_R3"]:
                    increment_button_count("RCLICK")
                    controller.hold_buttons(BUTTON_RCLICK)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_RCLICK)
                command_executed = True
            elif single in ["HOLD_UP", "HOLD_DOWN", "HOLD_LEFT", "HOLD_RIGHT"]:
                if single == "HOLD_UP":
                    increment_button_count("UP")
                    controller.hold_dpad(DPAD_UP)
                    sleep(1.0)
                    controller.release_dpad()
                elif single == "HOLD_DOWN":
                    increment_button_count("DOWN")
                    controller.hold_dpad(DPAD_DOWN)
                    sleep(1.0)
                    controller.release_dpad()
                elif single == "HOLD_LEFT":
                    increment_button_count("LEFT")
                    controller.hold_dpad(DPAD_LEFT)
                    sleep(1.0)
                    controller.release_dpad()
                elif single == "HOLD_RIGHT":
                    increment_button_count("RIGHT")
                    controller.hold_dpad(DPAD_RIGHT)
                    sleep(1.0)
                    controller.release_dpad()
                command_executed = True
            elif single in ["PRESS_UP", "PRESS_DOWN", "PRESS_LEFT", "PRESS_RIGHT"]:
                if single == "PRESS_UP":
                    increment_button_count("UP")
                    controller.hold_dpad(DPAD_UP)
                    sleep(0.5)
                    controller.release_dpad()
                elif single == "PRESS_DOWN":
                    increment_button_count("DOWN")
                    controller.hold_dpad(DPAD_DOWN)
                    sleep(0.5)
                    controller.release_dpad()
                elif single == "PRESS_LEFT":
                    increment_button_count("LEFT")
                    controller.hold_dpad(DPAD_LEFT)
                    sleep(0.5)
                    controller.release_dpad()
                elif single == "PRESS_RIGHT":
                    increment_button_count("RIGHT")
                    controller.hold_dpad(DPAD_RIGHT)
                    sleep(0.5)
                    controller.release_dpad()
                command_executed = True
            elif single in ["ADJUST_BACKWARD", "ADJUST_BACK", "ADJUST_FORWARD", "ADJUST_LEFT", "ADJUST_RIGHT"]:
                if single == "ADJUST_BACKWARD":
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    sleep(0.3)
                    controller.release_left_stick()
                elif single == "ADJUST_BACK":
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    sleep(0.3)
                    controller.release_left_stick()
                elif single == "ADJUST_FORWARD":
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    sleep(0.3)
                    controller.release_left_stick()
                elif single == "ADJUST_LEFT":
                    increment_button_count("LX MIN")
                    controller.move_left()
                    sleep(0.3)
                    controller.release_left_stick()
                elif single == "ADJUST_RIGHT":
                    increment_button_count("LX MAX")
                    controller.move_right()
                    sleep(0.3)
                    controller.release_left_stick()
                command_executed = True
            elif single in ["GLANCE_UP", "GLANCE_DOWN", "GLANCE_LEFT", "GLANCE_RIGHT"]:
                if single == "GLANCE_UP":
                    increment_button_count("RY MIN")
                    controller.look_up()
                    sleep(0.125)
                    controller.release_right_stick()
                elif single == "GLANCE_DOWN":
                    increment_button_count("RY MAX")
                    controller.look_down()
                    sleep(0.125)
                    controller.release_right_stick()
                elif single == "GLANCE_LEFT":
                    increment_button_count("RX MIN")
                    controller.look_left()
                    sleep(0.125)
                    controller.release_right_stick()
                elif single == "GLANCE_RIGHT":
                    increment_button_count("RX MAX")
                    controller.look_right()
                    sleep(0.125)
                    controller.release_right_stick()
                command_executed = True
            #hold until manual release
            elif single in ["KEEP_HOLD_A", "KEEP_HOLD_B", "KEEP_HOLD_X", "KEEP_HOLD_Y"]:
                if single == "KEEP_HOLD_A":
                    increment_button_count("A")
                    controller.hold_buttons(BUTTON_A)
                elif single == "KEEP_HOLD_B":
                    increment_button_count("B")
                    controller.hold_buttons(BUTTON_B)
                elif single == "KEEP_HOLD_X":
                    increment_button_count("X")
                    controller.hold_buttons(BUTTON_X)
                elif single == "KEEP_HOLD_Y":
                    increment_button_count("Y")
                    controller.hold_buttons(BUTTON_Y)
                command_executed = True
            elif single in ["RELEASE_A", "RELEASE_B", "RELEASE_X", "RELEASE_Y"]:
                if single == "RELEASE_A":
                    controller.release_buttons(BUTTON_A)
                elif single == "RELEASE_B":
                    controller.release_buttons(BUTTON_B)
                elif single == "RELEASE_X":
                    controller.release_buttons(BUTTON_X)
                elif single == "RELEASE_Y":
                    controller.release_buttons(BUTTON_Y)
                command_executed = True
            elif single in ["KEEP_HOLD_L", "KEEP_HOLD_LB", "KEEP_HOLD_R", "KEEP_HOLD_RB", "KEEP_HOLD_ZL", "KEEP_HOLD_LT", "KEEP_HOLD_ZR", "KEEP_HOLD_RT"]:
                if single in ["KEEP_HOLD_L", "KEEP_HOLD_LB"]:
                    increment_button_count("L")
                    controller.hold_buttons(BUTTON_L)
                elif single in ["KEEP_HOLD_R", "KEEP_HOLD_RB"]:
                    increment_button_count("R")
                    controller.hold_buttons(BUTTON_R)
                elif single in ["KEEP_HOLD_ZL", "KEEP_HOLD_LT"]:
                    increment_button_count("ZL")
                    controller.hold_buttons(BUTTON_ZL)
                elif single in ["KEEP_HOLD_ZR", "KEEP_HOLD_RT"]:
                    increment_button_count("ZR")
                    controller.hold_buttons(BUTTON_ZR)
                command_executed = True
            elif single in ["RELEASE_L", "RELEASE_LB", "RELEASE_R", "RELEASE_RB", "RELEASE_ZL", "RELEASE_LT", "RELEASE_ZR", "RELEASE_RT"]:
                if single in ["RELEASE_L", "RELEASE_LB"]:
                    controller.release_buttons(BUTTON_L)
                elif single in ["RELEASE_R", "RELEASE_RB"]:
                    controller.release_buttons(BUTTON_R)
                elif single in ["RELEASE_ZL", "RELEASE_LT"]:
                    controller.release_buttons(BUTTON_ZL)
                elif single in ["RELEASE_ZR", "RELEASE_RT"]:
                    controller.release_buttons(BUTTON_ZR)
                command_executed = True
            elif single in ["KEEP_HOLD_UP", "KEEP_HOLD_DOWN", "KEEP_HOLD_LEFT", "KEEP_HOLD_RIGHT"]:
                if single == "KEEP_HOLD_UP":
                    increment_button_count("UP")
                    controller.hold_dpad(DPAD_UP)
                elif single == "KEEP_HOLD_DOWN":
                    increment_button_count("DOWN")
                    controller.hold_dpad(DPAD_DOWN)
                elif single == "KEEP_HOLD_LEFT":
                    increment_button_count("LEFT")
                    controller.hold_dpad(DPAD_LEFT)
                elif single == "KEEP_HOLD_RIGHT":
                    increment_button_count("RIGHT")
                    controller.hold_dpad(DPAD_RIGHT)
                command_executed = True
            elif single in ["RELEASE_DPAD", "RELEASE_UP", "RELEASE_DOWN", "RELEASE_LEFT", "RELEASE_RIGHT"]:
                controller.release_dpad()
                command_executed = True
            #game sensitive
            elif single in ["JUMP_FORWARD", "JUMP_UP", "JUMP", "JUMP_BACK", "JUMP_DOWN", "JUMP_LEFT", "JUMP_RIGHT"]:
                if single == "JUMP_FORWARD":
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    sleep(0.05)
                    controller.hold_buttons(JUMP_BUTTON)
                    sleep(0.95)
                    controller.release_buttons(JUMP_BUTTON)
                    controller.release_left_stick()
                elif single == "JUMP_UP":
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    sleep(0.05)
                    controller.hold_buttons(JUMP_BUTTON)
                    sleep(0.95)
                    controller.release_buttons(JUMP_BUTTON)
                    controller.release_left_stick()
                elif single == "JUMP":
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    sleep(0.05)
                    controller.hold_buttons(JUMP_BUTTON)
                    sleep(0.95)
                    controller.release_buttons(JUMP_BUTTON)
                    controller.release_left_stick()
                elif single == "JUMP_BACK":
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    sleep(0.05)
                    controller.hold_buttons(JUMP_BUTTON)
                    sleep(0.95)
                    controller.release_buttons(JUMP_BUTTON)
                    controller.release_left_stick()
                elif single == "JUMP_DOWN":
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    sleep(0.05)
                    controller.hold_buttons(JUMP_BUTTON)
                    sleep(0.95)
                    controller.release_buttons(JUMP_BUTTON)
                    controller.release_left_stick()
                elif single == "JUMP_LEFT":
                    increment_button_count("LX MIN")
                    controller.move_left()
                    sleep(0.05)
                    controller.hold_buttons(JUMP_BUTTON)
                    sleep(0.95)
                    controller.release_buttons(JUMP_BUTTON)
                    controller.release_left_stick()
                elif single == "JUMP_RIGHT":
                    increment_button_count("LX MAX")
                    controller.move_right()
                    sleep(0.05)
                    controller.hold_buttons(JUMP_BUTTON)
                    sleep(0.95)
                    controller.release_buttons(JUMP_BUTTON)
                    controller.release_left_stick()
                command_executed = True
            elif single in ["HOP", "HOP_FORWARD", "HOP_UP", "HOP_BACKWARD", "HOP_BACK", "HOP_DOWN", "HOP_LEFT", "HOP_RIGHT"]:
                if single == "HOP":
                    sleep(0.05)
                    controller.push_button(JUMP_BUTTON)
                    sleep(0.15)
                elif single == "HOP_FORWARD":
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    sleep(0.05)
                    controller.push_button(JUMP_BUTTON)
                    sleep(0.15)
                    controller.release_left_stick()
                elif single in ["HOP_BACKWARD", "HOP_BACK"]:
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    sleep(0.05)
                    controller.push_button(JUMP_BUTTON)
                    sleep(0.15)
                    controller.release_left_stick()
                elif single == "HOP_UP":
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    sleep(0.05)
                    controller.push_button(JUMP_BUTTON)
                    sleep(0.15)
                    controller.release_left_stick()
                elif single == "HOP_DOWN":
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    sleep(0.05)
                    controller.push_button(JUMP_BUTTON)
                    sleep(0.15)
                    controller.release_left_stick()
                elif single == "HOP_LEFT":
                    increment_button_count("LX MIN")
                    controller.move_left()
                    sleep(0.05)
                    controller.push_button(JUMP_BUTTON)
                    sleep(0.15)
                    controller.release_left_stick()
                elif single == "HOP_RIGHT":
                    increment_button_count("LX MAX")
                    controller.move_right()
                    sleep(0.05)
                    controller.push_button(JUMP_BUTTON)
                    sleep(0.15)
                    controller.release_left_stick()
                command_executed = True
            #game specific commands
            elif single == "CROUCH":
                increment_button_count("LCLICK")
                controller.push_button(BUTTON_LCLICK)
                command_executed = True
            elif single == "STAND":
                increment_button_count("LCLICK")
                controller.push_button(BUTTON_LCLICK)
                command_executed = True
            elif single == "BLOCK":
                increment_button_count("ZL")
                controller.hold_buttons(BUTTON_ZL)
                sleep(1.0)
                controller.release_buttons(BUTTON_ZL)
                command_executed = True
            elif single == "SHIELD":
                increment_button_count("ZL")
                controller.hold_buttons(BUTTON_ZL)
                sleep(1.0)
                controller.hold_buttons(BUTTON_ZL)
                command_executed = True
            elif single == "RUNE":
                increment_button_count("L")
                controller.hold_buttons(BUTTON_L)
                sleep(1.0)
                controller.release_buttons(BUTTON_L)
                command_executed = True
            elif single == "USE_RUNE":
                increment_button_count("L")
                controller.hold_buttons(BUTTON_L)
                sleep(1.0)
                controller.release_buttons(BUTTON_L)
                command_executed = True
            elif single == "DRAW_ARROW":
                increment_button_count("ZR")
                controller.hold_buttons(BUTTON_ZR)
                sleep(1.0)
                controller.hold_buttons(BUTTON_ZR)
                command_executed = True
            elif single == "SHOOT_ARROW":
                increment_button_count("ZR")
                controller.hold_buttons(BUTTON_ZR)
                sleep(1.0)
                controller.hold_buttons(BUTTON_ZR)
                command_executed = True
            elif single == "NEXT_WEAPON":
                increment_button_count("RIGHT")
                controller.hold_dpad(DPAD_RIGHT)
                sleep(0.5)
                increment_button_count("R")
                controller.push_button(BUTTON_R)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "NEXT_ARROW":
                increment_button_count("LEFT")
                controller.hold_dpad(DPAD_LEFT)
                sleep(0.5)
                increment_button_count("R")
                controller.push_button(BUTTON_R)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "NEXT_SHIED":
                increment_button_count("LEFT")
                controller.hold_dpad(DPAD_LEFT)
                sleep(0.5)
                increment_button_count("R")
                controller.push_button(BUTTON_R)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "NEXT_RUNE":
                increment_button_count("UP")
                controller.hold_dpad(DPAD_UP)
                sleep(0.5)
                increment_button_count("R")
                controller.push_button(BUTTON_R)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "PREVIOUS_WEAPON":
                increment_button_count("RIGHT")
                controller.hold_dpad(DPAD_RIGHT)
                sleep(0.5)
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "LAST_WEAPON":
                increment_button_count("RIGHT")
                controller.hold_dpad(DPAD_RIGHT)
                sleep(0.5)
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "PREVIOUS_ARROW":
                increment_button_count("LEFT")
                controller.hold_dpad(DPAD_LEFT)
                sleep(0.5)
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "LAST_ARROW":
                increment_button_count("LEFT")
                controller.hold_dpad(DPAD_LEFT)
                sleep(0.5)
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "PREVIOUS_SHIELD":
                increment_button_count("LEFT")
                controller.hold_dpad(DPAD_LEFT)
                sleep(0.5)
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "LAST_SHIELD":
                increment_button_count("LEFT")
                controller.hold_dpad(DPAD_LEFT)
                sleep(0.5)
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "PREVIOUS_RUNE":
                increment_button_count("UP")
                controller.hold_dpad(DPAD_UP)
                sleep(0.5)
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "LAST_RUNE":
                increment_button_count("UP")
                controller.hold_dpad(DPAD_UP)
                sleep(0.5)
                increment_button_count("L")
                controller.push_button(BUTTON_L)
                sleep(0.5)
                controller.release_dpad()
                command_executed = True
            elif single == "ATTACK":
                increment_button_count("Y")
                controller.push_button(BUTTON_Y)
                sleep(0.2)
                command_executed = True
            elif single == "BASH":
                increment_button_count("Y")
                controller.push_button(BUTTON_Y)
                sleep(0.5)
                command_executed = True
            elif single == "CLIMB":
                increment_button_count("X")
                controller.push_button(BUTTON_X)
                command_executed = True
            elif single == "FOCUS":
                increment_button_count("ZL")
                controller.push_button(BUTTON_ZL)
                command_executed = True
            elif single == "SHEIKAH_SLATE":
                increment_button_count("SELECT")
                controller.push_button(BUTTON_MINUS)
                sleep(0.5)
                command_executed = True
            elif single == "MENU":
                increment_button_count("START")
                controller.push_button(BUTTON_PLUS)
                sleep(0.5)
                command_executed = True
            elif single == "STRAFE_LEFT":
                controller.move_left()
                controller.hold_buttons(BUTTON_ZL)
                sleep(1.5)
                controller.release_buttons(BUTTON_ZL)
                controller.release_left_stick()
                command_executed = True
            elif single == "STRAFE_RIGHT":
                controller.move_right()
                controller.hold_buttons(BUTTON_ZL)
                sleep(1.5)
                controller.release_buttons(BUTTON_ZL)
                controller.release_left_stick()
                command_executed = True
            elif single == "FOCUS":
                controller.push_button(BUTTON_ZL)
                command_executed = True
            elif single in ["RUN", "RUN_FORWARD", "RUN_UP", "RUN_BACKWARD", "RUN_BACK", "RUN_DOWN", "RUN_LEFT", "RUN_RIGHT"]:
                if single in ["RUN", "RUN_FORWARD"]:
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    increment_button_count("B")
                    controller.hold_buttons(BUTTON_B)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_B)
                    controller.release_left_stick()
                elif single in ["RUN_BACKWARD", "RUN_BACK"]:
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    increment_button_count("B")
                    controller.hold_buttons(BUTTON_B)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_B)
                    controller.release_left_stick()
                elif single == "RUN_UP":
                    increment_button_count("LY MIN")
                    controller.move_forward(GAME_MODE)
                    increment_button_count("B")
                    controller.hold_buttons(BUTTON_B)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_B)
                    controller.release_left_stick()
                elif single == "RUN_DOWN":
                    increment_button_count("LY MAX")
                    controller.move_backward(GAME_MODE)
                    increment_button_count("B")
                    controller.hold_buttons(BUTTON_B)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_B)
                    controller.release_left_stick()
                elif single == "RUN_LEFT":
                    increment_button_count("LX MIN")
                    controller.move_left()
                    increment_button_count("B")
                    controller.hold_buttons(BUTTON_B)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_B)
                    controller.release_left_stick()
                elif single == "RUN_RIGHT":
                    increment_button_count("LX MAX")
                    controller.move_right()
                    increment_button_count("B")
                    controller.hold_buttons(BUTTON_B)
                    sleep(1.0)
                    controller.release_buttons(BUTTON_B)
                    controller.release_left_stick()
                command_executed = True
            elif single in ["ONWARD"]:
                increment_button_count("LY MIN")
                controller.move_forward(GAME_MODE)
                command_executed = True
            elif single in ["STOP", "STILL"]:
                controller.release_left_stick()
                command_executed = True
            elif single == "PULL_OUT":
                increment_button_count("A")
                controller.hold_buttons(BUTTON_A)
                command_executed = True
            elif single == "MOVEMENTWAIT":
                controller.reset().wait()
                command_executed = True
            elif single == "CONNECT":  #connect the controller to the console
                controller.connect()
                command_executed = True
            # Experimental
            elif single == "DASH_ATTACK":
                increment_button_count("LY MIN")
                controller.move_forward(GAME_MODE)
                increment_button_count("B")
                controller.hold_buttons(BUTTON_B)
                sleep(0.05)
                increment_button_count("Y")
                controller.push_button(BUTTON_Y)
                sleep(0.15)
                controller.release_left_stick()
                controller.release_buttons(BUTTON_B)
                command_executed = True
            elif single == "EXPGLIDE":
                controller.move_forward(GAME_MODE)
                sleep(0.05)
                controller.push_button(BUTTON_X)
                sleep(0.05)
                controller.push_button(BUTTON_X)
                sleep(0.05)
                controller.push_button(BUTTON_X)
                sleep(0.05)
                controller.push_button(BUTTON_X)
                sleep(0.05)
                controller.release_left_stick()
                command_executed = True
            # Custom commands
            elif single[0:7] == "CUSTOM(" and single.find(")") > 7:  # single == "CUSTOM(smthg)"
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
                    if i in [BUTTON_PLUS, BUTTON_MINUS, BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y, BUTTON_L, BUTTON_R,
                             BUTTON_ZL, BUTTON_ZR, BUTTON_LCLICK, BUTTON_RCLICK]:
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
                    if i in [BUTTON_PLUS, BUTTON_MINUS, BUTTON_A, BUTTON_B, BUTTON_X, BUTTON_Y, BUTTON_L, BUTTON_R,
                             BUTTON_ZL, BUTTON_ZR, BUTTON_LCLICK, BUTTON_RCLICK]:
                        controller.release_buttons(i)
                    elif i in [DPAD_UP, DPAD_DOWN, DPAD_LEFT, DPAD_RIGHT]:
                        controller.release_dpad()
                    elif i in ["L_UP", "L_DOWN", "L_LEFT", "L_RIGHT"]:
                        controller.release_left_stick()
                    elif i in ["R_UP", "R_DOWN", "R_LEFT", "R_RIGHT"]:
                        controller.release_right_stick()

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
