from flask import Flask, jsonify, request, Response
import json
from datetime import datetime, timezone
import requests
import waitress
import csv
import os

app = Flask(__name__)

def discord_logging(spam_name, spam_message, spam_ip):
    fields = []
    if not spam_name == "": # add the name field only if there is a name
        fields.append({
            "name": "Name",
            "value": spam_name.replace("`", "'"),
            "inline": False
        })
    fields.append({
        "name": "Message",
        "value": spam_message.replace("`", "'"),
        "inline": False
    })
    
    embed = {
        "embeds": [
            {
                "title": "Message sent!",
                "description": f"A new message was sent via the Dynmap web chat from `{spam_ip}`",
                "fields": fields, # add fields from above
                "color": 0xADD8E6,
                "timestamp": datetime.now(timezone.utc).astimezone().isoformat() # current timestamp
            }
        ]
    }
    
    # send the thing to the webhook
    requests.post(discord_webhook_url, data=json.dumps(embed), headers={"Content-Type": "application/json"})

@app.route('/configuration', methods=['GET'])
def configpoint():
    # return the dynmap configuration from dynmap_config.json
    return jsonify(dynmap_config)

@app.route('/up/sendmessage', methods=['POST'])
def chatpoint():
    spam_name = request.json.get("name")
    spam_message = request.json.get("message")
    spam_ip = request.remote_addr
    if discord_enabled is True:
        discord_logging(str(spam_name), str(spam_message), str(spam_ip))
    if fl_enabled is True:
        fieldnames = ["ip", "name", "message", "timestamp"]
        towrite = {
            "ip": spam_ip,
            "name": spam_name,
            "message": spam_message,
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat()
        }
        with open(fl_path, 'a', newline='', encoding='utf-8', errors='ignore') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # write the header only if the file is empty
            if csvfile.tell() == 0:
                writer.writeheader()
            writer.writerow(towrite)
    print("New message")
    print(f" - From: {spam_ip}")
    print(f" - Name: {spam_name}")
    print(f" - Message: {spam_message}")
    return Response('{"error": "none"}', content_type='text/plain;charset=utf-8')

if __name__ == "__main__":
    global dynmap_config, discord_enabled, discord_webhook_url, fl_enabled, fl_path
    
    # load the dynmap config for the /configuration endpoint
    print("Reading Dynmap config")
    try:
        with open('dynmap_config.json', 'r') as dynconf:
            dynmap_config = json.load(dynconf)
    except FileNotFoundError:
        print("Dynmap config (dynmap_config.json) not found, exiting")
        exit()
    except json.JSONDecodeError:
        print("Error decoding JSON from dynmap_config.json, exiting")
        exit()
    
    # read main config
    print("Reading honeypot config")
    try:
        with open('honeypot_config.json', 'r') as honconf:
            honeypot_config = json.load(honconf)
            # check if discord webhook is enabled
            discord_enabled = honeypot_config.get("discord_webhook_enabled", False)
            print(f" - Discord Logging: {discord_enabled}")
            if discord_enabled is False:
                discord_webhook_url = None
            else:
                discord_webhook_url = honeypot_config.get("discord_webhook_url", None)
                if not discord_webhook_url: # exit if there's no webhook
                    print("Discord Webhook Logging is enabled, but no Webhook was provided. Exiting...")
                    exit()
            # check if file logging is enabled
            fl_enabled = honeypot_config.get("file_logging", False)
            print(f" - Log to file: {fl_enabled}")
            if fl_enabled is False:
                fl_path = None
            else:
                fl_path = honeypot_config.get("log_file", None)
                if not fl_path: # exit if there's no webhook
                    print("File Logging is enabled, but no path was provided. Exiting...")
                    exit()
                # create log file if doesn't exist
                if not os.path.exists(fl_path):
                    with open(fl_path, 'w') as file:
                        pass
                # write header if it doesn't exist
                header = "ip,name,message,timestamp"
                with open(fl_path, 'r', encoding='utf-8', errors='ignore') as filer:
                    first_line = filer.readline().strip()
                    if first_line != header:
                        with open(fl_path, 'w', encoding='utf-8', errors='ignore') as filer2:
                            filer2.write(header + '\n')
                            filer2.writelines(filer.readlines())
            # check if port is provided
            if honeypot_config.get("port", False) is False:
                print("No port provided, exiting")
                exit()
            else:
                honeyport = honeypot_config.get("port")
                print(f" - Port: {honeyport}")
    except FileNotFoundError:
        print("Honeypot config (honeypot_config.json) not found, exiting")
        exit()
    except json.JSONDecodeError:
        print("Error decoding JSON from honeypot_config.json, exiting")
        exit()
    
    print("Starting honeypot")
    waitress.serve(app, host='0.0.0.0', port=honeyport)