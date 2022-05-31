# PEON - BOT - Discord

![PEON](https://github.com/nox-noctua-consulting/peon/blob/main/media/andre-kent-peon-turntable.jpeg)
Art by [André Kent - Artstation](https://www.artstation.com/artwork/W2E0RQ)
**This project owns no rights to the image above. Please link to the site and request them accordingly.**

## The Easy Game Server Manager

### [Peon Project](https://github.com/nox-noctua-consulting/peon)

An **OpenSource** project to assist gamers in self-deploying/managing game servers.\
Intended to be a one-stop-shop for game server deployment/management.\
If run on a public/paid cloud, it is architected to try to minimise costs (easy schedule/manage uptime vs downtime)

### Peon Bot Discord (peon.bot.discord)

The [github](https://github.com/nox-noctua-consulting/peon-bot-discord/) repo for developing the peon server orchestrator.

## State

> **EARLY DEVELOPMENT**

## Version Info

Check [changelog](https://github.com/nox-noctua-consulting/peon-bot-discord/blob/master/changelog.md) for more information

### Known Bugs

### Architecture/Rules

Discord bot is built as a docker image for easy deployment.

### Feature Plan

#### *sprint 0.1.0*

- [ ] peon.orc servers can be managed by bot

### *sprint 0.2.0*

- [ ] peon.orc - servers can be created from discord

### Notes

[Guide](https://realpython.com/how-to-make-a-discord-bot-python/)

[Discord Application](https://discord.com/developers/applications)

[Discord.py](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#bots)

### Usage

> :point_up:  ``!poke``  to check if there is an available peon to do some work.\
> :european_castle:  ``!getall``  to list all warcamps in the warparty.\
> :tent:  ``!get orchestrator.uid game_server_uid``  to show the status of a warcamp.\
> :white_check_mark:  ``!start orchestrator.uid game_server_uid``  to start a warcamp.\
> :checkered_flag:  ``!stop orchestrator.uid game_server_uid``  to stop a warcamp.\
> :recycle:  ``!restart orchestrator.uid game_server_uid``  to restart a warcamp.\
> :calendar:  ``!schedule orchestrator.uid game_server_uid CCYY/MM/DD-HH:MM:SS``  to schedule a date and time when a warcamp must start/stop.\
> :clock3:  ``!extend orchestrator.uid game_server_uid [x]m/h/d``  to keep a warcamp alive for [x] more hours.\
> :wrench:  ``!register orchestrator.uid orchestrator.url orchestrator.apikey``  to register a warparty.\
> :hammer:  ``!unregister orchestrator.uid``  to remove a registered warparty.\
> :grey_question:  ``!usage``  to print this help menu.\
*Warparty - An vm/pc/server running the orchestrator software as well as hosting game servers*\
*Warcamp - A game server*

## Support the Project

PEON is an open-source project that I am working on in my spare time (for fun).
However, if you still wish to say thanks, feel free to pick up a virtual coffee for me at Ko-fi.

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/K3K567ILJ)
