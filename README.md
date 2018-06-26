# What even is this?

Glad you asked! Community Controller aims to bring a 24/7 interactive stream to your favorite platforms! So kick back, relax, and take control! Starting with Twitch Plays Nintendo Switch!

## Controls

All of the main switch buttons can be typed out in chat and work as a control.
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

### Custom commands

Thanks to the work of one of our community members(fazzfadf), we now support the use of custom commands in chat, that should allow you to circumvent any/all situations that the main controls make difficult!



```
Syntaxes :
    custom(button)
    custom(button; duration)
    custom([button; button2; ...])
    custom([button; button2; ...]; duration

    Please note that in these custom commands you use a semicolon(;) as a separator and not the usual comma(,)

Duration :
decimals between 0 (strictly greater) and 1
when duration is not specified or invalid, it lasts 0.02 second

Examples:
  custom(lup; 1.0) #holds up on left stick for 1 second
  custom([lup; x]) #presses up on left stick and X at the same time
  custom([lup; x]; 0.5) #holds up on left stick and X for half a second

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

wait #does nothing for the specified time

```
