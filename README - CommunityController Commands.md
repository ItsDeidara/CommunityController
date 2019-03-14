## Controls

All of the main Switch buttons can be typed out in chat and work as a control. Please note that you can also press two buttons at the same time by chaining them together with an & symbol. For example, if you want to press both A and B at the same time, you would enter A & B in chat. Commands are not case-sensitive.

```
A / B/ X / Y
UP / DOWN / LEFT / RIGHT
Move forward / back / left / right
Adjust Forward / Backward / Left / Right
L3 (left stick click)
R3 (right stick click)
LT (left trigger)
LB (left bumper)
RT (right trigger)
RB (right bumper)
Look Left / right / up / down
```

### Custom Commands

Thanks to the work of one of our community members(fazzfadf), we now support the use of custom commands in chat. These should allow you to circumvent any/all situations that the main controls make difficult!



```
Syntaxes:
    custom(button)
    custom(button; duration)
    custom([button; button2; ...])
    custom([button; button2; ...]; duration

    Please note that in these custom commands you use a semicolon(;) as a separator and not the usual comma(,).

Duration:
Decimals between 0 (strictly greater) and 1.
When duration is not specified or is invalid, it lasts 0.02 seconds.
All time durations are measured in seconds.

Examples:
  custom(lup; 1.0) #holds up on left stick for 1 second.
  custom([lup; x]) #presses up on left stick and X at the same time.
  custom([lup; x]; 0.5) #holds up on left stick and X for half a second.

Available Buttons:
A, B, X, Y

l, lb #L on joycon

r, rb #R on joycon

zl, lt #zl/left trigger on joycon

zr, rt #zr/right trigger on joycon

lclick, l3 #presses left stick

rclick, r3 #presses right stick

lup, ldown, lleft, lright #left stick movement

rup, rdown, rleft, rright #right stick movement

dup, ddown, dleft, dright, #dpad

wait #does nothing for the specified time, measured in seconds

```

# Game Specific Commands

* **Super Mario Odyssey**
    * Capture (Throws Cappy)
    * Ground Pound
    * Crouch
    * Backflip
    * Long Jump
    * Swim
    * Dive
    * Flick Up
* **Kirby Star Allies**
    * Attack
    * BFF
    * Dash Kick
    * Drop Ability
    * Suck
        * Succ
    * Swallow
* **Skyrim**
    * Activate
    * Sneak
    * Shout
    * Character Menu
    * Menu
    * Wait
    * Rear
    * Ready
* **The Legend of Zelda: Breath of the Wild**
    * Onward (Allows Link to walk forever until told to stop)
        * Stop  (Stops Link from walking)
        * Still (Stops Link from walking)
    * Run (Makes Link run)
    * Hop
        * Hop left
        * Hop right
        * Hop down
        * Hop up
        * Hop back
        * Hop backward
    * Attack
        * Bash (quick attack for when Link is catching his breath)
    * Climb
    * Focus
    * Sheikah Slate
    * Previous Rune
    * Last Rune
    * Previous Shield
    * Last Shield
    * Previous Arrow
    * Last Arrow
    * Previous Weapon
    * Last Weapon
    * Next Rune
    * Next Shield
    * Next Arrow
    * Next Weapon
    * Shoot Arrow
    * Draw Arrow
    * Use Rune
    * Shield
    * Block
    * Crouch
    * Glide
* **Donkey Kong: Tropical Freeze**
    * Kong Pow
        * Pow
        * KP
    * Grab
    * Throw
    * Pluck
    * Combine
    * Dismount
    * Roll Attack
    * Attack
    * Corkscrew
    * Swim
    * Keep Hold ZL (Holds ZL forever)
    * Release ZL   (Undos aforementioned hold ZL command)
* **Splatoon 2**
    * Keep Hold ZL (Holds ZL forever)
    * Release ZL   (Undos aforementioned hold ZL command)
* **A Link to the Past**
    * Walk Direction (Makes Link walk in the specified direction until told to stop)
    * Look Direction (Makes Link turn without moving)
    * Stand Still (Makes Link stop walking)
    * Stop Walking (Makes Link stop walking)
    * Stop (Makes Link stop walking)
    * Still (Makes Link stop walking)
    * Spin Attack
* **Xenoblade Chronicles 2**
    * Toggle Map (Toggles the minimap zoom)
    * Zoom Map (Same as above)
    * Target (Locks onto the enemy)
    * Engage (Locks onto the enemy and also initiates combat)
    * Menu (Pauses the game)
    * System (Brings up the system menu to allow for game saving and setting adjustment)
    * Travel (Brings up the skip travel menu which lets you fast travel)
* **Super Smash Bros Ultimate**
    * Strafe *direction*
    * Final Smash
    * Plus Ultra (Same as Final Smash)
    * Jump *direction*
    * Hop *direction*
    * Hold Smash *direction*
    * Adjust *direction*
    * Menu (Pauses the game)
    * Tilt *direction* (Tilt Attacks)
    * Special *direction* 
