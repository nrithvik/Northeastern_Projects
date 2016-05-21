#!/usr/bin/env python
import BaseHTTPServer
import hashlib
import os
import urllib2
import sys
import operator
import pickle
from SocketServer import ThreadingMixIn
from BaseHTTPServer import*
import SimpleHTTPServer




global hits   
hits={}
global programHits
programHits={}
global cache
cache={}
global sizeDict
sizeDict={}
global cachesize
cachesize=0
availableSize= 0.25*1024*1024

def input():
  
  if len(sys.argv)==5:
    
    if ((sys.argv[1]=="-p") and (sys.argv[3] =="-o")):

        
        iPort=sys.argv[2]
        orgserv=sys.argv[4]

      
    elif (sys.argv[1]!="-p"):
     
      print "Correct format is ./httpserver -p [port] -o [origin]"
      sys.exit()    
    
    elif (sys.argv[2] not in range(40000,65535)):

    
      print "Port number should be between 40000 and 65535"
      sys.exit()  

    elif (sys.argv[3]!= "-o"):


      print "Correct format is ./httpserver -p [port] -o [origin]"
      sys.exit()  

    else:
      
      
      print "Correct format is ./httpserver -p [port] -o [origin]"
      sys.exit()

  else:

    
    print "Correct format is ./httpserver -p [port] -o [origin]"
    sys.exit()


  return iPort,orgserv

class ThreadingSimpleServer(ThreadingMixIn, HTTPServer):
    pass
class httpHandler(BaseHTTPRequestHandler):
    def do_GET(self):

      try:
        
        global cachesize
        global programHits
        global hits
        

        
        x = hashlib.md5()
        x.update(self.path)
        cacheFilename = x.hexdigest() + ".cached"
        
        #Checks the local cache and memory cache for requested files

        if os.path.exists(cacheFilename) or cacheFilename in cache:
          
          if os.path.exists(cacheFilename):
            
            response = open(cacheFilename).readlines()
            
            hits[cacheFilename]+=1
            self.send_response(200)
            self.end_headers()
            self.wfile.writelines(response)


          else:
            
            response=cache[cacheFilename]
            programHits[cacheFilename]+=1
            self.send_response(200)
            self.end_headers()
            self.wfile.writelines(response)


        
        else:
          
          #Fetches content from the server
          
          wholeurl="http://"+url+":8080"+self.path
          response = urllib2.urlopen(wholeurl).readlines()
          
          ###Finding the size of the file###

          resp = urllib2.urlopen (wholeurl)
          if "Content-Length" in resp.headers:
              incomingSize = int (resp.headers["Content-Length"])
          else:
              incomingSize = len (resp.read ())
          
          
          
      
          self.send_response(200)
          self.end_headers()
          self.wfile.writelines(response)

          

          #Checks if there is size is full
          
          if (incomingSize+cachesize <= availableSize):
            
            
            cache[cacheFilename]=response
            hits[cacheFilename]=1
            sizeDict[cacheFilename]=incomingSize
            
            
            
            cachesize+=incomingSize

            programHits[cacheFilename]=1


          else:
            
            
            #removes content to make space for incoming content by removing lowest hits
            minSize=0
        
            while(minSize <= cachesize):
              sorted_hits=sorted(programHits.items(), key=operator.itemgetter(1))
              
              i=sorted_hits[:]
              j=i[0][0]

              
              minSize+= sizeDict[j]
              
              
              
              #Deletes the content here
              
              if ((j in cache.keys()) and (j in programHits.keys())):
                
                
                del programHits[j]
                del cache[j]
                

                cachesize-=minSize

              else:
                
                continue 
            
            #Checks the folder size
            
            folder = os.getcwd()
            folder_size = 0
            for (path, dirs, files) in os.walk(folder):
              for file in files:
                filename = os.path.join(path, file)
                folder_size += os.path.getsize(filename)
            
            cachelocal=cachesize+folder_size
            
            #Checks if incoming content is less than the local cache

            if (cachelocal <= availableSize):
              
              #Writes highest hits content to the local cache
              for key in cache:
                open(key, 'wb').writelines(cache[key])
              

              cache[cacheFilename]=response
              hits[cacheFilename]=1
              programHits[cacheFilename]=1
              sizeDict[cacheFilename]=incomingSize

              
              cachesize+=incomingSize
              
            else:

              #Removes low hit content to make room for relatively new content

              minSize=0

              while (minSize < cachesize):

                sorted_hits1=sorted(hits.items(), key=operator.itemgetter(1))
                p=sorted_hits1[:]
                q=p[0][0]
                minSize+=sizeDict[q]

                if q in hits.keys():
                  
                  del hits[q]
                  os.remove(q)

      except IOError:
        self.send_error(404, 'File not found')
        pass
      
      


      



if __name__ == '__main__':
    



 try:

  port , url = input()
  server_address = ('', int(port))
  #server = BaseHTTPServer.HTTPServer(server_address, httpHandler)
  server = ThreadingSimpleServer(server_address, httpHandler)
  print 'Starting server, use <Ctrl-C> to stop'
  
  if os.path.exists('hits.pickle'):
    with open('hits.pickle', 'rb') as handle:
      hits = pickle.load(handle) #Retrieves dictionaries from the local folder
  else:
    pass
  cachedir="CACHE"
  if  (not os.path.exists(cachedir)):
    os.mkdir(cachedir)
    os.chdir(cachedir)
  else:
    os.chdir(cachedir)
  
  server.serve_forever()

 except KeyboardInterrupt:
  os.chdir('..')
  with open('hits.pickle', 'wb') as handle: 
        pickle.dump(hits, handle) #Stores dictionaries into the local server

  server.socket.close()