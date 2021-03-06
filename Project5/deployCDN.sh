#!/bin/bash

make -f Makefile

# Arguments Parssing
while getopts "p:o:n:u:i:" arg
do
    case $arg in
        p)
            port=$OPTARG
            ;;
        o) 
            origin=$OPTARG
            ;;
        n)
	       name=$OPTARG
	       ;;
	u)
            username=$OPTARG
            ;;
        i)
            keyfile=$OPTARG
            ;;
        ?)
            echo "./deployCDN -p <port> -o <origin> -n <name> -u <username> -i <keyfile>"
	      exit 1
            ;;
        esac
done

# Http Replica Server List
# N. Virginia
REPLICA_SERVER_LIST[0]="ec2-54-85-32-37.compute-1.amazonaws.com"
# N. California
REPLICA_SERVER_LIST[1]="ec2-54-193-70-31.us-west-1.compute.amazonaws.com"
# Oregon
REPLICA_SERVER_LIST[2]="ec2-52-38-67-246.us-west-2.compute.amazonaws.com"
# Ireland
REPLICA_SERVER_LIST[3]="ec2-52-51-20-200.eu-west-1.compute.amazonaws.com"
# Frankfurt
REPLICA_SERVER_LIST[4]="ec2-52-29-65-165.eu-central-1.compute.amazonaws.com"
# Tokyo
REPLICA_SERVER_LIST[5]="ec2-52-196-70-227.ap-northeast-1.compute.amazonaws.com"
# Singapore
REPLICA_SERVER_LIST[6]="ec2-54-169-117-213.ap-southeast-1.compute.amazonaws.com"
# Sydney
REPLICA_SERVER_LIST[7]="ec2-52-63-206-143.ap-southeast-2.compute.amazonaws.com"
# Sao Paulo
REPLICA_SERVER_LIST[8]="ec2-54-233-185-94.sa-east-1.compute.amazonaws.com"


# Deploy HTTP code and executable file to Replica Servers
for server in "${REPLICA_SERVER_LIST[@]}"
do
    ssh -i $keyfile $username@$server 'mkdir ~/HTTP_JonRit_Test/'
    scp -i $keyfile httpserver.py $username@$server:~/HTTP_JonRit_Test/
    scp -i $keyfile httpserver $username@$server:~/HTTP_JonRit_Test/

done

# Deploy DNS code and executable file to Replica Servers
DNS_SERVER_DOMAIN=cs5700cdnproject.ccs.neu.edu
ssh -i $keyfile $username@$DNS_SERVER_DOMAIN 'mkdir ~/DNS_JonRit_Test'
scp -i $keyfile dnsserver $username@$DNS_SERVER_DOMAIN:~/DNS_JonRit_Test/
ssh -i $keyfile $username@$DNS_SERVER_DOMAIN "sh -c 'cd ~/DNS_JonRit_Test/; wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz; gunzip GeoLite2-City.mmdb'"
#ssh -i $keyfile $username@$DNS_SERVER_DOMAIN 'wget http://geolite.maxmind.com/download/geoip/database/GeoLite2-City.mmdb.gz'
#ssh -i $keyfile $username@$DNS_SERVER_DOMAIN 'gunzip GeoLite2-City.mmdb'
#scp -i $keyfile DNS_Server.cpp $username@$DNS_SERVER_DOMAIN:~/DNS_JonRit_Test/
#scp -i $keyfile CDNSServer.cpp $username@$DNS_SERVER_DOMAIN:~/DNS_JonRit_Test/
#scp -i $keyfile CDNSServer.h $username@$DNS_SERVER_DOMAIN:~/DNS_JonRit_Test/
#scp -i $keyfile maxminddb.h $username@$DNS_SERVER_DOMAIN:~/DNS_JonRit_Test/
#scp -i $keyfile maxminddb_config.h $username@$DNS_SERVER_DOMAIN:~/DNS_JonRit_Test/
#scp -i $keyfile libmaxminddb.a $username@$DNS_SERVER_DOMAIN:~/DNS_JonRit_Test/
