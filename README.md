# benchy
A tool for communication benchmarking in distributed systems within a local network

### introduction
this software lets you add your nodes local IP addresses and their role as **tester**
or a **testee**, more commonly known as server and client, allows you to virtually
define channels of communication between them and a span of time during which the
connectivity test will be performed for each of these channels.

### main dependencies
+ **python3**  
to perform high-end tasks like the GUI or handle the grpc framework

  + **grpcio** and **grpcio-tools**  
  to finely instruct hosts on their role and monitor their returning values  
  + **tkinter**  
  to run an interface in order to ease the process of building the
  configuration file needed to keep track of all nodes and their
  + **subprocess**
  to use threads from a thread-pool to reply to incoming requests

+ [**cmake**](https://cmake.org/)
Makefile constructing library that let me build, test and package my software,
freeing me from the hassles of platform and architecture dependencies, retaining
portability.
+ **pthread**
or similar. Included in the `CMakeLists` file, a valid thread library is
sought at compile time.

### assumptions
+ the supported IP addresses are only v4

### workflow
0. all information regarding the graph is checked and stored  
  + either through the GUI  
  + or manually filling the hosts file in `config/`  
1. via [secure copy](https://linux.die.net/man/1/scp) the necessary files are
copied to the user home directory
2. via [secure shell](https://linux.die.net/man/1/ssh) the `compile` script is
executed, which in turn runs local compilations to start a local Python
[grpc](https://grpc.io/docs/languages/python/quickstart/) server.
3. based on input edges, drawn between the hosts from the configuration file,
`master.py` then orchestrates the role-playing.
4. Once a command is received, the `slave.py` script
sifts the [proto buffer](https://developers.google.com/protocol-buffers/docs/pythontutorial)
request and either forks the C server or opens the client dynamic linked library.
5. `client.c`:  

   + receives `target` and `lifetime`
   + connects to `target`
   + sends `lifetime`
   + repeatedly asks the non-blocking socket for data until the select returns a timeout
6. `chat.c`:  

   + setup as to accept incoming requests from all IPv4 addresses through an agreed-upon port
   + creates a thread-pool and initiate a queue that all threads will be watching
   + repeatedly calling select on all connected sockets leads to a simple enqueue operation
    of the ready file descriptor or when a new connection comes in.
   + when a thread picks up a job, it waits for the first message to come in from the client,
    which will be the duration of the test for that client.
7. the python server re-encodes the returning value from our C clients back to the
  protobuf type needed to send the results of the tests.
8. the coordinating script waits for most processes to terminate before gathering
  the data and possibly come up with some graphical representation.  
