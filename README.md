# Automatic generation of Let's Encrypt certificate on OVH IP LoadBalancer Next gen 

This repo contains a way to generate SSL certificate (with Let's Encrypt) and add it automatically to your IPLB instance.
To do that, the domain you want to get SSL certificates must be managed by OVH.

## Usage

To use that tool, we provide an docker container [tracesoftware/ovh-ssl-iplb]().

To run it, you should just define some environments variables:
````
docker run -ti --rm -e application_key=XXXX -e application_secret=XXXX -e consumer_key=XXXX -e iplb_name=ip-XXXXXX tracesoftware/ovh-ssl-iplb
````

By default the tool will update the SSL certificate already present in the IPLB instance.

You can use the option `-d` to add a domain new domains in your IPLB.

````
docker run -ti --rm -e application_key=XXXX -e application_secret=XXXX -e consumer_key=XXXX -e iplb_name=ip-XXXXXX tracesoftware/ovh-ssl-iplb -d app.example.com -d app2.example.com
````

## Volumes

We expose some volumes in the docker container:

* `/etc/dehydrated/certs` which will contains SSL certificate
* `/etc/dehydrated/accounts` which will contains your Let's Encrypt account information

## Configuration

You must configure this script by setting some environments variables:

* `application_key`
    * Your OVH API application key
    * Optional: false
* `application_secret`
    * Your OVH API application secret
    * Optional: false
* `consumer_key`
    * Your OVH API consumer key
    * Optional: false
* `iplb_name`
    * The name of IPLB you want to manage SSL certificate
    * Optional: false
* `max_retry`
    * Number of retry can be perform for the validation of SSL certificate
    * Default value: `5`
    * Optional: true
* `DEBUG`
    * Define it to `True` if you want to print some extra informations and use the Let’s Encrypt staging server
    * Optional: true

To found `application_key`, `application_secret` and `consumer_key` you should check [this ovh documenation](https://api.ovh.com/g934.first_step_with_api) and [this page](https://api.ovh.com/createToken/).
Your credentials must have access to:

* list not defined yet
