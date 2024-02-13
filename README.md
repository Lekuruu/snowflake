# Snowflake

A work-in-progress card-jitsu snow server emulator, made for houdini.

## Progress

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
- [x] Enemies
    - [x] Movement
    - [x] Attacks
    - [x] AI
- [x] Powercards
    - [x] Progressbar
    - [x] Placing
    - [x] Animations
    - [x] Combos
    - [x] Effects
- [x] Member Card
- [x] Payout
- [x] Coins
- [x] EXP
- [x] Rewards
- [ ] Stamps
- [ ] Tusk Battle
- [ ] Custom Features
    - [ ] Singleplayer Mode
    - [ ] Ninja AI

## Setup

This setup requires you to have a working installation of houdini with dash, as well as a copy of [python](https://python.org) (3.8 to 3.12).
There is some necessary configuration to get this working, which I will cover in the following sections.

### Changing the wns url

The card-jitsu snow engine needs a special "wns url", to be able to connect to the right server.
You can find this url inside your `index.html` file, and searching for "wns".

If you have houdini set up with [wand](https://github.com/solero/wand), it would look something like this:

1. Open the `templates/vanilla-media/play/index.html.template` file in your editor of choice

2. Change the line with `"wns":"n7vcp1clubpwns.clubpenguin.com"` to `"wns":"{{ (parseUrl .Env.WEB_VANILLA_PLAY).Host }}"`

3. Restart nginx: `sudo docker-compose restart web`

This may be different for your setup of course. The important part is that the wns url is set to your vanilla play url, i.e. "play.localhost", or "localhost/play/".

### Configuring dash

**This step is not required if you run this project locally!**

Dash will tell the card-jitsu snow client where the game server is located, and thus needs to have the right configuration as well.

1. Open the `settings.py` file inside the `dash` folder

2. Search for a line with `CJS_HOST`

3. Change the content of the `CJS_HOST` to your **public ip address**

4. Restart dash

### Setting up snowflake

And now, we need to set up the actual repository.

1. Clone this repository: `git clone https://github.com/Lekuruu/snowflake.git`

2. Rename the `.env_example` file to `.env` and **edit it**, to match your setup

3. Install the requirements: `pip install -r requirements.txt`

4. Run the server: `python main.py`

## Troubleshooting

If something went wrong, you will most likely see this screen pop up:

![image](https://raw.githubusercontent.com/Lekuruu/snowflake/main/.github/screenshots/troubleshooting.png)

There are many reasons why this could be happening.
Here are some things to check:

1. Ensure that port 7002 and 843 are accessible from the outside

2. Check if your `crossdomain.xml` is accessible under `<your_play_url>/crossdomain.xml`

3. Ensure you set the right media url in the `.env`

If all of that didn't work, check if your server is `https` only, i.e. only allowing secure ssl connections. If that is the case, you need to replace the `flash_client_base_fp11.swf` inside `/game/mpassets/playclients/r3662/` with [this file](https://github.com/Lekuruu/snowflake/raw/main/.github/swf/flash_client_base_fp11.swf).

## Screenshots

![image](https://raw.githubusercontent.com/Lekuruu/snowflake/main/.github/screenshots/gameplay1.png)

![image](https://raw.githubusercontent.com/Lekuruu/snowflake/main/.github/screenshots/gameplay2.png)

![image](https://raw.githubusercontent.com/Lekuruu/snowflake/main/.github/screenshots/gameplay3.png)
