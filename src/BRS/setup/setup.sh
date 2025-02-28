#!/bin/bash


apt-get update
apt-get install -y curl libsane
apt-get clean

echo "setting up interface:"
subnet=$(echo $IPADDRESS | sed 's/\([0-9]*\.[0-9]*\.\)[0-9]*\.[0-9]*/\1/')
interface=$(ip addr show | grep -B10 $subnet | grep mtu | tail -1 | sed 's/[0-9]*: \(.*\): .*/\1/')
sed -i 's/^eth=.*//' /opt/brother/scanner/brscan-skey/brscan-skey.config
# if found an interface for scanner subnet. Will use this to contact scanner.
if [[ -z "$interface" ]]; then
	# if scanner subnet (roughly) not found in interfaces, assuming network_mode="host" is not set and using Docker default interface. 
	interface="eth0"
fi
echo "eth=$interface" >> /opt/brother/scanner/brscan-skey/brscan-skey.config
echo "using interface: $interface"
echo "-----"

echo "setting up host IP:"
sed -i 's/^ip_address=.*//' /opt/brother/scanner/brscan-skey/brscan-skey.config
if [[ -z "$HOST_IPADDRESS" ]]; then
	echo "no host IP configured, using default discovery"
else
	echo "ip_address=$HOST_IPADDRESS" >> /opt/brother/scanner/brscan-skey/brscan-skey.config
fi
echo "-----"

echo "whole config:"
cat /opt/brother/scanner/brscan-skey/brscan-skey.config
echo "-----"
# Install packages with force-all flag for potential conflicts
dpkg -i --force-all "brscan3-0.2.13-1.amd64.deb"
dpkg -i --force-all "brscan-skey-0.3.2-0.amd64.deb"



# Configure brscan3 (assuming correct arguments)
brsaneconfig3 -a name=phuc model=MFC-795CW ip=192.168.173.016

# Remove nrscan3

brsaneconfig3 -r NAME
# Run brscan-skey
brscan-skey

