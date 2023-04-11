# PEON - BOT - Discord

![PEON](https://github.com/the-peon-project/peon/blob/main/media/andre-kent-peon-turntable.jpeg)
Art by [André Kent - Artstation](https://www.artstation.com/artwork/W2E0RQ)
**This project owns no rights to the image above. Please link to the site and request them accordingly.**

[![Docker Pulls](https://img.shields.io/docker/pulls/umlatt/peon.bot.discord.svg)](https://hub.docker.com/r/umlatt/peon.bot.discord)
[![Docker Stars](https://img.shields.io/docker/stars/umlatt/peon.bot.discord.svg)](https://hub.docker.com/r/umlatt/peon.bot.discord)

## The Easy Game Server Manager

### Installation

> Please find the installation instructions at [PEON](https://github.com/the-peon-project/peon/) master project, as there are several dependencies that are required for this module to work correctly.

### [Peon Project](https://github.com/the-peon-project/peon)

An **OpenSource** project to assist gamers in self-deploying/managing game servers.\
Intended to be a one-stop-shop for game server deployment/management.\
If run on a public/paid cloud, it is architected to try to minimise costs (easy schedule/manage uptime vs downtime)

### Peon Bot Discord (peon.bot.discord)

The [github](https://github.com/the-peon-project/peon-bot-discord/) repo for developing the peon bot for discord.

## State

> **EARLY DEVELOPMENT**

## Version Info

Check [changelog](https://github.com/the-peon-project/peon-bot-discord/blob/master/changelog.md) for more information

### Known Bugs

### Architecture/Rules

Discord bot is built as a docker image for easy deployment.

### Feature Plan

#### *sprint 0.1.0*

- [x] peon.orc servers can be managed by bot

#### *sprint 0.2.0*

- [ ] peon.bot.discord bot is re-written for ``slash`` commands (see ``interactions.py``)

### Notes

[Guide](https://realpython.com/how-to-make-a-discord-bot-python/)

[Discord Application](https://discord.com/developers/applications)

[Discord.py](https://discordpy.readthedocs.io/en/stable/ext/commands/api.html#bots)

#### Improved bots

[interactions.py](https://discord-interactions.readthedocs.io/en/latest/quickstart.html)

### Usage

> :point_up:  ``!poke``  to check if there is an available peon to do some work.\
> :european_castle:  ``!getall``  to list all warcamps in their warparties.\
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
