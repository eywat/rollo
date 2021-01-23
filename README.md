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

Additionally, you can obtain a [tenor token](https://tenor.com/developer/keyregistration), to search for and post GIFs. 

Add a `.env` file to the rollo folder with the following content: 
```
BOT_TOKEN=your-discord-token-here
TENOR_TOKEN=your-tenor-token-here # Optional
LOG_LEVEL=10 # Optional
```

To run the bot simply run: `python rollo.py`
