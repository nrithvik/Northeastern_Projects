#!/usr/bin/python
import socket
import sys
import urlparse
from HTMLParser import HTMLParser
from bs4 import BeautifulSoup
from urlparse import urlparse
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creating a socket
port= 80
ad="cs5700sp16.ccs.neu.edu"
serverip=socket.gethostbyname(ad)
mainlist=[]
sublist=[]
secret_flags=[]
count =1



def movedpermanently(recdstring):
	splitlist=recdstring.split('\r\n')
	for i in range (0,len(splitlist)):
		if 'Location: ' in splitlist[i]:
			link=splitlist[i]				
			referer=link[11:len(link)]
			o=urlparse(referer)
			hosturl=o.netloc #gets host 
			pathurl=o.path   #gets path
			message = "GET %s HTTP/1.1\r\n" %pathurl
			host="Host: %s\r\n" %hosturl
			conn="Connection: keep-alive\r\n"
			ref="Referer: http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/\r\n"
			fmsg=message + host + conn + ref + "\r\n"
			s.sendall(fmsg)
			recdstring=s.recv(4096)
			return recdstring

def forbiddenpage():
	print "403 Forbidden ERROR"
	s.close()
	sys.exit()

def notfound():
	print "404 Not Found"
	print "Please check your URI"
	s.close()
	sys.exit()

def servererror():
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creating a socket
	port= 80
	ad="cs5700sp16.ccs.neu.edu"
	serverip=socket.gethostbyname(ad)
	try:
		s.connect((serverip,port))	#Client getting connected to the ser
	except socket.error, e:
		print "Socket error: %s" %e	
	message = "GET %s HTTP/1.1\r\n" % url
	host="Host: cs5700sp16.ccs.neu.edu\r\n"
	conn="Connection: keep-alive\r\n"
	re="Referer: http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/\r\n"
	ck= "Cookie: csrftoken=%s; sessionid=%s\r\n"% (csrftoken,sessionid)
	fmsg=message + host + conn + re + ck + "\r\n"
	s.sendall(fmsg)
	recdstring=s.recv(4096)
	return recdstring

def basic_page():
		#Check for the specified valid port number
	
	
	#print serverip
	#s.settimeout(10)
	try:
		s.connect((serverip,port))	#Client getting connected to the ser
	except socket.error, e:
		print "Socket error: %s" %e
	
	message = "GET /accounts/login/?next=/fakebook/ HTTP/1.1\r\n"
	host="Host: cs5700sp16.ccs.neu.edu\r\n"
	conn="Connection: keep-alive\r\n"
	ref="Referer: http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/\r\n"
	fmsg=message + host + conn + ref + "\r\n"
	s.sendall(fmsg) #send final GET message to server
	
	recdstring=s.recv(4096) #get recdstring and check for header line
	if "301 Moved Permanently" in recdstring: #checks if received message is a 301 response
		recdstring=movedpermanently(recdstring)
	elif "403 Forbidden" in recdstring:
		forbiddenpage()
	elif "404 Not Found" in recdstring:
		notfound()
	elif "500 Internal Server Error" in recdstring:
		recdstring=servererror()
		
