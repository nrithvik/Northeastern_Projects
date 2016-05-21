all: dnsserver httpserver deployCDN runCDN stopCDN
	chmod +x httpserver
	chmod +x deployCDN
	chmod +x runCDN
	chmod +x stopCDN

dnsserver: DNS_Server.o CDNSServer.o 
	g++ -o dnsserver DNS_Server.o CDNSServer.o -lpthread -L. -lmaxminddb

CDNSServer.o: CDNSServer.h CDNSServer.cpp 
	g++ -c CDNSServer.cpp 

DNS_Server.o: CDNSServer.h DNS_Server.cpp
	g++ -c DNS_Server.cpp 

httpserver:
	touch httpserver	
	cat httpserver.py > httpserver

deployCDN:
	touch deployCDN 	
	cat deployCDN.sh > deployCDN

runCDN:
	touch runCDN	
	cat runCDN.sh > runCDN

stopCDN:
	touch stopCDN	
	cat stopCDN.sh > stopCDN



