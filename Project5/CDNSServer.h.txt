#pragma once
#include <iostream>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <netdb.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <sys/epoll.h>
#include <errno.h>
#include <sys/socket.h>
#include <unistd.h>
#include <fcntl.h>
#include <netinet/tcp.h> 
#include "maxminddb.h"

// For Poll
#define MAX_EVENT_COUNTS 1024
#define BUFF_SIZE 1460

// Port Number Boundary
#define LOWEST_PORT 40000
#define HIGHEST_PORT 65535

// Server Lists
#define SERVER_ORIGINAL "54.88.98.7" // ec2-54-88-98-7.compute-1.amazonaws.com  Origin server (running Web server on port 8080)
#define SERVER_NORTH_VIRGINIA "54.85.32.37" // ec2-54-85-32-37.compute-1.amazonaws.com         N. Virginia
#define SERVER_NORTH_CALIFORNIA "54.193.70.31" // ec2-54-193-70-31.us-west-1.compute.amazonaws.com        N. California
#define SERVER_OREGON "52.38.67.246" // ec2-52-38-67-246.us-west-2.compute.amazonaws.com        Oregon
#define SERVER_IRELAND "52.51.20.200" // ec2-52-51-20-200.eu-west-1.compute.amazonaws.com        Ireland
#define SERVER_FRANKFURT "52.29.65.165" // ec2-52-29-65-165.eu-central-1.compute.amazonaws.com     Frankfurt
#define SERVER_TOKYO "52.196.70.227" // ec2-52-196-70-227.ap-northeast-1.compute.amazonaws.com  Tokyo
#define SERVER_SINGAPORE "54.169.117.213" // ec2-54-169-117-213.ap-southeast-1.compute.amazonaws.com Singapore
#define SERVER_SYDNEY "52.63.206.143" // ec2-52-63-206-143.ap-southeast-2.compute.amazonaws.com  Sydney
#define SERVER_SAO_PAULO "54.233.185.94" // ec2-54-233-185-94.sa-east-1.compute.amazonaws.com       Sao Paulo


// 
enum REPLICA_SERVERS
{
	RS_VIRGINIA         = 0,
	RS_NORTH_CALIFORNIA,
	RS_OREGON,
	RS_IRELAND,
	RS_FRANKFURT,
	RS_TOKYO,
	RS_SINGAPORE,
	RS_SYDNEY,
	RS_SAO_PAULO,
	RS_MAX,
};

#define REPLICA_SERVER_COUNTS 9

struct Replica_Measurement
{
	time_t iLatency[RS_MAX];
	__uint16_t uiPort;
};

struct Physical_Location
{
	double fLatitude;
	double fLongitude;
};


// DNS_QUERY_TYPE
#define TYPE_A 1 // Ipv4 Address
#define TYPE_NS 2 // NameServer
#define TYPE_CNAME 5 // Canonical Name
#define TYPE_SOA 6 // Start of authority zone 
#define TYPE_DOMAIN_NAME_PTR 12 // Domain Name Pointer 
#define TYPE_MX 15 // Mail Server

// DNS Header Structure
struct DNS_HEADER
{
	__uint16_t uiID; // identification number
 
	__uint8_t RD : 1; // 0 = Recursion not desired, 1 = Recursion desired
	__uint8_t TC : 1; // 0 = Not trauncated, 1 = Message truncated
	__uint8_t AA : 1; // 0 = No Authoritative, 1 = Is Authoritative
	__uint8_t Opcode : 4; // 0 = Standard Query, 1 = Inverse Query, 2 = Server Status Request, 4 = Notify, 5 = Update
	__uint8_t QR : 1; // 0 = Query / 1 = Response 
 
	__uint8_t Rcode : 4; // Response Code
	__uint8_t CD : 1; // Checking Disabled.
	__uint8_t AD : 1; // Authenticated Data
	__uint8_t Z : 1; // Reserved
	__uint8_t RA : 1; // Recursive Query Support, 0 = not Available, 1 = Available
 
	__uint16_t uiTotal_Questions; // Number of entries in the question list that were returned
	__uint16_t uiTotal_Answer_RRs; // Number of entries in the answer resource record list that were returned.
	__uint16_t uiTotal_Authority_RRs; // Number of entries in the authority resource record list that were returned.
	__uint16_t uiTotal_Additional_RRs; // Number of entries in the additional resource record list that were returned.
};

struct DNS_QUESTION
{
	__uint16_t uiType;
	__uint16_t uiClass;
};
 

#pragma pack(push, 1)
struct R_DATA
{
	__uint16_t uiType;
	__uint16_t uiClass;
	__uint32_t uiTTL;
	__uint16_t uiRdataLength;
};
#pragma pack(pop)
 
struct RESOURCE_RECORD
{
	__uint8_t* pName;
	struct R_DATA* pResource;
	__uint8_t* pRdata;
};
 
struct DNS_QUERY
{
	__uint8_t* pName;
	struct QUESTION* pQuestion;
};

class CDNSServer
{
public:
	CDNSServer(__uint16_t uiPort_, char* szCDNName_);
	~CDNSServer();
	
private:
	std::string m_strURL; // URL for which a Client requests a translation to an IP Address
	std::string m_strCDNName; // the CDN-specific name that this server translates to an IP.
	std::string m_strCDNNameDNSFormat; // 3www6google3com
	
	__uint16_t m_uiIDforDNSQuery; // ID of a DNS Query that a client sent to this server
	
	// Server Socket
	int m_iUDPSocketFD; // Server UDP Port 
	__uint16_t m_uiUDPServerPort; // Server Port 
	struct sockaddr_in m_stServerUDPSockAddr; // for binding
	
	// For EPoll
	int m_iEPollFD;
	
	// Packet Buffer
	unsigned char m_szSendBuff[BUFF_SIZE]; // for sending
	unsigned char m_szRecvBuff[BUFF_SIZE]; // for receiving
	
	// Replica Servers
	std::string m_strServerList[RS_MAX];
	int m_iReplicaFD[RS_MAX];
	bool m_bConnected[RS_MAX];
	struct Physical_Location m_stServerLocation[RS_MAX];
	struct sockaddr_in m_stReplicaSockAddr[RS_MAX];
	MMDB_s m_GeoIPDB;

public:
	bool InitServer(); // Initialize the Server
	bool CreateSocket(); // Create and Bind a Socket
	bool InitEPoll(); // Create EPoll and Register the Socket
	bool RunServer(); // Communicate with Clients
	int BuildDNSReponse(); // Build up a DNS Response corresponding to a Query from a Client
	int BuildDNSResponse(unsigned char* szRecvData_, unsigned char* szSendData_, const struct sockaddr *const pSockaddr_); // Build up a DNS Response corresponding to a Query from a Client
	void ConvertURLtoDNSName(char* szDNS_, char* szURL_); // Convert a URL into a DNS Name Format ( www.facebook.com -> 3www8facebook3com)
	void Display_Error_Message(const char* szErrorMessage_); // Print out an Error Message
	int SelectBestServer(double fLatitude_, double fLongitude_);
	bool InitGeoIPDatabase();
};

