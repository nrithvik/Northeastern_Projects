#!/bin/bash

# Arguments Parssing
while getopts "p:o:n:u:i:" arg ; do
    case $arg in
        p)
            port=${OPTARG}
            ;;
        o)
            origin=${OPTARG}
            ;;
        n)
	    name=${OPTARG}
	    ;;
	u)
            username=${OPTARG}
            ;;
        i)
            keyfile=${OPTARG}
            ;;
        ?)
            echo "./runCDN -p <port> -o <origin> -n <name> -u <username> -i <keyfile>"
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


# Run the http server on Replica Servers
for server in "${REPLICA_SERVER_LIST[@]}"
do
    ssh -i $keyfile -n -f $username@$server  "sh -c 'cd ~/HTTP_JonRit_Test/; nohup ./httpserver -p $port -o $origin > /dev/null 2>&1 &'"

done

# Run the dns server on cs5700cdnproject.com
ssh -i $keyfile -n -f $username@cs5700cdnproject.ccs.neu.edu "sh -c 'cd ~/DNS_JonRit_Test/; nohup ./dnsserver -p $port -n $name > /dev/null 2>&1 &'"
