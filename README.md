# VPN Suite for Sakthi (Sandy) Santhosh's Website

This repository contains all the necessary scripts to automate the process of maintaining VPN for my website on AWS EC2 instance. To get started, apply the IaC in the [WireGuard Terraform](https://github.com/sakthisanthosh010303/wireguard-terraform-aws) project.

> **Note:** The Terraform script will take care of setting up the WireGuard server on your machine. If you don't use it, you need to set-up the server manually.

Once done, SSH into the machine and clone this repository. Create a virtual environment with the following command:

```bash
virtualenv -q ./venv/ && source ./venv/bin/activate && pip3 install -r ./requirements.txt -q
```

Create peers in your WireGuard server by using the following set of commands:

```bash
wg genkey | tee ./private.key | wg pubkey > ./public.key
```

This'll generate the public and private key for the peer you want to connect. Once done, add the peer to the WireGuard server using the following command:

```bash
wg-quick set <interface-name> peer <public-key> allowed-ips <client-tunnel-ip>
```

This'll add the client to the WireGuard server. Create a secrets file with the following command and fill-out the details:

```bash
cp ./assets/env.example ./assets/.env
```

Now, you need to fill out the details in `/assets/recipients.csv`. Also, change the public key of the server in `/assets/config_template.conf` file.  Once that's done, send an email to the respective people with the `/send_email.py` command.

## CRON Job

Add the DNS updater as a CRON job with the following command:

```
crontab -e
@reboot source <parent-directory>/venv/bin/activate && python3 <parent-directory>/dns_updater.py > <parent-directory>/dns.log 2>&1
```
