# Rollo
A simple Discord bot for rolling dice, voting and posting GIFs.

## Installation 
Requires: `python 3.6` or higher. 

Install:
```bash
git clone https://github.com/eywat/rollo.git
cd rollo 
pip install -r requirements.txt
```
To run the bot you need a Discord application token, which can be obtained from [here](https://discord.com/developers/applications).
You will need to create an application and under the applications _Bot_ tab, you can create a Bot and access the token. 

Additionally, you can obtain a [tenor token](https://tenor.com/developer/keyregistration), to search for and post GIFs. 

Add a `.env` file to the rollo folder with the following content: 
```
BOT_TOKEN=your-discord-token-here
TENOR_TOKEN=your-tenor-token-here # Optional
LOG_LEVEL=10 # Optional
```

To run the bot simply run: `python rollo.py`

If you want to add the Bot to a guild, in the Discord Developer Portal, you will to access _OAuth2_ under your Bot's _Application_. There you have to select `bot` in _SCOPES_ and in the then appearing _BOT PERMISSIONS_ you will need to select `Send Messages, Embed Links, Attach Files, Read Message History`.
