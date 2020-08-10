#ifndef CLIENT_H
#define CLIENT_H


/*
* the function gauges the time and bytes send to this very client
* and performs the maths to return the results for this test
* PARAM:
*  char* is the target server local IP address
*  int is the user-defined timeout for the test
*/
double start(char*, int);

/*
* the function gauges the time and bytes send to this very client
* and performs the maths to return the results for this test
* PARAM:
*  int* is the file descriptor obtained from connecting with the server
*  int is the user-defined timeout for the test
*  FILE* log file descriptor
*/
double communicate(int*, int, FILE*);

/*
* uses non blocking sockets in a select loop to keep reading until
* max bandwidth is reached or there is no more data.
* PARAM:
*  int* is the file descriptor obtained from connecting with the server
*  FILE* log file descriptor
*/
int recv_all(int*, FILE*);

#endif //CLIENT_H
