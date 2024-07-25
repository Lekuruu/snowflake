# Setup

This setup requires you to have a working installation of [Houdini](https://github.com/solero/houdini) with [Dash](https://github.com/solero/dash), as well as a copy of [Python](https://python.org) (3.8 to 3.12).
There is some necessary configuration to get this working, which will be covered in the following sections.

## Changing the WNS URL

The Card-Jitsu Snow engine needs a special "WNS URL", to be able to connect to the right server.
You can find this URL inside your `index.html` file, and searching for "wns".

If you have Houdini set up with [Wand](https://github.com/solero/wand), it would look something like this:

1. Open the `templates/vanilla-media/play/index.html.template` file in your editor of choice

2. Change the line with `"wns":"n7vcp1clubpwns.clubpenguin.com"` to `"wns":"{{ (parseUrl .Env.WEB_VANILLA_PLAY).Host }}"`

3. Restart nginx: `sudo docker-compose restart web`

This may be different for your setup of course. The important part is that the WNS URL is set to your vanilla play URL, i.e. "play.localhost", or "localhost/play/".

## Configuring Dash

**This step is not required if you run this project locally!**

Dash will tell the Card-Jitsu Snow client where the game server is located, and thus needs to have the right configuration as well.

1. Open the `settings.py` file inside the `dash` folder

2. Search for a line with `CJS_HOST`

3. Change the content of the `CJS_HOST` to your **public ip address**

4. Restart dash

## Setting up Snowflake

And now, we need to set up the actual repository.

1. Clone this repository: `git clone https://github.com/Lekuruu/snowflake.git`

2. Rename the `.env_example` file to `.env` and **edit it**, to match your setup

3. Install the requirements: `pip install -r requirements.txt`

4. Run the server: `python main.py`

## Beta Mode

Snowflake includes a recreation of the Card-Jitsu Snow beta as a toggleable option. If you wish to use this feature, you'll need to add a few new SWF files.

- [cardjitsu_snowpayoutbeta.swf](https://github.com/Lekuruu/snowflake/raw/main/.github/swf/cardjitsu_snowpayoutbeta.swf) and [cardjitsu_snowplayerselectbeta.swf](https://github.com/Lekuruu/snowflake/raw/main/.github/swf/cardjitsu_snowplayerselectbeta.swf) both need to be in `/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/windows/`.

- [cjsnow_uiassetsbeta.swf](https://github.com/Lekuruu/snowflake/raw/main/.github/swf/cjsnow_uiassetsbeta.swf) and [cjsnow_playerselectassetsbeta.swf](https://github.com/Lekuruu/snowflake/raw/main/.github/swf/cjsnow_playerselectassetsbeta.swf) both need to be in `/game/mpassets/minigames/cjsnow/en_US/deploy/swf/ui/assets/`.

## Troubleshooting

If something went wrong, you will most likely see this screen pop up:

![image](https://raw.githubusercontent.com/Lekuruu/snowflake/main/.github/screenshots/troubleshooting.png)

There are many reasons why this could be happening.
Here are some basic things to check:

1. Ensure that port 7002 is accessible from the outside

2. Check if your `crossdomain.xml` is accessible under `<your_play_url>/crossdomain.xml`

3. Ensure you set the right media url in the `.env`

4. Ensure your copies of houdini and dash are up-to-date

### Issues with policy file requests

There have been multiple users experiencing issues with flash's policy file requests (e.g. in [here](https://github.com/Lekuruu/snowflake/issues/42)).
This might be resolved, by setting `ENABLE_POLICY_SERVER` to `True` in your `.env` file.

### HTTPS-only Servers

You might want to check if your server is `https` only, i.e. only allowing secure ssl connections. If that is the case, you need to replace the `flash_client_base_fp11.swf` inside `/game/mpassets/playclients/r3662/` with [this file](https://github.com/Lekuruu/snowflake/raw/main/.github/swf/flash_client_base_fp11.swf).

---

Feel free to contact me on Discord (@lekuru), or per E-Mail ([contact@lekuru.xyz](mailto:contact@lekuru.xyz)), for further support.