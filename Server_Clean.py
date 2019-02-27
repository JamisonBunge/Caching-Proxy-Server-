from socket import *
import sys
if len(sys.argv) <= 1:
        print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
        sys.exit(2)
# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)

########################################################################################
# Fill in start.
tcpSerPort = 8888
tcpSerSock.bind(("",tcpSerPort))
tcpSerSock.listen(5)
# Fill in end.
########################################################################################

while 1:
    # Start receiving data from the client
    print('Ready to serve...')
    tcpCliSock, addr = tcpSerSock.accept()
    print('Received a connection from:', addr)

    ########################################################################################
    message = tcpCliSock.recv(1024)
    ########################################################################################
    
    print(message)
    # Extract the filename from the given message
    print(message.split()[1])
    filename = message.split()[1].partition("/")[2]
    print(filename)
    fileExist = "false"
    filetouse = "/" + filename
    print(filetouse)
    try:
        # Check wether the file exist in the cache
        f = open(filetouse[1:], "r")
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
            hostn = filename
            hostn = filename.replace("www.","",1)
            #print(hostn)
            try:           
                # Connect to the socket to port 80
                # Fill in start.
               # hostn = filename.replace("http://www.","",1)
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

                getL = "GET " + "http://" + filename + " HTTP/1.0\r\n\r\n"
                hostL = "Host: "+ hostn + "\r\n\r\n"
             


                a = open("getLog.txt", "a+")
                a.write(getL)
                
                a.write("BREAK\n")
                #a.close()
                print("1.1")

                fileobj.write(getL)#Host: " + hostn + "\r\n\r\n")
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
                #tmpFile = open("./" + filename,"wb")
               # print("./" + filename)
                print("3")
                ########################################################################################
                # Fill in start.
                for i in range(0, len(buff)):
                    a.write(buff[i])
                    #tmpFile.write(buff[i])
                    tcpCliSock.send(buff[i])
                print("4")
                #tmpFile.close()
                a.close()
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
tcpSerSock.close()
# Fill in end.