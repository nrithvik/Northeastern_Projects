#!/usr/bin/python
import socket
from urlparse import urlparse
import sys
import random
import os
import subprocess
from struct import *
import time
os.system("iptables -F")
os.system("iptables -A OUTPUT -p tcp --tcp-flags RST RST -j DROP")
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
destination_address=sys.argv[1]

o = urlparse(destination_address)
path=o.path
if len(o.scheme)==0:
	destination_address='http://' +destination_address
o = urlparse(destination_address)
path=o.path
x=os.path.basename(path)

if len(x)==0:
	file_name = "index.html"
else:
	file_name = x

s.connect(("gmail.com",80))
source_ip=(s.getsockname()[0])
source_ip= socket.inet_aton (source_ip) 
s.close()
try:

	destination_name=socket.gethostbyname(o.netloc)
except socket.gaierror,msg:
	print "Please check the url and try again, No address associated with the hostname"
	sys.exit()

destination_ip=socket.inet_aton ( destination_name )

src_port = random.randint(3000,65535) 
dst_port = 80
cwnd=0







	

def carry_around_add(a, b):
    c = a + b
    return (c & 0xffff) + (c >> 16)
# checksum functions needed for calculation checksum
def checksum(msg):
    s = 0
    
    # loop taking 2 characters at a time
    if len(msg)%2 != 0:
    	
    	msg=msg+chr(0)
    	
    	for i in range(0, len(msg), 2):
        	w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        	s = carry_around_add(s,w)
    else:
     	
     	for i in range(0, len(msg), 2):
        	w = ord(msg[i]) + (ord(msg[i+1]) << 8 )
        	s = carry_around_add(s,w)
    #complement and mask to 4 byte short
    s = ~s & 0xffff
     
    return s
 
#create a raw socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
except socket.error , msg:
    print 'Socket could not be created. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
    sys.exit()
 

# now start constructing the packet
 
# ip header fields
def ip_header(ip_id,ip_proto,destination_ip,source_ip):
	ip_ihl = 5
	ip_ver = 4
	ip_tos = 0
	ip_tot_len = 0  # kernel will fill the correct total length
	ip_frag_off = 0
	ip_ttl = 255
	ip_proto = socket.IPPROTO_TCP
	ip_check = 0    # kernel will fill the correct checksum
	#ip_saddr = socket.inet_aton ( source_ip )   #Spoof the source ip address if you want to
	#ip_daddr = socket.inet_aton ( destination_ip )

	ip_ihl_ver = (ip_ver << 4) + ip_ihl

	ip_header = pack('!BBHHHBBH4s4s' , ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off, ip_ttl, ip_proto, ip_check, source_ip, destination_ip)
	return ip_header
# tcp header fields
def tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data):
	tcp_source = src_port # source port
	tcp_dest = dst_port   # destination port

	tcp_ack_seq = tcp_ackno
	tcp_doff = 5    #4 bit field, size of tcp header, 5 * 4 = 20 bytes
	#tcp flags
	tcp_rst = 0
	tcp_urg = 0
	tcp_window = socket.htons (3500)    #   maximum allowed window size
	tcp_check = 0
	tcp_urg_ptr = 0
	 
	tcp_offset_res = (tcp_doff << 4) + 0
	tcp_flags = tcp_fin + (tcp_syn << 1) + (tcp_rst << 2) + (tcp_psh <<3) + (tcp_ack << 4) + (tcp_urg << 5)
	tcp_header=pack('!HHLLBBHHH',tcp_source,tcp_dest,tcp_seq,tcp_ack_seq,tcp_offset_res,tcp_flags,tcp_window,tcp_check,tcp_urg_ptr)
 
# pseudo header fields
	#source_address = socket.inet_aton(source_ip)
	#dest_address = socket.inet_aton(destination_ip)
	placeholder = 0
	protocol = socket.IPPROTO_TCP
	tcp_length = len(tcp_header) + len(user_data)
	
	psh=pack('!4s4sBBH',source_ip,destination_ip,placeholder,protocol,tcp_length);
	psh=psh+tcp_header + user_data;
	
	tcp_check = checksum(psh)
	#print tcp_checksum
	
	# make the tcp header again and fill the correct checksum - remember checksum is NOT in network byte order
	tcp_header = pack('!HHLLBBH',tcp_source,tcp_dest,tcp_seq,tcp_ack_seq,tcp_offset_res,tcp_flags,tcp_window)+pack('H',tcp_check)+pack('!H',tcp_urg_ptr)
	return tcp_header

def SYN():

	tcp_ackno=0
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
	except socket.error:
		print 'Socket Error'
		sys.exit()
	user_data=''
	ip_ident=random.randint(50000,60000)

	#ip_header(ip_id,ip_proto,destination_ip,source_ip)
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,source_ip)
	tcp_sequ=random.randint(30000,35000)
	
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)
	tcp1=tcp_header(tcp_sequ,tcp_ackno,0,0,1,0,user_data)
	packet=ip1+tcp1
	s.sendto(packet,(destination_name,0))
	start_time=time.time()
	SYN_ACK(start_time)


