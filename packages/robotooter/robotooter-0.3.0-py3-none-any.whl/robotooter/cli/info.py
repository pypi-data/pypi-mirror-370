from robotooter import RoboTooter


def run_info(rt: RoboTooter) -> None:
    print("RobotoTooter info")
    print(f"Version: {rt.__version__}")
    print(f"Root directory: {rt.config.working_directory}")

    if not rt.is_configured:
        print("It looks like things have not been set up yet.")
        return

    print("Filters:")
    for f in rt.filters.keys():
        print(f"  {f}")
    print("Tooters:")
    for t in rt.bots:
        print(f"  {t}")

