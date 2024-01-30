# Snowflake

A card-jitsu snow server emulator, made for houdini.
This is still a work in progress, and is not ready for general use yet.

## What works?

- [x] Player Select
- [x] Matchmaking
- [x] Base Game Engine
    - [x] Creating, moving & animating game objects
    - [x] SWF Windows
    - [x] Sounds
    - [x] Assets
- [x] Basic round loop
    - [x] Timer
    - [x] User Interface
    - [x] Round Title
    - [x] Spawning Ninjas
    - [x] Spawning Enemies
- [x] Moving Ninjas
- [ ] Attacking
    - [x] Water Attacks
    - [ ] Snow Attacks
    - [ ] Fire Attacks
- [ ] Healing
- [ ] Reviving
- [ ] Powercards
- [ ] Powercard Combos
- [ ] Member Cards
- [ ] Enemy AI
- [ ] EXP/Coins System
- [x] Payout
- [ ] Stamps
- [ ] Tusk Battle
- [ ] Custom Features
    - [ ] Singleplayer Mode
    - [ ] Ninja AI

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