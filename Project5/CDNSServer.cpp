#include "CDNSServer.h"


// Set up Port Number and CDN-specifi Name
// Initialize Memory
CDNSServer::CDNSServer(__uint16_t uiPort_, char* szCDNName_)
{
	m_uiUDPServerPort = uiPort_;
	m_strCDNName = szCDNName_;
	
	char szTemp[256] = { 0, };
	char szCNDName[256] = { 0, };
	memcpy(szCNDName, m_strCDNName.c_str(), m_strCDNName.length());
	ConvertURLtoDNSName(szTemp, szCNDName);
	m_strCDNNameDNSFormat = szTemp;
	
	memset(&m_stServerUDPSockAddr, 0, sizeof(m_stServerUDPSockAddr));
	m_iEPollFD = -1;
	
	// Replica Servers
	m_strServerList[RS_VIRGINIA] = SERVER_NORTH_VIRGINIA;
	m_strServerList[RS_NORTH_CALIFORNIA] = SERVER_NORTH_CALIFORNIA;
	m_strServerList[RS_OREGON] = SERVER_OREGON;
	m_strServerList[RS_IRELAND] = SERVER_IRELAND;
	m_strServerList[RS_FRANKFURT] = SERVER_FRANKFURT;
	m_strServerList[RS_TOKYO] = SERVER_TOKYO;
	m_strServerList[RS_SINGAPORE] = SERVER_SINGAPORE;
	m_strServerList[RS_SYDNEY] = SERVER_SYDNEY;
	m_strServerList[RS_SAO_PAULO] = SERVER_SAO_PAULO;
	
	// Server Locations
	m_stServerLocation[RS_VIRGINIA].fLatitude = 39.018000;
	m_stServerLocation[RS_VIRGINIA].fLongitude = -77.539000;
	
	m_stServerLocation[RS_NORTH_CALIFORNIA].fLatitude = 37.339400;
	m_stServerLocation[RS_NORTH_CALIFORNIA].fLongitude  = -121.895000;
	
	m_stServerLocation[RS_OREGON].fLatitude = 45.778800;
	m_stServerLocation[RS_OREGON].fLongitude  = -119.529000;
	
	m_stServerLocation[RS_IRELAND].fLatitude = 53.333100;
	m_stServerLocation[RS_IRELAND].fLongitude  = -6.248900;
	
	m_stServerLocation[RS_FRANKFURT].fLatitude = 50.116700;
	m_stServerLocation[RS_FRANKFURT].fLongitude  = 8.683300;
	
	m_stServerLocation[RS_TOKYO].fLatitude = 35.685000;
	m_stServerLocation[RS_TOKYO].fLongitude  = 139.751400;
	
	m_stServerLocation[RS_SINGAPORE].fLatitude = 1.293100;
	m_stServerLocation[RS_SINGAPORE].fLongitude  = 103.855800;
	
	m_stServerLocation[RS_SYDNEY].fLatitude = -33.861500;
	m_stServerLocation[RS_SYDNEY].fLongitude  = 151.205500;
	
	m_stServerLocation[RS_SAO_PAULO].fLatitude = -23.547500;
	m_stServerLocation[RS_SAO_PAULO].fLongitude  = -46.636100;

	
	/////
	memset(m_iReplicaFD, -1, sizeof(m_iReplicaFD));
	memset(m_bConnected, 0, sizeof(m_bConnected));
	memset(&m_stReplicaSockAddr, 0, sizeof(m_stReplicaSockAddr));
	for (int i = 0; i < RS_MAX; ++i)
	{
		m_stReplicaSockAddr[i].sin_family = AF_INET;
		m_stReplicaSockAddr[i].sin_port = htons(m_uiUDPServerPort);
		inet_aton(m_strServerList[i].c_str(), &m_stReplicaSockAddr[i].sin_addr);
	}
}

// Close Socket
CDNSServer::~CDNSServer()
{
	close(m_iUDPSocketFD);
	MMDB_close(&m_GeoIPDB);
}

