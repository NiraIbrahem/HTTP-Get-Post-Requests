# HTTP-Requests
we will use sockets to implement a simple web client that communicates with a web server using a restricted subset of HTTP.
You are supposed to handle HTML, TXT and images. 
You should handle the both commands GET (to get file from the server) and POST (to send 
file to the server).  
You are required to add simple HTTP/1.1 support to your web server, consisting of persistent connections.You will also need to add some heuristics to your web server to determine when it will close a persistent connection.This timeout needs to be configured in the server and ideally should be dynamic based on the number of other active connections the server is currently supporting. 
