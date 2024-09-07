# Dynpot
A Dynmap Web Chat Honeypot\

## Setup
- Clone this repository, modify dynmap_config.json and honeypot.config as needed, install the requirements and run.
## Config Files
- dynmap_config.json: The configuration that /configuration returns, you'll most likely want to leave it at default
- honeypot_config.json: Honeypot configuration. Pretty self-explanatory, "port" is the port that the honeypot will run on, "discord_webhook_enabled" is whether you want Discord Webhook logging and "discord_webhook_url" is the url of your Webhook (if you have one). Same goes for "file_logging" and "log_file".