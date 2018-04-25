"""Main Script for the Kodiot Plugin."""
#!/usr/bin/python
# -*- coding: utf-8 -*-

import logging

import xbmc
import xbmcaddon

from lib.paho import mqtt
from lib.paho.mqtt import client


ADDON = xbmcaddon.Addon()
__version__ = ADDON.getAddonInfo('version')

# need to write a kodi log handler perhaps also log to mqtt topic
LOG = logging.getLogger(__name__)


def main():
    """Main Program."""
    LOG.info('Launching Kodiot %s, MQTT version %s', __version__,
             mqtt.__version__)
    xbmc.log('Launching Kodiot %s, MQTT version %s' % (__version__, mqtt.__version__), xbmc.LOGDEBUG)
    while True:
    	pass


if __name__ == '__main__':
    main()
