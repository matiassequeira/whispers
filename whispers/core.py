import re
import os

from pathlib import Path

from whispers.log import debug
from whispers.secrets import WhisperSecrets
from whispers.utils import load_yaml_from_file
from shutil import copy2
from random import seed
from random import randint


def load_config(configfile, src="."):
    configfile = Path(configfile)
    if not configfile.exists():
        debug(f"{configfile} does not exist")
        raise FileNotFoundError

    if not configfile.is_file():
        debug(f"{configfile} is not a file")
        raise TypeError

    config = load_yaml_from_file(configfile)

    # Ensure minimal expected config structure
    if "exclude" not in config:
        config["exclude"] = {"files": [], "keys": [], "values": []}
    else:
        for idx in ["files", "keys", "values"]:
            if idx not in config["exclude"]:
                config["exclude"][idx] = []
    if "include" not in config:
        config["include"] = {"files": ["**/*"]}
    elif "files" not in config["include"]:
        config["include"]["files"] = ["**/*"]

    # Glob excluded files
    exfiles = []
    for fileglob in config["exclude"]["files"]:
        for filepath in Path(src).glob(fileglob):
            exfiles.append(filepath)
    config["exclude"]["files"] = exfiles

    # Compile regex from excluded keys and values
    for param in ["keys", "values"]:
        excluded = []
        for item in config["exclude"][param]:
            excluded.append(re.compile(item, flags=re.IGNORECASE))
        config["exclude"][param] = excluded

    # Optional: rules
    if "rules" not in config:
        config["rules"] = {}

    return config


def run(src: str, config=None, dst=None):
    source= src
    src = Path(src)
    if not src.exists():
        debug(f"{src} does not exist")
        raise FileNotFoundError

    if src.is_file():
        files = [src.as_posix()]
    elif src.is_dir():
        files = []
    else:
        debug(f"{src} is neither a file nor a directory")
        raise TypeError

    # Configure execution
    if not config:
        configpath = Path(__file__).parent
        configfile = configpath.joinpath("config.yml").as_posix()
        config = load_config(configfile, src=src)

    # Include files
    for incfile in config["include"]["files"]:
        files += set(src.glob(incfile))

    # Exclude files
    files = list(set(files) - set(config["exclude"]["files"]))

    if dst and not os.path.isdir(dst):
        os.mkdir(dst)

    # Scan files
    whispers = WhisperSecrets(config)
    for filename in files:
        # print(filename)
        try:
            for secret in whispers.scan(filename):
                if secret:
                    if dst: save_file(filename, dst)
                    yield secret
        except Exception as e:
            print(f"Error: {e}")

def save_file(filepath, dst):
    seed(1)
    original_filepath= filepath
    filename= os.path.basename(filepath)
    try:
        new_filepath= os.path.join(dst, filename)
        # Avoid collision of files with same name by adding three random numbers at the end
        while os.path.exists(new_filepath):
            filename=str(filename)+'_'+str(randint(100, 999))
            new_filepath= os.path.join(dst, filename)
        copy2(original_filepath, new_filepath)
    except Exception as e:  
        print(f"Error saving file: {e}") 