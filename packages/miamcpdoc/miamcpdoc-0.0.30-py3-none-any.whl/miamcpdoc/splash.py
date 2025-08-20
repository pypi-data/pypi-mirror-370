import os

def _get_splash():
    try:
        # Construct path to the splash file relative to this file
        dir_path = os.path.dirname(os.path.realpath(__file__))
        splash_path = os.path.join(dir_path, "ascii_art.txt")
        with open(splash_path, "r", encoding="utf-8") as f:
            return f.read()
    except FileNotFoundError:
        return "MCPDOC"  # Fallback splash

SPLASH = _get_splash()