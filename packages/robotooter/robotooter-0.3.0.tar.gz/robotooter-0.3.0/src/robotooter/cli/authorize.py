from robotooter import RoboTooter
from robotooter.bots.base_bot import BaseBot
from robotooter.cli.util import get_yes
from robotooter.mastodon.authenticator import Authenticator


def run_authorize(rt: RoboTooter, bot: BaseBot, force: bool=False) -> None:
    if not bot.config.username:
        raise RuntimeError("Username not set")
    authenticator = Authenticator(
        main_path=rt.config.working_directory,
        bot_path=bot.config.working_directory,
        full_username=bot.config.username,
    )

    if authenticator.bot_config_exists:
        if force or get_yes("Mastodon authentication file already exists. Do you want to replace it?"):
            authenticator.bot_config_path.unlink()
        else:
            print("Keeping current authentication settings.")
            return

    print("\nGreat! Now we will request an authorization URL.")
    auth_url = authenticator.get_auth_url()
    print("Here's your authorization URL:")
    print(auth_url)

    print("\nYou need to open that in a browser, make sure you're logged into Mastodon, and authorize")
    print("the application to user the account. It will give you a code, which you will enter here.")
    code = input("Enter authorization code: ")

    authenticator.log_in(code=code)

    print(f"Success! {bot.config.bot_name} should be set to toot up a storm.")
