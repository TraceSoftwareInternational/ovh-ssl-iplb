#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from ovh_interface.InterfaceBase import InterfaceBase


class DnsManager(InterfaceBase):
    """
    This class provide an easy object way to interact with OVH DNS API
    """

    def __init__(self, ovh_client=None):
        """
        Constructor
        :param ovh_client: the ovh client you want to use. If none use environment variable to initialize the ovh client.
        """
        InterfaceBase.__init__(self, ovh_client)

    def get_dns_zone_manageable(self):
        """
        Get all DNS zone which can be managed by the ovh api
        :return: The list of manageable DNS zone
        """
        return self.ovh_client.get('/domain/zone')

    @staticmethod
    def _split_create_domain_challenge(domain):
        """
        Split the domain to base domain / sub domain and add the let's encrypt domain challenge to the sub domain
        :param domain: The domain you want to split
        :return: The base domain and the sub domain
        """
        ndd = domain.split(".")
        if len(ndd) == 2:
            subdomain = "_acme-challenge"
            basedomain = ndd[0] + "." + ndd[1]
        else:
            subdomain = "_acme-challenge." + ndd[0]
            basedomain = ndd[1] + "." + ndd[2]

        return basedomain, subdomain

    def create_txt_entry(self, domain, value):
        """
        Create a TXT entry in a DNS zone
        :param domain: The domain where the DNS entry will be inserted
        :param value: The value which will be inserted
        :return: The DNS records created
        """

        basedomain, subdomain = self._split_create_domain_challenge(domain)

        dns_entry = self.ovh_client.post('/domain/zone/{}/record'.format(basedomain),
                                         fieldType="TXT",
                                         subDomain=subdomain,
                                         ttl=0,
                                         target=value
                                         )
        self.ovh_client.post('/domain/zone/{}/refresh'.format(basedomain))
        self.logger.info("DNS challenge was added for domain: {}".format(basedomain))
        self.logger.debug("{}.{} with value ({}) was written".format(subdomain, basedomain, value))

        return dns_entry

    def delete_entry(self, domain, id_record):
        """
        Delete a DNS entry
        :param domain: The domain where the entry you want to delete is present
        :param id_record: The record id you want to delete
        """

        basedomain, _ = self._split_create_domain_challenge(domain)
        self.ovh_client.delete('/domain/zone/{}/record/{}'.format(basedomain, id_record))
        self.ovh_client.post('/domain/zone/{}/refresh'.format(basedomain))

        self.logger.info("Clean DNS entry for domain: {}".format(basedomain))
        self.logger.debug("DNS entry {} in {} was deleted".format(id_record, basedomain))

