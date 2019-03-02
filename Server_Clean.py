#!/usr/bin/python2.7

from socket import *
import sys
import os
from threading import Thread,Lock

#Global Constants: not my code, need to modify
MAX_PENDING = 5
MAX_BUFSIZE = 4096
EXIT_CODE = True
STATUS_LOOKUP = {200: "OK", 201: "Created", 202: "Accepted", 204: "No Content",
                 301: "Moved Permanently", 302: "Moved Temporarily", 304: "Not Modified",
                 400: "Bad Request", 401: "Unauthorized", 403: "Forbidden", 404: "Not Found",
                 500: "Internal Server Error", 501: "Not Implemented", 502: "Bad Gateway", 503: "Service Unavailable"}

def main():
    
    #Create File Hierarchy
    makeDirectory()
    #Create Server Socket
    #serverSocket = establishServer()
    #Create a thread that will allow the user to kill the server from the terminal.
    #listenForUser = Thread(target=killServer, args=())
    #listenForUser.start()
    serverSocket = socket(AF_INET, SOCK_STREAM)
    tcpSerPort = 8888  
    serverSocket.bind(("",tcpSerPort))
    serverSocket.listen(1)

    while True:
        # Start receiving data from the client
        print('Ready to serve...')
        tcpCliSock, addr = serverSocket.accept()
        print('Received a connection from:', addr)

        ########################################################################################
        message = tcpCliSock.recv(1024)
        ########################################################################################
        b = open("messageLog.txt", "a+")
        b.write(message)
        b.write("\n")
        b.close()

        #print(message)
        # Extract the filename from the given message
        print(message.split()[1])
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
            f = open(filetouse[1:], "r")
            # except:
            #     print("fileToUse failed")
            #     raise IOError
            print("OPENED FILE")
            outputdata = f.readlines()
            fileExist = "true"
            # ProxyServer finds a cache hit and generates a response message
            tcpCliSock.send("HTTP/1.0 200 OK\r\n")
            tcpCliSock.send("Content-Type:text/html\r\n")
            ########################################################################################
            # Fill in start.
            for g in range(0, len(outputdata)):
                tcpCliSock.send(outputdata[g])
            # Fill in end.      
            ########################################################################################

            print('Read from cache')
        # Error handling for file not found in cache
        except IOError:
            if fileExist == "false":
                # Create a socket on the proxyserver
                ########################################################################################
                c =  socket(AF_INET,SOCK_STREAM)
                ########################################################################################
                
                filenamePart = filename.partition("/")
                if "www." in filenamePart[0]:
                    hostn = filenamePart[0].replace("www.","",1)
                    print("HostName: " +hostn)
                    host_name = filenamePart[0]
                    local_path = "/" + filenamePart[2]
                else:
                    local_path = "/" + filename


                #hostn = filename
                # hostn = filename.replace("www.","",1)
                #
                # tempHost = hostn.split("/",1)[0]
                # print("TempHost: " +tempHost)
                try:           
                    # Connect to the socket to port 80
                    # Fill in start.
                    print("00")
                    c.connect((hostn,80))
                    print("88")
                    # Fill in end.
                    # Create a temporary file on this socket and ask port 80 for the file requested by the client
                    fileobj = c.makefile('r', 0) #Instead of using send and recv, we can use makefile
                    print("1")



                    #print("GET "+  filename + "HTTP/1.1\r\nHost: www.ee.columbia.edu\r\n\r\n")
                # print("Host: " + hostn + "\n\r")
                    
                                            #GET http://www.ee.columbia.edu/keren-bergman HTTP/1.10\r\n\r\n
                                            #GET http://www.ee.columbia.edu/keren-bergman HTTP/1.0\r\nHost: www.ee.columbia.edu/keren-bergman\n\n

                   # getL = "GET " + "http://" + filename + " HTTP/1.0\r\n\r\n"
                    #hostL = "Host: "+ hostn + "\r\n\r\n"
                


                    #a = open("getLog.txt", "a+")
                    #a.write(getL)
                    
                    #a.write("BREAK\n")
                    #a.close()
                    print("1.1")

                    #fileobj.write(getL)#Host: " + hostn + "\r\n\r\n")

                    fileobj.write("GET {object} HTTP/1.0\r\n".format(object=local_path))
                    fileobj.write("Host: {host}\r\n\r\n".format(host=host_name))
                    
                    print("GET {object} HTTP/1.0".format(object=local_path))
                    print("Host: {host}\n".format(host=host_name))
                    #fileobj.write(hostL)
                    #fileobj.write("\n\n")
                    #fileobj.write("\r\n")
                    #fileobj.write("Host: " + hostn + "\n\r")
                    print("2")
                    # Read the response into buffer
                    ########################################################################################
                    # Fill in start.
                    buff = fileobj.readlines()  
                    print("2.1")              
                    # Fill in end.
                    ########################################################################################
                    # Create a new file in the cache for the requested file.
                    # Also send the response in the buffer to client socketand the corresponding file in the cache
                    #fileN = "./" + filename + ".txt"
                    tmpFile = open("./" + filename,"w")
                # print("./" + filename)
                    print("3")
                    ########################################################################################
                    # Fill in start.
                    for line in buff:
                        #a.write(buff[i])
                        tmpFile.write(line)
                        print(buff)
                        tcpCliSock.send(line)
                    print("4")
                    tmpFile.close()
                    #a.close()
                    # Fill in end.
                    ########################################################################################
                except:
                    print("Illegal request")
            else:
                # HTTP response message for file not found
                ########### #############################################################################
                # Fill in start.
                print '404: Not Found'
                # Fill in end.
                ########################################################################################
        # Close the client and the server sockets
        tcpCliSock.close()
    # Fill in start.
    serverSocket.close()
    # Fill in end.



def establishServer():
    serverSocket = socket(AF_INET, SOCK_STREAM)
    tcpSerPort = 8888  
    serverSocket.bind(("",tcpSerPort))
    serverSocket.listen(5)
    return serverSocket




def makeDirectory():
    """
    This function creates the folder the files will be saved
    into as well as changes the working directory so the program 
    will write into the new folder 
    """
    
    dirName = 'Cache'

    try:

        os.mkdir(dirName)
        print(dirName + " directory created.")

    except OSError:
        print(dirName + " directory already exists")
    
    
    os.chdir(dirName) #Change the operating directory to write files into this folder 


def killServer():
    print("To close the server type \"exit\" at any time.")
    while 1:
        if raw_input("")=="exit":
            print("D")
            #sys.exit("The server has beeen stopped.")

if __name__ == '__main__':
    main()

