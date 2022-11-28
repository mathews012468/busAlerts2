with open("config.ini", "a") as config, open(".env") as env:
    for line in env:
        config.write("\nenv = " + line.strip())