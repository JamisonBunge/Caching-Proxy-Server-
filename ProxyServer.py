#!/usr/bin/python2.7

"""
Internal Data-Structure Format
-----------------------------
**This information is explained in the READ_ME**

The cache information is stored in a dictionary called cachedFiles

    KEY ->      The filename formated so it can be written to the hard disk
    VALUE ->    A tuple that stores information used to see if the file is out of date 

    TUPLE FIELDS ->     0 -> Last-Modifed parameter from the the http response
                        NOTE: if this this was not found in the header then this value will be the time the request was made
                        1 -> The date the get reqeust was made / the date the saved file was created 
                        2 -> The path to the cached file within the created hierarchy 
                        3 -> hostname 
                        4 -> host for the GET request
                        5 -> file for the GET request 
"""

#IMPORTS
from socket import *
import sys
import os
from threading import Thread,Lock
from collections import namedtuple
from wsgiref.handlers import format_date_time
from datetime import datetime
from time import mktime

#GLOBAL VARS
cachedFiles = dict()
DIRECTORY_ROOT = "Cache"
BUF_SIZE = 1024
WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))


def main():
    #CREATE FILE HIERARCHY
    makeDirectory(DIRECTORY_ROOT)
    os.chdir(DIRECTORY_ROOT)

    #CREATE SERVER SOCKET
    serverSocket = establishServer()

    while True:

        #WAIT TO RECV DATA FROM THE CLIENT
        print('Ready to serve...')
        clientSocket, addr = serverSocket.accept()
        print('Received a connection from:', addr)


        message = clientSocket.recv(BUF_SIZE)   

        #print(message)
        # Extract the filename from the given message
        #print(message.split()[1])
        filename = message.split()[1].partition("/")[2]
        print(filename)
        fileExist = "false"
        filetouse = "/" + filename
 
        # CHECK TO SEE IF THE FILE EXISTS IN THE CACHE
        try:  
           
            
            #FORMATING STRINGS FOR USE BELOW
            fileToRead = filename.replace("/",".")
            fileToCheckTime = fileToRead 
            fileToRead = "/" + fileToRead

            #CHECK TO SEE IF THE FILE HAS BEEN CACHED THIS SESSION
            if fileToCheckTime in cachedFiles.keys():

                #OPEN THE FILE 
                #IF THE FILE DOES NOT EXIST AN IO-EXCEPTION WILL RAISE AND THE FILE WITH BE FETCHED
                f = open(fileToRead[1:], "r")
                fileExist = "true"

                #TUPLE PARAMS AS NAMED VARS FOR READABLITY 
                tupleResponse = cachedFiles.get(fileToCheckTime)

                savedDateLastMod =tupleResponse[0]
                savedDateCached = tupleResponse[1]
                savedActivePath = tupleResponse[2]
                savedHostn = tupleResponse[3]
                savedHostNameForRequest = tupleResponse[4]
                savedRelativePath = tupleResponse[5]

                #CHECK TO SEE IF MODIFED
                socketToCheckIfModded =  socket(AF_INET,SOCK_STREAM)
                socketToCheckIfModded.connect((savedHostn,80))

                #CREATE MAKE FILE FOR SEND/RECV 
                fileob = socketToCheckIfModded.makefile('r', 0) 
                   
                #WRITE TO THE MAKEFILE TO SEND THE HTTP REQUEST TO THE WEB SERVER
                fileob.write("GET {object} HTTP/1.0\r\n".format(object=savedRelativePath))
                fileob.write("Host: {host}\r\n".format(host=savedHostNameForRequest))
                fileob.write("If-Modified-Since: {date}\r\n\r\n".format(date=savedDateLastMod))

                #PRINT LINES TO THE TERMINAL 
                print("GET {object} HTTP/1.0".format(object=relativePath))
                print("Host: {host}".format(host=hostNameForRequest))
                print("If-Modified-Since: {date}\r\n\r\n".format(date=savedDateLastMod))

                #PARSE RESPONSE CODE FROM RESPONSE
                b = fileob.readline()
                responseCode=b.split(" ")[1]

                #CLOSE THE SOCKET
                socketToCheckIfModded.close()

                #DETERMINE ACTION BASED ON RESPONSE CODE
                if responseCode == "304":
                    
                    #THE CACHE IS UP TO DATE, STAY IN THE TRY BLOCK AND SEND THE FILE
                    print("Code 304: Cache is up to date.")
                    print("The saved file will be served")

                elif responseCode == "200":

                    #THIS IS AN AMBIGOUS RESPONSE. SOME WEBSITES ARE SENDING THIS EVEN WHEN THEY ARE UP TO DATE
                    #BECAUSE IT MAY BE OUT OF DATE, DELETE THE CACHED FILE AND FETCH A NEW VERSION 
                    print("Code 200: The Cache is either out of date or a 304 was not sent when it should have been.")
                    print("This is ambiguous so the server will delete the cached file and download a new one")
                    
                    #TRY AND REMOVE THE FILE
                    try:
                        os.remove("." + fileToRead)
                        print("file removed from disk")
                    except:
                        print("file could not be removed")

                    #REMOVE ENTRY FROM THE INTERNAL DATASTRUCT
                    del cachedFiles[fileToCheckTime]

                    #RAISE AN IOERROR SO A NEW RESPONSE CAN BE FETCHED
                    fileExist = "false"
                    raise IOError
                else:

                    #THIS IMPLEMTATION ONLY HANDLES 200, 404, AND 304 RESPONSES
                    #ALL OTHER RESPONESES AT THIS STAGE WILL BE TREATED AS 304 AND THE FILE WILL BE SERVED TO THE BROWSER
                    print("Received a response code, {code} that could not be understood by this implementation".format(code=responseCode))
                    print("The cached file will be served to the browser")

             

            else:
                
                #IF THE FILE WAS NOT CACHED IN THIS SESSION, FETCH IT BY RAISING AN IOERROR

                raise IOError

            #READ THE DATA FROM THE CACHED FILE
            outputdata = f.readlines()
            
            #raise IOError #DO NOT KEEP ME IN THIS CODE <---

            #RESPONSE MESSAGE FOR THE CLIENT
            clientSocket.send("HTTP/1.0 200 OK\r\n")
            clientSocket.send("Content-Type:text/html\r\n")

            #send data from the file to the client 
            #SEND DATA FROM THE CACHED FILE
            for m in outputdata:
                clientSocket.send(m)

            print('Read from cache')

        #ERROR HANDLING FOR THE FILE NOT BEING FOUND IN THE CACHE 
        #THIS BLOCK IS ALSO RAN WHEN A FILE IS FOUND BUT OUT OF DATE
        except IOError:
            if fileExist == "false":
                
                #SOCKET FOR FETCHING DATA FROM A WEBPAGE
                c =  socket(AF_INET,SOCK_STREAM)

                #GET FILEPATH AFTER THE FIRST SLASH
                fileNameAsStringArray = filename.partition("/")

                #IMPORTANT INFORMATION IN COMMENT BELOW 
                """
                Whenever a new host is going to be connected, we want to save
                all of the the associated files in a new folder. This way, the cached 
                files for each website can be grouped together.

                Also, hostn should only be changed when a "www." is detected. This is because all
                of the request following the first one sent do not include www.websiteName.com and a host
                name can not be parsed from this GET request alone. Changing the host name only under this condition
                fixes this problem.
                """

                #CHECK TO SEE IF THE GET REQUEST INCLDUES A WWW.
                if "www." in fileNameAsStringArray[0]: 
                    
                    #IF IT DOES, MAKE IT HOSTN FOR THE SOCKET CONNECTION
                    hostn = fileNameAsStringArray[0].replace("www.","",1)
                    print("HostName: " +hostn)
                    
                    #CHANGE DIRECTORY TO OUR LOCAL 'ROOT'
                    os.chdir(WORKING_DIRECTORY + "/" + DIRECTORY_ROOT)

                    #MAKE A NEW DIRECTORY FOR EVERY HOSTN, THIS WILL KEEP THE FILES GROUPED TOGETHER
                    makeDirectory(hostn.replace("/","."))

                    #MAKE A COPY OF THE DIRECTORY PATH, THIS WILL BE STORED IN THE INTERNAL DATASTRUCTURE
                    activePath = WORKING_DIRECTORY + "/" + DIRECTORY_ROOT + "/" + hostn.replace("/",".")

                    #CHANGE THE DIRECTORY TO THE ASSOSIATED HOST DIRECTORY
                    os.chdir(WORKING_DIRECTORY + "/" + DIRECTORY_ROOT + "/" + hostn.replace("/","."))

                    #KEEP A COPY OF THE HOST NAME BEFORE THE www. WAS REMOVED ; THIS WILL BE USED FOR THE GET REQUESTS 
                    hostNameForRequest = fileNameAsStringArray[0]

                    #FOR REQUESTS WITH WWW. RELATIVE PATH WILL BE THE INFORMATION AFTER THE FIRST SLASH
                    relativePath = "/" + fileNameAsStringArray[2]
                else:
                    relativePath = "/" + filename

                try:           
                    #CREATE SOCKET FOR WEB SERVER CONNECTION
                    c.connect((hostn,80))

                    #CREATE MAKE FILE FOR SEND/RECV 
                    fileobj = c.makefile('r', 0) 
        
                    #WRITE TO THE MAKEFILE TO SEND THE HTTP REQUEST TO THE WEB SERVER
                    fileobj.write("GET {object} HTTP/1.0\r\n".format(object=relativePath))
                    fileobj.write("Host: {host}\r\n\r\n".format(host=hostNameForRequest))

                    #PRINT LINES TO THE TERMINAL 
                    print("GET {object} HTTP/1.0".format(object=relativePath))
                    print("Host: {host}\n".format(host=hostNameForRequest))
 
                    #READ THE RESPONSE INTO THE BUFFER
                    buffer = fileobj.readlines() 

                    #CREATE A NEW FILE TO CACHE THE RESPONSE
                    writeName = filename.replace("/",".")
                    tmpFile = open("./" + writeName,"wb")
                   
                    #IF "Last-Modified:" IS NOT IN THE RESPONSE,USE THE CURRENT TIME 
                    now = datetime.now()
                    stamp = mktime(now.timetuple())
                    dateLastMod =  format_date_time(stamp)

                    #STREAM THE INFORMATION
                    for m in buffer:

                        #CHECK TO SEE IF LAST MODIFIED DATE WAS SENT
                        if "Last-Modified" in m:
                            dateLastMod = m.strip().split(' ', 1)[1]
                        
                        #WRITE TO CACHE FILE
                        tmpFile.write(m)

                        #SEND TO BROWSER
                        clientSocket.send(m)

                    #CLOSE THE CACHE FILE
                    tmpFile.close()

                    #ADD THIS INSTANCE TO THE INTERNAL DATASTRUCTURE
                    if writeName not in cachedFiles.keys():

                        #RECORD THE TIME THE FILE WAS CACHED
                        now = datetime.now()
                        stamp = mktime(now.timetuple())
                        dateCached =  format_date_time(stamp)
                        
                        #INSERT THE INFORMATION INTO THE DICTIONARY 
                        cachedFiles.update({writeName : (dateLastMod,dateCached,activePath,hostn,hostNameForRequest,relativePath)})

                except:
                    print("Illegal request")
            else:
                # HTTP RESPONSE FOR IF NOT FOUND 
                print ("404: Not Found")
                response = "<html><body>" + "<h1>" + "404: Not Found" + "</h1>" +"</body></html>"
                clientSocket.send("HTTP/1.0 404 NOT FOUND\r\n")
                clientSocket.send("Content-Type:text/html\r\n\r\n")
                clientSocket.send(response)

        #CLOSE THE CLIENT SOCKET
        clientSocket.close()
    #CLOSE THE SERVER
    serverSocket.close()

def establishServer():
    #SOCKET DECLORATION
    serverSocket = socket(AF_INET, SOCK_STREAM)
    tcpSerPort = 8888  
    serverSocket.bind(("",tcpSerPort))
    serverSocket.listen(10)
    return serverSocket

def makeDirectory(dirName):

    #IF THE DIRECTORY DOES NOT EXIST, CREATE IT
    try:
        os.mkdir(dirName)
        print(dirName + " directory created.")

    except OSError:
        print(dirName + " directory already exists")

if __name__ == '__main__':
    main()

