import logging

import discord 
import numpy as np
from environs import Env

logger = logging.getLogger(__name__)

def setup_logger(log_level):
    global logger
    logger.setLevel(log_level)
    ch = logging.StreamHandler()
    ch.setLevel(log_level)
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)

    logger.debug("Logging setup")

def main():
    env = Env()
    env.read_env()

    setup_logger(env.int('LOG_LEVEL', logging.INFO))
    

    

if __name__ == "__main__":
    main()