# Snowflake

A card-jitsu snow server emulator, made for houdini.
This is still a work in progress, and is not ready for general use yet.

## Setup

1. Get a working installation of [wand](https://github.com/solero/wand)

2. Install a copy of [python](https://python.org) with pip

2. Open the `templates/vanilla-media/play/index.html.template` file in your editor of choice

3. Search for a line with "wns" in it, and change it from `"wns":"n7vcp1clubpwns.clubpenguin.com"` to `"wns":"{{ (parseUrl .Env.WEB_VANILLA_PLAY).Host }}"`

4. Restart nginx: `sudo docker-compose restart web`

5. Clone this repository: `git clone https://github.com/Lekuruu/snowflake.git`

6. Rename the `.env_example` file to `.env` and **edit it**, to match your setup

7. Install the requirements: `pip install -r requirements.txt`

7. Run the server: `python main.py`
