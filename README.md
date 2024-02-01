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
- [x] Ninjas
    - [x] Movement
    - [x] Attacks
    - [x] Healing
    - [x] Reviving
- [ ] Enemies
    - [ ] Movement
    - [ ] Attacks
    - [ ] AI
- [ ] Powercards
- [ ] Powercard Combos
- [ ] Member Cards
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

## Screenshots

![image](https://github.com/Lekuruu/snowflake/assets/84310095/107a05aa-79ed-45ec-9b9e-182ec1e686fc)

![image](https://github.com/Lekuruu/snowflake/assets/84310095/61c741a2-b4a4-4133-b596-e0ece93c6e31)
