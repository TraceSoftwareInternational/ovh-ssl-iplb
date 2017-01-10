#!/usr/bin/env python
# -*- encoding: utf-8 -*-

import logging
import os
import sys
from time import sleep
from ovh_interface import DnsManager, LoadBalancerSSLManager

####################################################
# Static init
####################################################

logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())

if os.getenv('DEBUG'):
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)

####################################################
# End Static init
####################################################


def deploy_challenge(domain, txt_challenge):
    """
    Deploy the DNS challenge
    :param domain:  The domain where DNS challenge will be witten
    :param txt_challenge: The token value
    """

    logger.info('Deploy challenge for {}'.format(domain))

    dns_manager = DnsManager.DnsManager()
    dns_records = dns_manager.create_txt_entry(domain, txt_challenge)

    with open('.idRecord', 'w') as tempfile:
        tempfile.write(str(dns_records['id']))

    logger.info('Waiting period, DNS propagation for {}'.format(domain))
    sleep(30)


def clean_challenge(domain):
    """
    Clean the previous DNS challenge
    :param domain:  The domain where DNS challenge will be deleted
    """

    logger.info('Clean challenge for {}'.format(domain))

    with open('.idRecord', 'r') as tempfile:
        id_records = tempfile.readline()
    os.remove('.idRecord')

    dns_manager = DnsManager.DnsManager()
    dns_manager.delete_entry(domain, id_records)


def deploy_cert(domain, private_key, certificate, chain=None):
    """
    Deploy the previously generated certificate IN the IPLB
    :param domain: The domain where the certificate will be deploy
    :param private_key: The private key of certificate you want to deploy
    :param certificate: The certificate you want to deploy
    :param chain: The chain of certificate you want to deploy
    """

    iplb_name = os.getenv('iplb_name')
    logger.info('Deploy certificate for {} in {}'.format(domain, iplb_name))
    lb_ssl_manager = LoadBalancerSSLManager.LoadBalancerSSLManager(ip_lb_name=iplb_name)
    lb_ssl_manager.update_certificate(domain=domain, certif_path=certificate, privatekey_path=private_key, chain_path=chain)


def unchanged_cert(args):
    logger.debug("Certificate was unchanged. args: {}".format(args))


def invalid_challenge(args):
    logger.error("Challenge is invalid! args: {}".format(args))
    with open('failedRenew.log', 'a') as failedDomain:
        failedDomain.write('{}\n'.format(args[1]))


def main(argv):
    """
    Entry point of the hook
    :param argv: The command line args
    """

    logger.debug("Ovh hook executing: {}".format(argv))

    if argv[0] == 'deploy_challenge':
        deploy_challenge(domain=sys.argv[2], txt_challenge=sys.argv[4])
    elif argv[0] == 'clean_challenge':
        clean_challenge(domain=sys.argv[2])
    elif argv[0] == 'deploy_cert':
        deploy_cert(domain=argv[1], private_key=argv[2], certificate=argv[3], chain=argv[4])
    elif argv[0] == 'unchanged_cert':
        unchanged_cert(argv)
    elif argv[0] == 'invalid_challenge':
        invalid_challenge(argv)
    else:
        logger.fatal("Operation not managed: {0}".format(argv[0]))


if __name__ == '__main__':
    main(sys.argv[1:])
