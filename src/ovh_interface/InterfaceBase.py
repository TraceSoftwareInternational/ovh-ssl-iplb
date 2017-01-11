#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import ovh
import logging
import os


class InterfaceBase:
    """
    This class represent the base of each class in ovh_interface. I contains some utils object like logger and ovh_client
    """

    """
    The default logger for all subclass ;)
    """
    logger = None

    def __init__(self, ovh_client=None):
        """
        Constructor
        :param ovh_client: the ovh client you want to use. If none use environment variable to initialize the ovh client.
        """

        if ovh_client is None:
            self.ovh_client = ovh.Client(endpoint=os.getenv('endpoint', 'ovh-eu'),
                                         application_key=os.getenv('application_key'),
                                         application_secret=os.getenv('application_secret'),
                                         consumer_key=os.getenv('consumer_key')
                                         )
        else:
            self.ovh_client = ovh_client

        if not InterfaceBase.logger:
            InterfaceBase.logger = logging.getLogger('InterfaceBase')
            InterfaceBase.logger.addHandler(logging.StreamHandler())

            if os.getenv('DEBUG'):
                InterfaceBase.logger.setLevel(logging.DEBUG)
            else:
                InterfaceBase.logger.setLevel(logging.INFO)
            self.logger = InterfaceBase.logger