def SYN_ACK(start_time):

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW,socket.IPPROTO_TCP)
	except s.error:
		print 'Socket Error'
		sys.exit()
	
	recd_data=s.recvfrom(65535)
	
	recd_data=recd_data[0]
	recd_packet=recd_data[20:]
	ip_data=unpack('BBHHHBBH4s4s', recd_data[0:20])
	
	IP_DST_addr = socket.inet_ntoa(ip_data[8])
	IP_Src_addr = socket.inet_ntoa(ip_data[9])
	IP_ver_headerl= ip_data[0]
	IP_ver= IP_ver_headerl >> 4
	IP_headerl= ((IP_ver_headerl & 0xF) * 4)
	
	
	tcp_data= unpack('!HHLLBBHHH', recd_data[IP_headerl : IP_headerl+20])
	global tcp_seqno
	tcp_seqno=tcp_data[2]
	global tcp_ackno
	tcp_ackno=tcp_data[3]
	tcp_flags=tcp_data[5]
	checksum=cal_rec_checksum(recd_packet)

	tcp_headerl_res = tcp_data[4]			
	tcp_headerl = tcp_headerl_res >> 4
	if checksum==0:
		if tcp_flags==18 and ((start_time-time.time())<60):
			ACK(tcp_seqno,tcp_ackno)
		elif ((start_time-time.time())>60):
			if ((start_time-time.time())>180):
				print "No packet in 3 minutes. Exiting"
				sys.exit()
			else:
				SYN()
		else:
			SYN()
	else:
		SYN()

def ACK(tcp_seqno,tcp_ackno):
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
	except socket.error:
		print 'Socket Error'
		sys.exit()
	user_data=''
	ip_ident=random.randint(50000,60000)
	

	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,source_ip)
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)
	tcp1=tcp_header(tcp_ackno,tcp_seqno+1,1,0,0,0,user_data)
	packet=ip1+tcp1
	s.sendto(packet,(destination_name,0))
	
	GetData(tcp_ackno,tcp_seqno)

def GetData(tcp_ackno,tcp_seqno):
	cwnd=0
	i=0
	start_time=0
	
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW,socket.IPPROTO_RAW)
	except socket.error:
		print 'Socket Error'
		sys.exit()
	ip_ident=random.randint(50000,60000)
	user_data = ("GET " +path+  " HTTP/1.0\r\n"
	"Host: david.choffnes.com\r\n"
	"Connection: keep-alive\r\n"
	"\r\n")

	if len(user_data) % 2 !=0:
		user_data = user_data + " "
	
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,source_ip)
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)
	tcp1=tcp_header(tcp_ackno,tcp_seqno+1,1,1,0,0,user_data)
	
	tot_tcp_data=len(tcp1+user_data)-20
	packet=ip1+tcp1+user_data
	
	
	s.sendto(packet,(destination_name,0))
	
	try:
			s = socket.socket(socket.AF_INET, socket.SOCK_RAW,socket.IPPROTO_TCP)
	except socket.error:
			print 'Socket Error'
			sys.exit()
	
	
	final_data=()
	tcp_flags=0
	seqdata={}
	
	while True:

		
		recd_data=s.recvfrom(65535)
		final_data+=recd_data
		
		real_data=recd_data[0]
		recd_packet=real_data[20:]
		ip_data=unpack('BBHHHBBH4s4s', real_data[0:20])
		
		IP_DST_addr = socket.inet_ntoa(ip_data[8])
		IP_Src_addr = socket.inet_ntoa(ip_data[9])
		IP_ver_headerl= ip_data[0]
		IP_ver= IP_ver_headerl >> 4
		IP_headerl= ((IP_ver_headerl & 0xF) * 4)
		
		
		tcp_data= unpack('!HHLLBBHHH', real_data[IP_headerl : IP_headerl+20])
		
		tcp_seqno=tcp_data[2]
		
		tcp_ackno=tcp_data[3]
		tcp_flags = tcp_data[5]
		
		tcp_headerl_res = tcp_data[4]			
		tcp_headerl = tcp_headerl_res >> 4

		Total_Header = IP_headerl + (tcp_headerl *4)
		total_data = len(real_data) - Total_Header
		
		data=real_data[Total_Header:]
		checksum=cal_rec_checksum(recd_packet)
		
		

		if (tcp_data[0]==dst_port and tcp_data[1]==src_port):
			
			if i==1:
				

				if(added_seq==tcp_seqno and checksum==0):
					
					
					if tcp_flags%2!=0:
						if '200 OK' in final_data[2]:
							
							seqdata[tcp_seqno]=data
							create_file(seqdata)
							FIN_ACK(tcp_seqno,tcp_ackno)
						
						elif '301' in final_data[2]:
							print"301 Moved Permanently"
							FIN_ACK(tcp_seqno,tcp_ackno)
							sys.exit()
						
						elif '403'in final_data[2]:
							print " 403 Forbidden"
							FIN_ACK(tcp_seqno,tcp_ackno)
							sys.exit()
						
						elif '500' in final_data[2]:
							print "500 Internal Server Error"
							FIN_ACK(tcp_seqno,tcp_ackno)
							sys.exit()
						
						elif '404' in final_data[2]:
							print "404 Not Found"
							FIN_ACK(tcp_seqno,tcp_ackno)
							sys.exit()
						
						else:
							create_file(seqdata)
							FIN_ACK(tcp_seqno,tcp_ackno)
					else:
						
						seqdata[tcp_seqno]=data
						ACK2(total_data,tcp_seqno,tcp_ackno)
						start_time=time.time()
						added_seq=tcp_seqno+total_data
						
						prev_tcpseq=tcp_seqno
						prev_ack=tcp_ackno
						prev_totaldata=total_data
						start_time=time.time()
						
						if cwnd==1000:
							cwnd=1000
						else:
							cwnd+=1
				
				elif (added_seq!=tcp_seqno and ((time.time()-start_time)> 180)):
					
					print "No packet in 3 minutes. Exiting."
					sys.exit()
				
				elif (added_seq!=tcp_seqno and ((time.time()-start_time)>60)):
					
					start_time=0
					cwnd=1
					ACK2(prev_totaldata,prev_tcpseq,prev_ack)
					start_time=time.time()

			else:
				i=i+1
				
				start_time=time.time()
				added_seq=tcp_seqno+total_data
				
				prev_tcpseq=tcp_seqno
				prev_ack=tcp_ackno
				prev_totaldata=total_data


