Author: Jamison Bunge

The IP and Port: localhost,8888

Url format: localhost:8888/wwww.website.com



The data structure I use for cacheing:

I use a dictionary that has the filename as the key.
The value is a tuple that includes a bunch of relevant information.
I do not use all of the stored tuple information in the program. However, I left it in 
to possibly use for a further build out. A breakdown of the tuple information is as follows:

cachedFiles : dictionary

    KEY ->      The filename formatted so it can be written to the hard disk
    VALUE ->    A tuple that stores information used to see if the file is out of date 

    TUPLE FIELDS ->     0 -> Last-Modified parameter from the the http response
                        NOTE: if this this was not found in the header then this value will be the time the request was made
                        1 -> The date the get request was made / the date the saved file was created 
                        2 -> The path to the cached file within the created hierarchy 
                        3 -> hostname 
                        4 -> host for the GET request
                        5 -> file for the GET request 





BUG / NOTE:

I handle 'checking to see if file needs to be updated' by making a If-Modified-Since GET request when the file is 
found in the cashedFiles data structure. 

Some websites don't respond with a 304 response even when including "If-Modified-Since: {Last_Modified_Date}. 
For websites that give a 200 response to this GET request, I treat that file as if it is out of date. 
That means: 
	deleting the file,
	removing from the cachedFiles data structure, 
	and doing another GET request to obtain a new version of the file. 




Example websites where I don't have this problem.

http://localhost:8888/www.iczn.org
http://localhost:8888/www.sciaroidea.info
http://localhost:8888/www.weevil.myspecies.info
http://localhost:8888/www.ipaeg.org


Websites where I do have this issue:

http://localhost:8888/www.ee.columbia.edu
http://localhost:8888/www.google.com


	When this problem occurs, the files are still able to be cached. What's not working is the mechanism for verifying 
	the stored file is up to date. This does not happen on all websites. 




Bonus Points:

I refactored the original code to keep more useful information. For example: 

	reseting hostn only when it is appropriate
	keeping track of the Last_Modified line
	creating a file hierarchy where cached objects are grouped by their hostname 
	created a file naming convention to eliminate illegal characters from the write name
	restructuring the code into functions 







Other instructions:

	When reseting the server, it can be helpful to manually delete the created 'Cache' directory. This way, the cachedFiles data
	structure tracks ALL of the files. (File tracking does not persist when the program is restarted)

	When trying to run the server, if an error occurs where the socket address is already in use. 
	Use this bash command to kill the program:

		kill $(pgrep -f ProxyServer.py)


