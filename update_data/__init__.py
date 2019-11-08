import os
from setting import config

config = config.get(os.getenv('CONFIG_TYPE') or 'development')
