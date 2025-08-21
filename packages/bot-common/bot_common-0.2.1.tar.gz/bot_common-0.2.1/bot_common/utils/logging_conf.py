import logging

config = {
          'level': logging.DEBUG,
          'format': "%(levelname)s - %(asctime)s - %(name)s: %(message)s",
          'datefmt': '%Y-%m-%d %H:%M:%S'
         }

logger = logging.getLogger(__name__)
logging.basicConfig(**config)
