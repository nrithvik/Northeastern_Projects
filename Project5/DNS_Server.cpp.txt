#include "CDNSServer.h"
#include <pthread.h>
// Thread Argument
struct ThreadData
{
	CDNSServer* m_pDNSServer;
	int m_iThreadNumber;
};

// Thread Handler
void *thread_main(void *pArg_)
{
	struct ThreadData* pData = (ThreadData*)pArg_;
	int iThreadNumber = pData->m_iThreadNumber;
	pData->m_pDNSServer->RunServer();
	//pData->m_pWebCrawler->SetThreadNumber(iThreadNumber);
	//pData->m_pWebCrawler->InitConnection();
	//pData->m_pWebCrawler->ConnectToServerWithPolling(0);
	//pData->m_pWebCrawler->CrawlingWithPolling();
	
	return NULL;
}

int main(int argc, char *argv[])
{
	
	// Input Arguments Checking
	if (argc < 5)
	{
		printf("Usage: ./dnsserver -p <port> -n <name>\n");
		return 0;
	}
	
	// Option Checking
	if (0 != strcmp(argv[1], "-p") || 0 != strcmp(argv[3], "-n"))
	{
		printf("Usage: ./dnsserver -p <port> -n <name>\n");
		return 0;
	}
	
	// Port Number Range Checking
	int iPort = atoi(argv[2]);
	if (iPort < LOWEST_PORT || iPort > HIGHEST_PORT)
	{
		printf("Port Number must be between 40000 - 65535\n");
		return 0;
	}
	


	//int iPort = 42007;
	//char szURL[256] = "cs5700cdn.example.com";
	//CDNSServer* pDNSServer = new CDNSServer(iPort, szURL);
	// Create a DNS Server and run it
	CDNSServer* pDNSServer = new CDNSServer(iPort,argv[4]);
	pthread_t uiThread[4];
	int iThreadCount = 4;
	if (pDNSServer->InitServer())
	{
		
		for(int i = 0 ; i < iThreadCount; ++i)
		{
			struct ThreadData stTheadInfo = { pDNSServer, i };
			
			pthread_create(&uiThread[i], NULL, &thread_main, (void*)&stTheadInfo);
		}
		
		
		pDNSServer->RunServer();
	}
		
	
	delete pDNSServer;
	
	return 0;
}
