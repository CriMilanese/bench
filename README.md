# benchy
A tool for communication benchmarking in distributed systems within a local network

### introduction
this software lets you add your nodes local IP addresses and their role as **tester**
or a **testee**, more commonly known as server and client, allows you to virtually
define channels of communication between them and a span of time during which the
connectivity test will be performed for each of these channels.

### dependencies
+ **python3**  
to perform high-end tasks like the GUI or handle the grpc framework

  **grpcio** and **grpcio-tools**  
  to finely instruct hosts on their role and monitor their returning values  
  **tkinter**  
  to run an interface in order to ease the process of building the
  configuration file needed to keep track of all nodes and their links
