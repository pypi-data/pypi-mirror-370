from robotooter import RoboTooter


def run_configure(rt: RoboTooter) -> None:
    # Make sure it doesn't already exist
    if rt.is_configured:
        print("It looks like the configuration already exists. Exiting")
        return

    rt.save_configuration()
    print(f"Configuration saved to {rt.config.working_directory}")