// Initialize the Server
bool CDNSServer::InitServer()
{
	if (false == CreateSocket())
		return false;
	
	if (false == InitEPoll())
		return false;
	
	if (false == InitGeoIPDatabase())
		return false;
	
	return true;
	//return (CreateSocket() && InitEPoll());
}

// Display an error message
void CDNSServer::Display_Error_Message(const char* szErrorMessage_)
{
	printf("Error : %s\n", szErrorMessage_);
}

// Create and Bind a Socket
bool CDNSServer::CreateSocket()
{
	m_iUDPSocketFD = socket(AF_INET, SOCK_DGRAM, IPPROTO_UDP);
	if (-1 == m_iUDPSocketFD)
	{
		Display_Error_Message("UDP Socket Creation Failed!");
		return false;
	}
	
	m_stServerUDPSockAddr.sin_family = AF_INET;
	m_stServerUDPSockAddr.sin_port = htons(m_uiUDPServerPort);
	m_stServerUDPSockAddr.sin_addr.s_addr = htonl(INADDR_ANY);
	
	int iResult = bind(m_iUDPSocketFD, (struct sockaddr*)&m_stServerUDPSockAddr, sizeof(m_stServerUDPSockAddr));
	if (-1 == iResult)
	{
		Display_Error_Message("UDP Socket Binding Failed!");
		return false;
	}
	
	int iFlags = fcntl(m_iUDPSocketFD, F_GETFL, 0);
	if (-1 == iFlags)
	{
		Display_Error_Message("UDP Socket fcntl F_GETFL Failed!");
		return false;
	}
	iFlags |= O_NONBLOCK;
	
	iResult = fcntl(m_iUDPSocketFD, F_SETFL, iFlags);
	if (-1 == iResult)
	{
		Display_Error_Message("UDP Socket fcntl F_SETFL Failed!");
		return false;
	}
	
	for (int i = 0; i < RS_MAX; ++i)
	{
		m_iReplicaFD[i] = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP);
		if (-1 == m_iReplicaFD[i])
		{
			Display_Error_Message("%dth Replica Server Socket Creation Failed!");
			return false;
		}
		
		// Nagle Algorithm Off
		int iOpt = 1;
		if (-1 == setsockopt(m_iReplicaFD[i], IPPROTO_TCP, TCP_NODELAY, &iOpt, sizeof(iOpt)))
		{
			Display_Error_Message("Replica Server Socket setsockopt Failed!");
			return false;
		}
		
		
		int iFlags = fcntl(m_iReplicaFD[i], F_GETFL, 0);
		if (-1 == iFlags)
		{
			Display_Error_Message("Replica Server Socket fcntl F_GETFL Failed!");
			return false;
		}
		iFlags |= O_NONBLOCK;
	
		iResult = fcntl(m_iReplicaFD[i], F_SETFL, iFlags);
		if (-1 == iResult)
		{
			Display_Error_Message("Replica Server Socket fcntl F_SETFL Failed!");
			return false;
		}
	}
	
	return true;
}

// Create EPoll and Register the Socket
bool CDNSServer::InitEPoll()
{
	m_iEPollFD = epoll_create1(0);
	if (-1 == m_iEPollFD)
	{
		Display_Error_Message("epoll_create1(0) Failed!");
		return false;
	}
	
	struct epoll_event event;
	memset(&event, 0, sizeof(event));
	// EPoll Edge Triggered Mode
	event.events = EPOLLIN | EPOLLET;
	event.data.fd = m_iUDPSocketFD;
	int iResult = epoll_ctl(m_iEPollFD, EPOLL_CTL_ADD, m_iUDPSocketFD, &event);
	if (-1 == iResult)
	{
		Display_Error_Message("epoll_ctl Failed!");
		return false;
	}
	
	return true;
	int iConnectedServerCounts = 0;
	int iIndex = 0;
	do
	{
		if (iIndex >= RS_MAX)
			iIndex = 0;
			
		if (false == m_bConnected[iIndex])
		{
			iResult = connect(m_iReplicaFD[iIndex], (struct sockaddr*)&m_stReplicaSockAddr[iIndex], sizeof(m_stReplicaSockAddr[iIndex]));
			if (0 == iResult)
			{
				m_bConnected[iIndex] = true;
				++iConnectedServerCounts;
			}
		}
		
		++iIndex;
	} while (iConnectedServerCounts < RS_MAX);
	
	for (int i = 0; i < RS_MAX; ++i)
	{
		memset(&event, 0, sizeof(event));
		// EPoll Edge Triggered Mode
		event.events = EPOLLIN | EPOLLET;
		event.data.fd = m_iReplicaFD[i];
		iResult = epoll_ctl(m_iEPollFD, EPOLL_CTL_ADD, m_iReplicaFD[i], &event);
		if (-1 == iResult)
		{
			Display_Error_Message("epoll_ctl Failed!");
			return false;
		}
	}
	
	return true;
}