#The loop below runs to receive the entire message

	if 'Content-Length: 0' not in recdstring: 
	    while '</html>' not in recdstring:
	        recdstring=recdstring+s.recv(4096)
	
	val=recdstring.find("csrftoken=")
	
	csrftoken=recdstring[val+10:val+42]
	
	sid=recdstring.find("sessionid=")
	sessionid=recdstring[sid+10:sid+42]

	


	home="next=/fakebook/"
	message = "POST /accounts/login/ HTTP/1.1\r\n"
	parameters = "username=%s&password=%s&csrfmiddlewaretoken=%s&%s \r\n" % (username,password,csrftoken,home)
	host="Host: cs5700sp16.ccs.neu.edu\r\n"
	Conn="Connection: keep-alive\r\n"
	contentLength = "Content-Length: " + str(len(parameters)) + "\r\n"
	contentType = "Content-Type: application/x-www-form-urlencoded\r\n"
	Referer="Referer: http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/\r\n"
	ck= "Cookie: csrftoken=%s; sessionid=%s\r\n"% (csrftoken,sessionid)
	finalMessage = message + host + Conn + contentLength + contentType + Referer + ck + "\r\n"
	finalMessage = finalMessage + parameters
	s.sendall(finalMessage)
	
	recdstring=s.recv(4096) #get recdstring and check for header line

	if "301 Moved Permanently" in recdstring: #checks if received message is a 301 response
		print "The link has been moved permanently"
		s.close()
		sys.exit()
	elif "403 Forbidden" in recdstring:
		forbiddenpage()
	elif "404 Not Found" in recdstring:
		notfound()
	elif "500 INTERNAL SERVER ERROR" in recdstring: #Reinitiating the POST Request
		home="next=/fakebook/"
		message = "POST /accounts/login/ HTTP/1.1\r\n"
		parameters = "username=%s&password=%s&csrfmiddlewaretoken=%s&%s \r\n" % (username,password,csrftoken,home)
		host="Host: cs5700sp16.ccs.neu.edu\r\n"
		Conn="Connection: keep-alive\r\n"
		contentLength = "Content-Length: " + str(len(parameters)) + "\r\n"
		contentType = "Content-Type: application/x-www-form-urlencoded\r\n"
		Referer="Referer: http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/\r\n"
		ck= "Cookie: csrftoken=%s; sessionid=%s\r\n"% (csrftoken,sessionid)
		finalMessage = message + host + Conn + contentLength + contentType + Referer + ck + "\r\n"
		finalMessage = finalMessage + parameters
		s.sendall(finalMessage)
		recdstring=s.recv(4096)
		
	if 'Content-Length: 0' not in recdstring:
	    while '</html>' not in recdstring:
	        recdstring=recdstring+s.recv(4096)

	if "Please enter a correct username and password" in recdstring: #Checks if the username and password entered are valid
		print "Wrong username and password pair"
		s.close()
		sys.exit()
	else:
		sid=recdstring.find("sessionid=")
		sessionid=recdstring[sid+10:sid+42]
		


		message = "GET /fakebook/ HTTP/1.1\r\n"
		host="Host: cs5700sp16.ccs.neu.edu\r\n"
		conn="Connection: keep-alive\r\n"
		re="Referer: http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/\r\n"
		ck= "Cookie: csrftoken=%s; sessionid=%s\r\n"% (csrftoken,sessionid)
		fmsg=message + host + conn + re + ck + "\r\n"
		
		s.sendall(fmsg)
		recdstring=s.recv(4096)
		if "301 MOVED PERMANENTLY" in recdstring: #checks if received message is a 301 response
			recdstring=movedpermanently(recdstring)
		elif "403 Forbidden" in recdstring:
			forbiddenpage()
		elif "404 Not Found" in recdstring:
			notfound()
		elif "500 INTERNAL SERVER ERROR" in recdstring:
			recdstring=servererror()
		if 'Content-Length: 0' not in recdstring:
		    while '</html>' not in recdstring:
		        recdstring=recdstring+s.recv(4096)
		
		soup=BeautifulSoup(recdstring,'html.parser') #Parse using beautiful soup to obtain links
		
		for link in soup.find_all('a'):
		    a = str(link.get('href'))
		    if '/fakebook/' in a:
		    	mainlist.append(a)
	s.close()
	return (sessionid,csrftoken)




def url_page(url,sessionid,csrftoken):
	sublist_count=0
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creating a socket
	port= 80
	ad="cs5700sp16.ccs.neu.edu"
	serverip=socket.gethostbyname(ad)
	try:
		s.connect((serverip,port))	
	except socket.error, e:
		print "Socket error: %s" %e
	
	message = "GET %s HTTP/1.1\r\n" % url
	host="Host: cs5700sp16.ccs.neu.edu\r\n"
	conn="Connection: keep-alive\r\n"
	re="Referer: http://cs5700sp16.ccs.neu.edu/accounts/login/?next=/fakebook/\r\n"
	ck= "Cookie: csrftoken=%s; sessionid=%s\r\n"% (csrftoken,sessionid)
	fmsg=message + host + conn + re + ck + "\r\n"
	s.sendall(fmsg)
	recdstring=s.recv(4096)
	if "301 Moved Permanently" in recdstring: #checks if received message is a 301 response
		recdstring=movedpermanently(recdstring)
	elif "403 Forbidden" in recdstring:
		forbiddenpage()
	elif "404 Not Found" in recdstring:
		notfound()
	elif "500 INTERNAL SERVER ERROR" in recdstring:
		recdstring=servererror()
	if 'Content-Length: 0' not in recdstring:
	    while '</html>' not in recdstring:
	        recdstring=recdstring+s.recv(4096)
	        if recdstring.find("Connection: close\r\n"):
	        	break

	soup=BeautifulSoup(recdstring,'html.parser')
	for link in soup.find_all('a'):
	    a = str(link.get('href'))
	    if (a not in mainlist) and ('/fakebook/' in a): #check if link obtained is already present in the mainlist
	    	mainlist.append(a)
	    	sublist_count+=1
		if "secret_flag" in recdstring: #Checks for secret flag in response
			flag=str(soup.h2.string)
			print flag.replace("FLAG: ","")
			if flag in secret_flags: 
				print "Repition"
				sys.exit()
			else:
				secret_flags.append(flag)
	if  len(secret_flags)==5: # if this line is combined with donetillnow==mainlist[:] the program would crawl all the webpages also
		
		sys.exit()
	s.close()
	return (sublist_count)
if (len(sys.argv)!=3 or len(sys.argv[1])!=9 or sys.argv[1].isdigit()==False or len(sys.argv[2])==0):
	print "Please correct your Username and Password, and try again."
	sys.exit()
else:	
	count=0
	username=sys.argv[1]
	password=sys.argv[2]
	sessionid,csrftoken=basic_page()
	sublist_length=[len(mainlist)]
	sum=0
	donetillnow=[] #Used to crawl all webpages if needed
	while True:
		donetillnow=mainlist[:]
		for j in range (0,len(sublist_length)): 
			sublist=mainlist[sum:sum+sublist_length[j]-1] #Contains the position of the last link traversed from mainlist
			
			for i in range (len(sublist)):
				url=sublist[i]
				if url=="/fakebook/":
					continue
				
				count_sublist=url_page(url,sessionid,csrftoken)
				count+=1
				sublist_length.append(count_sublist)
				