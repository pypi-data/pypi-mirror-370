def get_yes(message: str) -> bool:
    response = input(f"{message.strip()} (y/n): ").lower().strip()
    return response != "" and response[0] == 'y'
