#!/usr/bin/python2.7

from socket import *
import sys
import os
from threading import Thread,Lock
from collections import namedtuple
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime
#import ordered_set

cachedFiles = dict()
DIRECTORY_ROOT = "Cache"
BUF_SIZE = 1024
WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))

"""
Internal Datastructure Format
-----------------------------


The cache information is stored in a dictionary called cachedFiles
KEY -> The filename formated so it can be written to the hard disk
VALUE -> A tuple that stores information used to see if the file is out of date 

    Tuple Feilds
        0 -> Last-Modifed parameter from the the http response
                NOTE: if this this was not found in the header then this value will be the time the request was made
        1 -> The date the get reqeust was made / the date the saved file was created 
        2 -> The path to the cached file within the created hierarchy 
        3 -> hostname 
        4 -> host for the GET request
        5 -> file for the GET request 

"""


#def proc():


def main():
    #Create File Hierarchy
    makeDirectory(DIRECTORY_ROOT)
    os.chdir(DIRECTORY_ROOT)
    #Create Server Socket
    serverSocket = establishServer()
    print(WORKING_DIRECTORY)

    #Create a thread that will allow the user to kill the server from the terminal.
    #listenForUser = Thread(target=killServer, args=(hello))
    #listenForUser.start()

    while True:

        # Start receiving data from the client
        print('Ready to serve...')
        clientSocket, addr = serverSocket.accept()
        print('Received a connection from:', addr)


        message = clientSocket.recv(BUF_SIZE)   

        #print(message)
        # Extract the filename from the given message
        #print(message.split()[1])
        filename = message.split()[1].partition("/")[2]
        #print(filename)
        fileExist = "false"
        filetouse = "/" + filename
 
        try:
            # Check wether the file exist in the cache
            
           
            fileToRead = filename.replace("/",".")
            fileToCheckTime = fileToRead 
            fileToRead = "/" + fileToRead
            print(fileToRead)
            print("A")
            ############################################################

            if fileToCheckTime in cachedFiles.keys():
                print("B")
                print(cachedFiles.get(fileToCheckTime))
                f = open(fileToRead[1:], "r")
                print("C")
                tupleResponse = cachedFiles.get(fileToCheckTime)
                print("D")

                #I am parsing all of the relevent information into seperate variables
                #This is not needed, I'm just doing it for readablity'

                savedDateLastMod =tupleResponse[0]
                savedDateCached = tupleResponse[1]
                savedActivePath = tupleResponse[2]
                savedHostn = tupleResponse[3]
                savedHostNameForRequest = tupleResponse[4]
                savedRelativePath = tupleResponse[5]

                #CHECK TO SEE IF MODIFED
                socketToCheckIfModded =  socket(AF_INET,SOCK_STREAM)
                socketToCheckIfModded.connect((savedHostn,80))

                fileob = socketToCheckIfModded.makefile('r', 0) 
                print("E")
                   
        
                #Pass the arguments into the write lines using string format
                fileob.write("GET {object} HTTP/1.0\r\n".format(object=savedRelativePath))
                print("F")
                fileob.write("Host: {host}\r\n".format(host=savedHostNameForRequest))
                print("G")
                fileob.write("If-Modified-Since: {date}\r\n\r\n".format(date=savedDateLastMod))
                print("H")


                #Print the lines
                print("GET {object} HTTP/1.0".format(object=relativePath))
                print("Host: {host}".format(host=hostNameForRequest))
                print("If-Modified-Since: {date}\r\n\r\n".format(date=savedDateLastMod))

                print("I")

                b = fileob.readline()
                
                s=b
                s=s.split(" ")
                responseCode = s[1]

                socketToCheckIfModded.close()

                if responseCode == "304":
                    print("Code 304: Cache is up to date.")
                    print("The saved file will be served")
                elif responseCode == "200":
                    print("Code 200: The Cache is either out of date or a 304 was not sent when it should have been.")
                    print("This is ambiguous so the server will delete the cached file and download a new one")
                    
                    try:
                        #os.chdir(savedActivePath)
                        print("j")
                        os.remove("." + fileToRead)
                        print("f")
                        #os.chdir(WORKING_DIRECTORY + "/" + DIRECTORY_ROOT)
                        print("d")
                        print("file removed from disk")
                    except:
                        print("file could not be removed")


                    del cachedFiles[fileToCheckTime]

                    #TODO: delete from dictionary

                    raise IOError
                else:
                    print("Received a response code, {code} that could not be understood by this implementation".format(code=responseCode))
                    print("The cached file will be served to the browser")
      

                print(s)
                print(s[1])

                print("J")

                
                
                


            else:
                print("Manually throwing IOError")
                raise IOError


            ############################################################
    
            print("OPENED FILE")
            outputdata = f.readlines()
            fileExist = "true"

            # ProxyServer finds a cache hit and generates a response message
            clientSocket.send("HTTP/1.0 200 OK\r\n")
            clientSocket.send("Content-Type:text/html\r\n")

            #send data from the file to the client 
            for m in outputdata:
                clientSocket.send(m)

            

            print('Read from cache')

        # Error handling for file not found in cache
        except IOError:
            if fileExist == "false":
                # Create a socket on the proxyserver
                
                c =  socket(AF_INET,SOCK_STREAM)

                """
                Break the filename into a string array 
                seperated by '/'. This will allow us to check to see if a new 
                host name exists so the socket connection can be reassigned
                """
                fileNameAsStringArray = filename.partition("/")

                if "www." in fileNameAsStringArray[0]: #
                    hostn = fileNameAsStringArray[0].replace("www.","",1)
                    print("HostName: " +hostn)
                    
                    """
                    Whenever a new host is going to be connected, we want to save
                    all of the the associated files in a new folder. This way, the cached 
                    files for each website can be grouped together.
                    """
                    os.chdir(WORKING_DIRECTORY + "/" + DIRECTORY_ROOT)
                    makeDirectory(hostn.replace("/","."))
                    #changeDirectory(hostn.replace("/","."))
                    activePath = WORKING_DIRECTORY + "/" + DIRECTORY_ROOT + "/" + hostn.replace("/",".")
                    os.chdir(WORKING_DIRECTORY + "/" + DIRECTORY_ROOT + "/" + hostn.replace("/","."))

                    hostNameForRequest = fileNameAsStringArray[0]
                    relativePath = "/" + fileNameAsStringArray[2]
                else:
                    relativePath = "/" + filename

                try:           
                    # Connect to the socket to port 80
                    print("00")
                    c.connect((hostn,80))
                    print("01")
                    #print(time.gmtime(0))
                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    fileobj = c.makefile('r', 0) 
                    print("1")
        
                    #Pass the arguments into the write lines using string format
                    fileobj.write("GET {object} HTTP/1.0\r\n".format(object=relativePath))
                    fileobj.write("Host: {host}\r\n\r\n".format(host=hostNameForRequest))

                    #print the lines to the terminal 
                    print("GET {object} HTTP/1.0".format(object=relativePath))
                    print("Host: {host}\n".format(host=hostNameForRequest))
 
                    print("2")
                    # Read the response into buffer
    
                    buffer = fileobj.readlines() 
                    print("2.1")              
                    # Fill in end.


                    # Create a new file in the cache for the requested file.
                    writeName = filename.replace("/",".")
                    #print("writeName: " +writeName)
                    tmpFile = open("./" + writeName,"wb")
                   
                    print("3")



                    now = datetime.now()
                    stamp = mktime(now.timetuple())
                    dateLastMod =  format_date_time(stamp)

                    # Fill in start.
                    for m in buffer:
                        if "Last-Modified" in m:
                            dateLastMod = m.strip().split(' ', 1)[1]
                            print("HEY ITS ME THE GUY YOUR LOOKING FOR : " + dateLastMod)
                        tmpFile.write(m)
                        clientSocket.send(m)
                    #print("4")
                    
                    tmpFile.close()
                    
          
                    rWriteName = "/" + writeName
                    # f = open(rWriteName[1:], "r")
                    print("5")


                    now = datetime.now()
                    stamp = mktime(now.timetuple())
                    dateCached =  format_date_time(stamp)

                    #
                    # for line in f:
                    #     if "Last-Modified" in line:
                    #         dateLastMod = line.strip().split(' ', 1)[1]
                    #         print(dateLastMod)
                    #         break
                    # f.close()
                    #print("6")

                    if writeName not in cachedFiles.keys():
                        now = datetime.now()
                        stamp = mktime(now.timetuple())
                        dateCached =  format_date_time(stamp)
                        
                        cachedFiles.update({writeName : (dateLastMod,dateCached,activePath,hostn,hostNameForRequest,relativePath)})



                except:
                    print("Illegal request")
            else:
                # HTTP response message for file not found
                print '404: Not Found'
                response = "<html><body>\n" \
                "<h1>" + "404: Not Found" + "</h1>\n" \
                "</body></html>\n"
                clientSocket.send(response)
                # Fill in end.
                ########################################################################################
        # Close the client and the server sockets
        clientSocket.close()
    # Fill in start.
    serverSocket.close()
    # Fill in end.

#def getModitfiedTime(host,filename)
  #  fileobj.write("GET {object} HTTP/1.0\r\n".format(object=relativePath))
  # fileobj.write("Host: {host}\r\n\r\n".format(host=hostNameForRequest))



def establishServer():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    tcpSerPort = 8888  
    serverSocket.bind(("",tcpSerPort))
    serverSocket.listen(5)
    return serverSocket




def makeDirectory(dirName):
    """
    This function creates the folder the files will be saved
    into as well as changes the working directory so the program 
    will write into the new folder 
    """

    try:
        os.mkdir(dirName)
        print(dirName + " directory created.")

    except OSError:
        print(dirName + " directory already exists")
 
def changeDirectory(dirName):
    print(os.chdir(os.path.dirname(os.path.realpath(__file__))))
    #os.chdir(DIRECTORY_ROOT)
    #os.chdir(dirName)

def killServer():
    print("To close the server type \"exit\" at any time.")
    while 1:
        if raw_input("")=="exit":
            print("D")
            #sys.exit("The server has beeen stopped.")

if __name__ == '__main__':
    main()

