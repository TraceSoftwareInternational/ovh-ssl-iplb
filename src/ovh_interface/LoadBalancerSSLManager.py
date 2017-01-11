#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import ovh
import re
from pathlib import Path
from ovh_interface.InterfaceBase import InterfaceBase


class LoadBalancerSSLManager(InterfaceBase):
    """
    Class which manage SSL in ovh IPLB
    """

    def __init__(self, ip_lb_name, ovh_client=None):
        """
        Constructor
        :type ip_lb_name: The name of ip LB you want to work with
        :param ovh_client: the obvh client you want to use. If none use environment variable to initialize the ovh client.
        """
        InterfaceBase.__init__(self, ovh_client)
        self.ip_lb_name = ip_lb_name

    def get_certificate_managed_by_ip_lb(self):
        """
        Get certificate managed by IP load balancer
        :return: list of dict {ip_lb_name, ssl_id_in_lb, ssl_cn}
        """

        self.logger.debug('List certificate in IP LB')
        regex_parse_ovh_ssl_config = r"/CN=([\w\d\.]+)"

        list_of_ssl_ip_lb_entry = []

        for ip_lb_name in self.ovh_client.get('/ipLoadbalancing'):
            if self.ip_lb_name == ip_lb_name:
                for ssl_id in self.ovh_client.get('/ipLoadbalancing/{}/ssl'.format(ip_lb_name)):
                    ssl_config = self.ovh_client.get('/ipLoadbalancing/{}/ssl/{}'.format(ip_lb_name, ssl_id))
                    matches = re.findall(regex_parse_ovh_ssl_config, ssl_config['subject'])
                    if len(matches) != 0:
                        list_of_ssl_ip_lb_entry.append({
                            "ip_lb_name": ip_lb_name,
                            "ssl_id": ssl_id,
                            "ssl_cn": matches[0]}
                        )

        self.logger.debug('SSL certif in IPLB : {}'.format(list_of_ssl_ip_lb_entry))
        return list_of_ssl_ip_lb_entry

    def _add_certificate(self, certif, privatekey, chain=None):
        """
        Add a certificate in the current ip lb
        :param certif: The content of
        :param privatekey:
        :param chain:
        :return: The certificate entry created or None if an error occurred
        """

        try:
            result = self.ovh_client.post('/ipLoadbalancing/{}/ssl'.format(self.ip_lb_name),
                                          certificate=certif.strip(),
                                          key=privatekey.strip(),
                                          chain=chain.strip()
                                          )
        except (ovh.exceptions.BadParametersError, ovh.exceptions.ResourceConflictError) as err:
            self.logger.error('Impossible to add certificate. err: {}'.format(err))
            return None

        return result

    def _get_ssl_id_from_domain(self, domain):
        """
        Get all ssl id of certificate found for a domain
        :param domain: The domain you want to search ssl associated with
        :return: List of ssl id
        """
        list_of_ssl_ip_lb_entry = self.get_certificate_managed_by_ip_lb()
        return (ssl_ip_lb_entry['ssl_id'] for ssl_ip_lb_entry in list_of_ssl_ip_lb_entry if ssl_ip_lb_entry['ssl_cn'] == domain)

    def _delete_certificate(self, list_of_ssl_id):
        """
        Delete a SSL certificates
        :param list_of_ssl_id: list of ssl entry you want to delete
        """

        for ssl_id in list_of_ssl_id:
            self.logger.debug("Delete SSL certif {}".format(ssl_id))
            self.ovh_client.delete('/ipLoadbalancing/{serviceName}/ssl/{id}'.format(serviceName=self.ip_lb_name, id=ssl_id))

    def update_certificate(self, domain, certif_path, privatekey_path, chain_path=None):
        """
        Update a certificate in the current ip lb
        :param domain: The domain you want to update
        :param certif_path: The path to the certificate you want to add
        :param privatekey_path: The path to the private key you want to add
        :param chain_path: The path to the  chain you want to add
        :return: True if success else False
        """

        self.logger.info("Update the certificate of {}".format(domain))
        self.logger.debug("certif: {}\nprivatekey:{}\nchain: {}".format(certif_path, privatekey_path, chain_path))

        if not Path(certif_path).is_file() or not Path(privatekey_path).is_file():
            self.logger.error("Impossible to update the certificate of {} some files doesn't exist".format(domain))
            return False

        if chain_path is not None and not Path(chain_path).is_file():
            self.logger.error("Impossible to update the certificate of {} some chain file doesn't exist {}".format(domain, chain_path))
            return False

        with open(certif_path, 'r') as content_file:
            certif = content_file.read()

        with open(privatekey_path, 'r') as content_file:
            privatekey = content_file.read()

        if chain_path:

            with open(chain_path, 'r') as content_file:
                chain = content_file.read()

        else:
            chain = None

        list_of_ssl_id_to_delete = self._get_ssl_id_from_domain(domain)

        self.logger.info('Add certificate for domain : {}'.format(domain))
        if self._add_certificate(certif, privatekey, chain) is None:
            return False

        self.logger.debug('Delete certificate for domain {}'.format(domain))
        self._delete_certificate(list_of_ssl_id_to_delete)
        return True