// Communicate with Clients
bool CDNSServer::RunServer()
{
	struct epoll_event stEPollEvents[MAX_EVENT_COUNTS];
	memset(stEPollEvents, 0, sizeof(stEPollEvents));
	
	do
	{
		int iEventCounts = epoll_wait(m_iEPollFD, stEPollEvents, MAX_EVENT_COUNTS, -1);
		for (int i = 0; i < iEventCounts; ++i)
		{
			if ((EPOLLERR & stEPollEvents[i].events)
				|| (EPOLLHUP & stEPollEvents[i].events)
				|| !(EPOLLIN & stEPollEvents[i].events))
			{
				close(stEPollEvents[i].data.fd);
			}
			else if (stEPollEvents[i].data.fd == m_iUDPSocketFD)
			{
				struct sockaddr_in stSockAddr;
				memset(&stSockAddr, 0, sizeof(stSockAddr));
				socklen_t iSockLength = sizeof(stSockAddr);
				 
				unsigned char szRecvBuff[BUFF_SIZE] = { 0, }; // for receiving
				int iReadBytes = recvfrom(m_iUDPSocketFD, szRecvBuff, BUFF_SIZE, 0, (struct sockaddr *)&stSockAddr, &iSockLength);
				if (iReadBytes <= 0)
					continue;
				
				iSockLength = sizeof(stSockAddr);
				unsigned char szSendBuff[BUFF_SIZE] = { 0, }; // for sending
				int iToSendBytes = BuildDNSResponse(szRecvBuff, szSendBuff, (struct sockaddr *)&stSockAddr);
				if (iToSendBytes > 0)
				{
					int iSendBytes = sendto(m_iUDPSocketFD, szSendBuff, iToSendBytes, 0, (struct sockaddr *)&stSockAddr, iSockLength);
				}
			}
			else
			{
				
			}
		
		}
	} while (1);
	
	return true;
}


