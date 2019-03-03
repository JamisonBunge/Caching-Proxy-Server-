#!/usr/bin/python2.7

from socket import *
import sys
import os
from threading import Thread,Lock

#Global Constants: not my code, need to modify
MAX_PENDING = 5
DIRECTORY_ROOT = "Cache"
WORKING_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
BUF_SIZE = 1024
EXIT_CODE = True
STATUS_LOOKUP = {200: "OK", 201: "Created", 202: "Accepted", 204: "No Content",
                 301: "Moved Permanently", 302: "Moved Temporarily", 304: "Not Modified",
                 400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
                 500: "Internal Server Error", 501: "Not Implemented", 502: "Bad Gateway", 503: "Service Unavailable"}

def main():
    
    #Create File Hierarchy
    makeDirectory(DIRECTORY_ROOT)
    os.chdir(DIRECTORY_ROOT)
    #Create Server Socket
    serverSocket = establishServer()
    print(WORKING_DIRECTORY)

    #Create a thread that will allow the user to kill the server from the terminal.
    #listenForUser = Thread(target=killServer, args=())
    #listenForUser.start()

    while True:

        # Start receiving data from the client
        print('Ready to serve...')
        clientSocket, addr = serverSocket.accept()
        print('Received a connection from:', addr)


        message = clientSocket.recv(BUF_SIZE)   

        b = open("messageLog.txt", "a+")
        b.write(message)
        b.write("\n")
        b.close()

        print(message)
        # Extract the filename from the given message
        #print(message.split()[1])
        filename = message.split()[1].partition("/")[2]
        #print(filename)
        fileExist = "false"
        filetouse = "/" + filename
        print("fileName: " + filetouse )
    #print(filetouse)
        try:
            # Check wether the file exist in the cache
            print("INSIDE")
            #try:
            fileToRead = filename.replace("/",".")
            fileToRead = "/" + fileToRead
            f = open(fileToRead[1:], "r")
            # except:
            #     print("fileToUse failed")
            #     raise IOError
            print("OPENED FILE")
            outputdata = f.readlines()
            fileExist = "true"

            # ProxyServer finds a cache hit and generates a response message
            clientSocket.send("HTTP/1.0 200 OK\r\n")
            clientSocket.send("Content-Type:text/html\r\n")
            ########################################################################################
            # Fill in start.
            for m in outputdata:
                clientSocket.send(m)
            # Fill in end.      
            ########################################################################################

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
                    os.chdir(WORKING_DIRECTORY + "/" + DIRECTORY_ROOT + "/" + hostn.replace("/","."))

                    hostNameForRequest = fileNameAsStringArray[0]
                    relativePath = "/" + fileNameAsStringArray[2]
                else:
                    relativePath = "/" + filename

                try:           
                    # Connect to the socket to port 80
                    print("00")
                    c.connect((hostn,80))
                    print("88")
           
                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    fileobj = c.makefile('r', 0) 
                    print("1")

                


                    #a = open("getLog.txt", "a+")
                    #a.write(getL)
                    
                    #a.write("BREAK\n")
                    #a.close()
                    print("1.1")

                    #Pass the arguments into the write lines using string format
                    fileobj.write("GET {object} HTTP/1.0\r\n".format(object=relativePath))
                    fileobj.write("Host: {host}\r\n\r\n".format(host=hostNameForRequest))
                    
                    #print the lines to the terminal 
                    print("GET {object} HTTP/1.0".format(object=relativePath))
                    print("Host: {host}\n".format(host=hostNameForRequest))
 
                    print("2")
                    # Read the response into buffer
    
                    # Fill in start.
                    buffer = fileobj.readlines()  
                    print("2.1")              
                    # Fill in end.


                    # Create a new file in the cache for the requested file.
                    writeName = filename.replace("/",".")
                    #print("writeName: " +writeName)
                    tmpFile = open("./" + writeName,"wb")
                   
                # print("./" + filename)
                    print("3")

                    # Fill in start.
                    for m in buffer:
                        #a.write(buff[i])
                        tmpFile.write(m)
                        #print(buff)
                        clientSocket.send(m)
                    print("4")
                    tmpFile.close()

                except:
                    print("Illegal request")
            else:
                # HTTP response message for file not found
                print '404: Not Found'
                response += "<html><body>\n" \
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

