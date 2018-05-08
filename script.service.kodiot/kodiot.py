"""Main Script for the Kodiot Plugin."""
#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import logging
import ssl

import xbmc
import xbmcaddon

from lib.paho import mqtt
from lib.paho.mqtt import client


class XbmcHandler(logging.Handler):

    """Logging Handler to integrate built-in logging package with xbmc's.
    """

    def emit(self, record):
        """Write the record to xbmc log system.
        """
        try:
            msg = self.format(record)
            xbmc.log(msg)
        except StandardError:
            self.handleError(record)


LOG = logging.getLogger(__name__)
LOG.setLevel(logging.DEBUG)
LOG.addHandler(XbmcHandler())


class Kodiot(xbmc.Monitor):

    """Kodiot Add on Abstraction."""

    def __init__(self):
        self.addon = xbmcaddon.Addon()

    def onSettingsChanged(self):
        """Called when addon settings are changed."""
        LOG.info('Kodiot: Settings changed')

    @property
    def version(self):
        """Return the version of this Addon."""
        return self.addon.getAddonInfo('version')

    @property
    def host(self):
        """Return the host setting."""
        return self.addon.getSetting('host').strip()

    @property
    def port(self):
        """Return the port setting."""
        return int(self.addon.getSetting('port').strip())

    @property
    def root_ca(self):
        """Return the Root CA cert path."""
        return self.addon.getSetting('cacrt').strip()

    @property
    def pem(self):
        """Return the PEM file path."""
        return self.addon.getSetting('pem').strip()

    @property
    def key(self):
        """Return the Client Private Key path."""
        return self.addon.getSetting('key').strip()

    @property
    def keepalive(self):
        """Return the keepalive setting."""
        return float(self.addon.getSetting('keepalive').strip())

    def on_connect(self, mqtt, userdata, flags, rc):
        """MQTT on connect callback function implementation."""
        LOG.info('on_connect: %s', client.connack_string(rc))
        # listen on this topic for state updates
        mqtt.subscribe('$aws/things/kodi/shadow/update/delta', qos=1)
        # publish on '$aws/things/kodi/shadow/update' topic to report state

    def on_disconnect(self, mqtt, userdata, rc):
        """MQTT on disconnect callback function implementation."""
        if rc != 0:
            LOG.info('on_disconnect: Unexpected disconnection.')

    def on_subscribe(self, mqtt, userdata, mid, granted_qos):
        """MQTT on subscribe callback function implementation."""
        LOG.info('on_subscribe: mid: %s QoS: %s', mid, granted_qos)

    def on_message(self, mqtt, userdata, message):
        """MQTT on message callback function implementation."""
        LOG.info('on_message: topic: %s payload: %s', message.topic,
                 message.payload)
        if message.topic == '$aws/things/kodi/shadow/update/delta':
            payload = json.loads(message.payload)
            result = xbmc.executeJSONRPC(json.dumps(payload['state']))
            result = json.dumps({'state': {'reported':result, 'desired':None}})
            LOG.info(result)
            msginfo = mqtt.publish('$aws/things/kodi/shadow/update', result, qos=1)
            if msginfo.rc != 0:
                LOG.info('problem publishing to shadow %s.', str(msginfo))


def main():
    """Main Program."""
    kodiot = Kodiot()
    LOG.info('Launching Kodiot %s, MQTT version %s', kodiot.version,
             mqtt.__version__)

    mqttc = client.Client()
    mqttc.on_connect = kodiot.on_connect
    mqttc.on_disconnect = kodiot.on_disconnect
    mqttc.on_subscribe = kodiot.on_subscribe
    mqttc.on_message = kodiot.on_message
    mqttc.tls_set(kodiot.root_ca, certfile=kodiot.pem, keyfile=kodiot.key,
                  cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)

    # Connect with MQTT Broker
    mqttc.connect(kodiot.host, kodiot.port, kodiot.keepalive)
    mqttc.loop_start()

    while not kodiot.waitForAbort(1.0):
        pass

    mqttc.loop_stop()

if __name__ == '__main__':
    main()
