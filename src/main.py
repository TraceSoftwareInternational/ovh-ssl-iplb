#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from ovh_interface.DnsManager import DnsManager
from ovh_interface.LoadBalancerSSLManager import LoadBalancerSSLManager
import os
import logging
import subprocess
from typing import List
import argparse

####################################################
# Static init
####################################################

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

if os.getenv('DEBUG'):
    logger.setLevel(logging.DEBUG)
    logger.debug("DEBUG MODE".center(100, '-'))
else:
    logger.setLevel(logging.INFO)

####################################################
# End Static init
####################################################


def renew_certificate(domain: str) -> bool:
    """
    Create/Renew the certificate for domain passed in arg
    :param domain: The domain you want to get the ssl certificate
    :return: True if certificated getted and added in IP LB with success
    """

    logger.info("Renew certificate for {}".format(domain))
    command_result = subprocess.run(args=['dehydrated', '-c', '-d', domain, '-k', './ovhDnsHook.py', '-t', 'dns-01'], stdout=subprocess.PIPE)
    return True if command_result.returncode == 0 else False


def parse_command_line() -> List[str]:
    """
    Parse the command line and extract list of domain passed in param
    :return: list of domain you want to add SSL certif in IPLB
    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--domain", action='append', help="Domain you want to get the certificate and add it in the IP-LB")

    args = parser.parse_args()
    if args.domain:
        return args.domain
    else:
        return []


if __name__ == '__main__':

    ip_lb_name = os.getenv('iplb_name')
    input_domain_list = parse_command_line()

    if os.getenv('DEBUG'):
        with open('/etc/dehydrated/config', 'a') as config:
            config.write('CA="https://acme-staging.api.letsencrypt.org/directory"\n')

    loadBalancerUpdaterSSL = LoadBalancerSSLManager(ip_lb_name=ip_lb_name)

    list_of_ssl_ip_lb_entry = loadBalancerUpdaterSSL.get_certificate_managed_by_ip_lb()
    domains_from_iplb = [ssl_ip_lb_entry['ssl_cn'] for ssl_ip_lb_entry in list_of_ssl_ip_lb_entry]
    all_domains_to_get_certif = domains_from_iplb + list(set(input_domain_list) - set(domains_from_iplb))

    dnsManager = DnsManager()
    list_dns_zone = dnsManager.get_dns_zone_manageable()
    list_of_updatable_domain = set([domain for domain in all_domains_to_get_certif if '.'.join(domain.split('.')[1:]) in list_dns_zone])

    logger.info("List of domain will be updated: {}".format(list_of_updatable_domain))

    for ssl_certif_updatable in list_of_updatable_domain:
        renew_certificate(ssl_certif_updatable)

    for retry_count in range(os.getenv('max_retry', 5)):

        if not os.path.exists('failedRenew.log'):
            break

        with open('failedRenew.log', 'r') as failedDomain:
            domains = failedDomain.readlines()
        os.remove('failedRenew.log')

        logger.info("Domain retry (count: {}): {}".format(retry_count+1, domains))
        for domain in domains:
            renew_certificate(domain)
