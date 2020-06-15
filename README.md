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
freeing me from the hassles of platform dependencies
+ **pthread**
or similar. Included in the ''CMakeLists' file, a valid thread library is
sought at compile time.

### assumptions
+ the supported IP addresses are only v4

### design
0. all information regarding the surronding is checked and stored  
  + either through the GUI  
  + or manually filling the hosts file in config/  
1. via [secure copy](https://linux.die.net/man/1/scp) the necessary files are
copied to the user home directory
2. via [secure shell](https://linux.die.net/man/1/ssh) the '''compile''' script is
executed
