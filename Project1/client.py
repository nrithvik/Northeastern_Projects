#!/usr/bin/python
import socket
import sys
import ssl

try:		#Check for the specified valid port number
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Creating a socket
	portNumber=sys.argv[1]
	port= int(sys.argv[2])
	assert(portNumber=='-p') #Checks if port switch is specified
except AssertionError:
	print "Invalid parameter for port, please specify the port switch"
	sys.exit()
except ValueError:
	print "Invalid input for port"
	sys.exit()
try:		#Check for SSL 
	sslVariable= sys.argv[3]
	assert(sslVariable=="-s"),"Please specify -s after port to provide ssl"
except AssertionError:
	print "-s not specified for SSL"
	sys.exit()

try:		#Check for specified and valid hostname 
	serveraddress = sys.argv[4]
	serverip=socket.gethostbyname(serveraddress)
	assert(serverip=="129.10.113.143"),"Invalid hostname"
except socket.gaierror:
	print "Name or service not known"
	sys.exit()
except AssertionError:
	print "Invalid hostname"
	sys.exit()

nuID=sys.argv[5]
if len(nuID)==9 and nuID.isdigit(): #This condition checks for a valid NUID
		
   try:	
	s=ssl.wrap_socket(s)
	s.settimeout(5)				#Timeout of 5 seconds keeps the socket open for that duration 
	s.connect((serverip,port))		#Client getting connected to the server 
   except ssl.SSLEOFError:
	print "Wrong port number specified for SSL"
	s.close()
	sys.exit()
   except OverflowError:
	print "Port range should be between 0-65535"
	s.close()
	sys.exit()	
   except socket.timeout:
	print"Socket timed out"
	s.close()
	sys.exit()
   helo = "cs5700spring2016 HELLO %s \n" %(nuID)	#Message containing the initial request from client 
   s.sendall(helo)									#Initial message sent to server 
   while True:
			reply=s.recv(256)						#Server's reply of buffersize 256 bytes received 
			
			try:								#Checks to see if timeout has occurrer 
				x=reply.split()						#Splits the response from server based on blank spaces in between 
			except socket.error:
				print "Socket connection timedout"
				s.close()
				sys.exit()
			
			if x[1]=="STATUS" and x[0]=="cs5700spring2016" and len(x)==5: #Checks the server's response to see if message received is as expected 
				try:						      #Checks if operands are legitimate 
					assert (x[2].isdigit()==True and x[4].isdigit()==True),"Operands are not numbers"
				except AssertionError:
					print "Terminating connection because operands received are not numbers"
					s.close()
					sys.exit()
				op1 = int (x[2])
				op2 = int (x[4])
				try:
					assert((0<=op1<=1000) and (0<=op2<=1000)),"Operands are not within the range"
				except AssertionError:
					print "Terminating connection because operands received are not within the range"
					s.close()
					sys.exit()
				
				opr=x[3]
				if opr == '+' :
					result= op1+op2
				elif  opr == '-' :
					result= op1-op2
				elif opr == '/' :
					try:
						result= op1/op2
					except ZeroDivisionError:
						print "Integer division or modulo by zero"
						s.close()
						sys.exit()
						
				elif opr == '*':
					result= op1*op2
				else:
					print("Operand recieved cannot be processed")
					s.close()	
				
				
				solution = "cs5700spring2016 %d \n" %(result)        #Computes the solution 
				s.sendall(solution)				     #Send the solution back to the server
			elif x[2]=="BYE" and x[0]=="cs5700spring2016" and len(x)==3: #Checks if the response is a BYE message that is expected
				print x[1]
				if len (x[1])!=64:				     #Checks if the BYE message contains a legitimate 64 byte secret flag
					print "Flag received is not of 64 bytes"
					s.close()
					break
				else:
					s.close()	
					break
			else:
				print reply
				print "The server has sent an invalid response"
				s.close()
				break	
else:
	print("Please check your NEUID and try again")
	s.close()