// Build up a DNS Response corresponding to a Query from a Client
int CDNSServer::BuildDNSReponse()
{
	// Parsing a DNS Query from a Client
	struct DNS_HEADER* pRecvedDNSHeader  = (struct DNS_HEADER*)(m_szRecvBuff);
	m_uiIDforDNSQuery = pRecvedDNSHeader->uiID;
	unsigned char* pURL = m_szRecvBuff + sizeof(struct DNS_HEADER);
	m_strURL = (char*)pURL;
	
	//if (0 != memcmp(szTemp, m_strURL.c_str(), m_strURL.length()))
	
	// Drop Requests other than cs5700cdn.example.com
	if (m_strURL != m_strCDNNameDNSFormat)
		return 0;
	
	
	// Build up a Response
	memset(m_szSendBuff, 0, sizeof(m_szSendBuff));
	struct DNS_HEADER* pDNSHeader = (struct DNS_HEADER*)(m_szSendBuff);

	pDNSHeader->uiID = m_uiIDforDNSQuery;
	pDNSHeader->RD = 1;
	pDNSHeader->QR = 1; // Response
	pDNSHeader->RA = 1;

	pDNSHeader->TC = 0;
	pDNSHeader->AA = 0;
	pDNSHeader->Opcode = 0;
	pDNSHeader->Rcode = 0;
	pDNSHeader->CD = 0;
	pDNSHeader->AD = 0;
	pDNSHeader->Z = 0;
	
	pDNSHeader->uiTotal_Questions = htons(1);
	pDNSHeader->uiTotal_Answer_RRs = htons(1);
	pDNSHeader->uiTotal_Authority_RRs = 0;
	pDNSHeader->uiTotal_Additional_RRs = 0;
	
	unsigned char* pBuff = m_szSendBuff + sizeof(struct DNS_HEADER);
	memcpy(pBuff, m_strURL.c_str(), m_strURL.length());
	
	struct DNS_QUESTION* pDNSQuestion = (struct DNS_QUESTION*)(pBuff + strlen((char*)pBuff) + 1);
	pDNSQuestion->uiType = htons(TYPE_A);
	pDNSQuestion->uiClass = htons(1);
	
	// Offset setting
	unsigned char* pMessageCompression = pBuff + strlen((char*)pBuff) + 1 + sizeof(struct DNS_QUESTION);	
	*pMessageCompression++ = 0xc0;
	*pMessageCompression++ = 0x0c;
	
	struct R_DATA* pRData = (struct R_DATA*)pMessageCompression;
	pRData->uiClass = htons(1);
	pRData->uiType = htons(TYPE_A);
	pRData->uiTTL = htonl(5);
	pRData->uiRdataLength = htons(4);
	
	// Only one IP for now
	unsigned char* pIP = pMessageCompression + sizeof(struct R_DATA);
	//54.88.97.7
	*pIP++ = 54;
	*pIP++ = 88;
	*pIP++ = 98;
	*pIP++ = 7;
	
	return pIP - m_szSendBuff;
}

// Build up a DNS Response corresponding to a Query from a Client
// This function is used in multiple threads, so be careful about using member variables here.
int CDNSServer::BuildDNSResponse(unsigned char* szRecvData_, unsigned char* szSendData_, const struct sockaddr *const pSockaddr_)
{
	// Parsing a DNS Query from a Client
	struct DNS_HEADER* pRecvedDNSHeader  = (struct DNS_HEADER*)(szRecvData_);
	//m_uiIDforDNSQuery = pRecvedDNSHeader->uiID;
	unsigned char* pURL = szRecvData_ + sizeof(struct DNS_HEADER);
	std::string strURL = (char*)pURL;
	
	// Drop Requests other than cs5700cdn.example.com
	if (strURL != m_strCDNNameDNSFormat)
		return 0;

	// Build up a Response
	struct DNS_HEADER* pDNSHeader = (struct DNS_HEADER*)(szSendData_);

	pDNSHeader->uiID = pRecvedDNSHeader->uiID;
	pDNSHeader->RD = 1;
	pDNSHeader->QR = 1; // Response
	pDNSHeader->RA = 1;
	
	pDNSHeader->uiTotal_Questions = htons(1);
	pDNSHeader->uiTotal_Answer_RRs = htons(1);
/*
	pDNSHeader->TC = 0;
	pDNSHeader->AA = 0;
	pDNSHeader->Opcode = 0;
	pDNSHeader->Rcode = 0;
	pDNSHeader->CD = 0;
	pDNSHeader->AD = 0;
	pDNSHeader->Z = 0;
	

	pDNSHeader->uiTotal_Authority_RRs = 0;
	pDNSHeader->uiTotal_Additional_RRs = 0;
*/
	
	unsigned char* pBuff = szSendData_ + sizeof(struct DNS_HEADER);
	memcpy(pBuff, strURL.c_str(), strURL.length());
	
	struct DNS_QUESTION* pDNSQuestion = (struct DNS_QUESTION*)(pBuff + strlen((char*)pBuff) + 1);
	pDNSQuestion->uiType = htons(TYPE_A);
	pDNSQuestion->uiClass = htons(1);
	
	// Offset setting
	unsigned char* pMessageCompression = pBuff + strlen((char*)pBuff) + 1 + sizeof(struct DNS_QUESTION);	
	*pMessageCompression++ = 0xc0;
	*pMessageCompression++ = 0x0c;
	
	struct R_DATA* pRData = (struct R_DATA*)pMessageCompression;
	pRData->uiClass = htons(1);
	pRData->uiType = htons(TYPE_A);
	pRData->uiTTL = htonl(5);
	pRData->uiRdataLength = htons(4);
	
	
	//
	struct sockaddr_in SockAddr;
	
	SockAddr.sin_family = AF_INET;
	SockAddr.sin_port = htons(m_uiUDPServerPort);
	inet_aton(m_strServerList[8].c_str(), &SockAddr.sin_addr);
	
	int gai_error, mmdb_error;
	MMDB_lookup_result_s LookupResult = MMDB_lookup_sockaddr(&m_GeoIPDB, pSockaddr_, &mmdb_error);
	int iBestServerIndex = RS_VIRGINIA;
	if (MMDB_SUCCESS == mmdb_error) 
	{
		int exit_code = 0;
		if (LookupResult.found_entry) 
		{

			MMDB_entry_data_s Location_Latitude;
			MMDB_entry_data_s Location_Longitude;
			int status = MMDB_get_value(&LookupResult.entry, &Location_Latitude, "location", "latitude", NULL);
			if (MMDB_SUCCESS == status) 
			{
				double fLatitude = Location_Latitude.double_value;
				status = MMDB_get_value(&LookupResult.entry, &Location_Longitude, "location", "longitude", NULL);
				
				if (MMDB_SUCCESS == status) 
				{
					double fLongitude = Location_Longitude.double_value;
					iBestServerIndex = SelectBestServer(fLatitude, fLongitude);
				}
			}
		}
	}
			
	// Only one IP for now
	unsigned char* pIP = pMessageCompression + sizeof(struct R_DATA);
	memcpy(pIP, &m_stReplicaSockAddr[iBestServerIndex].sin_addr, sizeof(m_stReplicaSockAddr[iBestServerIndex].sin_addr));

	return (pIP + 4 - szSendData_);
}

