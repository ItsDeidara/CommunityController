# What even is this?

This is the source code used for CommunityController also known as Twitch Plays Nintendo Switch/Twitch Plays Super Mario Odyssey! I am sharing the files I used in hopes our community can improve the code to make the stream better and so people can further innovate on this project and create their own bots!

## What can I do with this?

I'm glad you asked! This bot uses a simple Python script (seriously check it out, a child could learn it) so you can do a pletora of things. For example, you can make a rudimentary TAS bot for your favorite game or create a bot to duplicate & sell items to get an infinite amount of gold!

## This is great, but what's the catch?
There is no catch at all! I only ask you link back to this repo within your Project if you use it. 

## Is there a discussion thread or anywhere that I can go for support, or to share my work? 
Of course there is! You can find a [gbatemp thread for this bot here](https://gbatemp.net/threads/communitycontroller-pro-controller-python-bot.528158/)

## Known bugs
1. Serial Connection randomly closes and will not re-open. A dirty fix is to start the main.py file with a looping shell script like I did in CommunityController
2. The left thumbstick is not completly centered. It is fine in most cases but it can cause oddities in some games. For example, you are not able to navigate the map in Breath of the Wild or Warp in Super Mario Odyssey. This bug may cause the character to drift forward but I have only encountered this in the Nintendo Switch version of Fortnite