def ACK2(total_data,tcp_seqno,tcp_ackno):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
	except socket.error:
		print 'Socket Error'
		sys.exit()
	user_data=''
	ip_ident=random.randint(50000,60000)
	
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,source_ip)
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)
	tcp1=tcp_header(tcp_ackno,tcp_seqno+total_data,1,0,0,0,user_data)
	packet=ip1+tcp1
	s.sendto(packet,(destination_name,0))

def FIN_ACK(tcp_seqno,tcp_ackno):
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
	except socket.error:
		print 'Socket Error'
		sys.exit()
	user_data=''
	ip_ident=random.randint(50000,60000)
	
	ip1=ip_header(ip_ident,socket.IPPROTO_TCP,destination_ip,source_ip)
	#tcp_header(tcp_seq,tcp_ackno,tcp_ack,tcp_psh,tcp_syn,tcp_fin,user_data)
	tcp1=tcp_header(tcp_ackno,tcp_seqno+1,1,0,0,1,user_data)
	packet=ip1+tcp1
	s.sendto(packet,(destination_name,0))

	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_RAW,socket.IPPROTO_TCP)
	except s.error:
		print 'Socket Error'
		sys.exit()
	
	recd_data=s.recvfrom(65535)
	
	recd_data=recd_data[0]
	ip_data=unpack('BBHHHBBH4s4s', recd_data[0:20])
	
	IP_DST_addr = socket.inet_ntoa(ip_data[8])
	IP_Src_addr = socket.inet_ntoa(ip_data[9])
	IP_ver_headerl= ip_data[0]
	IP_ver= IP_ver_headerl >> 4
	IP_headerl= ((IP_ver_headerl & 0xF) * 4)
	
	
	tcp_data= unpack('!HHLLBBHHH', recd_data[IP_headerl : IP_headerl+20])
	tcp_seqno=tcp_data[2]
	tcp_ackno=tcp_data[3]
	tcp_flags=tcp_data[5]
	
	
	tcp_headerl_res = tcp_data[4]			
	tcp_headerl = tcp_headerl_res >> 4
	if tcp_flags==16 or tcp_flags%2==0:
		s.close()
		sys.exit()

def cal_rec_checksum(recd_packet):
	
	protocol=socket.IPPROTO_TCP
	placeholder=0
	psh=pack('!4s4sBBH',source_ip,destination_ip,placeholder,protocol,len(recd_packet));
	psh=psh+recd_packet

	calc_checksum=checksum(psh)

	return calc_checksum

def create_file(seqdata):
	
	sorted_tcp_seq=sorted(seqdata.keys())
	file=open(file_name,"w")
	i=0
	for j in sorted_tcp_seq:
		if i==0:
			data=seqdata[j]
			file.writelines(data.split('\r\n\r\n')[1])
			i=i+1
		else:
			file.writelines(seqdata[j])
	file.close()


####Start execution####
if (len(sys.argv)!=2):
	print "Please use the following command: ./rawhttpget.py [URL]"
	sys.exit()
else:

	SYN()