// Convert a URL into a DNS Name Format ( www.facebook.com -> 3www8facebook3com)
void CDNSServer::ConvertURLtoDNSName(char* szDNS_, char* szURL_)
{
	int iCurrentIndex = 0;
	strcat(szURL_, ".");
	char* pCurrentURL = szURL_;
	
	do
	{
		char* pDot = strchr(pCurrentURL, '.');
		if (NULL == pDot)
			break;

		int iDottedLength = pDot - pCurrentURL;
		*szDNS_++ = iDottedLength;
		memcpy(szDNS_, pCurrentURL, iDottedLength);
		szDNS_ += iDottedLength;
		pCurrentURL += iDottedLength + 1;

	} while (1);
	
	*szDNS_ = '\0';
}

int CDNSServer::SelectBestServer(double fLatitude_, double fLongitude_)
{
	double fDiffLatitude = (fLatitude_ - m_stServerLocation[0].fLatitude);
	double fDiffLongitude = (fLongitude_ - m_stServerLocation[0].fLongitude);
	
	int iShortestIndex = 0;
	double fShortestDistance = (fDiffLatitude * fDiffLatitude) + (fDiffLongitude * fDiffLongitude);
	for (int i = 1; i < RS_MAX; ++i)
	{
		fDiffLatitude = (fLatitude_ - m_stServerLocation[i].fLatitude);
		fDiffLongitude = (fLongitude_ - m_stServerLocation[i].fLongitude);
		double fDistance = (fDiffLatitude * fDiffLatitude) + (fDiffLongitude * fDiffLongitude);
		if (fShortestDistance > fDistance)
		{
			fShortestDistance = fDistance;
			iShortestIndex = i;
		}
			
	}
	
	return iShortestIndex;
}

bool CDNSServer::InitGeoIPDatabase()
{
	char fname[256] = "GeoLite2-City.mmdb";
	int status = MMDB_open(fname, MMDB_MODE_MMAP, &m_GeoIPDB);

	if (MMDB_SUCCESS != status)
	{
		Display_Error_Message("MMDB_open Failed!");
		return false;
	}
	
	return true;
}


