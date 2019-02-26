#!/bin/sh
#python /Users/jami/Workspace/networksLocalProxyServer.py

from socket import *
import sys
#aaaa

if len(sys.argv) <= 1:
	print('Usage : "python ProxyServer.py server_ip"\n[server_ip : It is the IP Address Of Proxy Server')
#	sys.exit(2)

# Create a server socket, bind it to a port and start listening
tcpSerSock = socket(AF_INET, SOCK_STREAM)
tcpSerPort = 8888
tcpSerSock.bind(("",tcpSerPort))
tcpSerSock.listen(1)
# Fill in start.
# Fill in end.
while 1:
	# Start receiving data from the client
	print('Ready to serve...')
	tcpCliSock, addr = tcpSerSock.accept()
	print('Received a connection from:', addr)
	message = tcpCliSock.recv(1024) 
	print('message')
	print(message)
	# Extract the filename from the given message
	#print('mes split 1')
	print(message.split()[1])
	filename = message.split()[1].partition("/")[2]
	print('FILE NAME:')
	print(filename)
	fileExist = "false"
	filetouse = "/" + filename
	print ("filetouse")
	print(filetouse)
	try:
		# Check wether the file exist in the cache
		print("First Try Block:")
		
		print("A")
		f = open(filetouse[1:], "r")
		print("B")
		outputdata = f.readlines()
		print("C")
		fileExist = "true"

		# ProxyServer finds a cache hit and generates a response message
		tcpCliSock.send("HTTP/1.0 200 OK\r\n")
		tcpCliSock.send("Content-Type:text/html\r\n")
		# Fill in start.
		for g in range(0, len(outputdata)):
			tcpCliSock.send(outputdata[g])
	
		# Fill in end
		print('Read from cache')
	# Error handling for file not found in cache
	except IOError:
		if fileExist == "false":
			print('inside')
			# Create a socket on the proxyserver
			c = socket(AF_INET,SOCK_STREAM)
			hostn = filename.replace("www.","",1)
			print("HOST NAME")
			print(hostn)
			try:
				# Connect to the socket to port 80
				print('made it to this point')
				c.connect(("ee.columbia.edu",80)) # needs to be a touple
				print("connection passed")
                
				# Fill in start.
               
				# Fill in end.
				# Create a temporary file on this socket and ask port 80 for the file requested by the client
				#fileobj = c.makefile('r', 0) #Instead of using send and recv, we can use makefile
				print('2')
				print('GET /' + filename +  ' HTTP/1.1\r\nHost: www.ee.columbia.edu\r\n\r\n')
				tcpCliSock.send('GET /' + filename +  ' HTTP/1.1\r\nHost: www.ee.columbia.edu\r\n\r\n')
				#fileobj.send('GET /' + filename +  ' HTTP/1.1\r\nHost: www.'+ hostn + '\r\n\r\n')
				#strHeader=str.encode("GET "+"http://" + filename + "HTTP/1.0\n\n")
				#print('3')
				#fileobj.write(strHeader) 
				print('4')
				#print(fileobj)	
				while True:
					response = tcpCliSock.recv(1024)
					if not response:
						break
					tcpCliSock.sendall(response)
					#print(response)
					print("BREAK")
					tmpFile.write(response)

				# Read the response into buffer
				# Fill in start.
				#buff = fileobj.readlines()
				# Fill in end.
				# Create a new file in the cache for the requested file.
				# Also send the response in the buffer to client socket and the corresponding file in the cache
				print('writing')
				tmpFile = open("./" + filename,"wb")
				print(tmpFile)
				for i in range(0,len(buff)):
					print(buff[i])
					tmpFile.write(buff[i])
					tcpCliSock.send(buff[i])
				print('wrote')
				#print(tmpFile.readlines())
				print('HIHI')
				# Fill in start.
				# Fill in end.
			except:
				print("Illegal request")
		else:
			# HTTP response message for file not found
			print '404: Not Found'
			# Fill in start.
			# Fill in end.
	# Close the client and the server sockets
	tcpCliSock.close()
	
# Fill in start.
tcpSerSock.close()
# Fill in end.
