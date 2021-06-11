#ifndef CHAT_H
#define CHAT_H

#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <pthread.h>
#include <errno.h>
#include "queue.h"

/* user defined constants */

#define INFO_BUFFER 16
#define SEND_CHUNK 4*1024
#define PORT 8080
#define SA struct sockaddr
#define BACKLOG 8  // holds a pool of maximum open ports
#define TIMEOUT 10  // sec
#define QUEUE_SIZE 8
#define THREAD_POOL_SIZE 4
#define WIN_TIME 1 // sec for each connection
#define CONNECTED (-1) // lifetime value before first contact

/* user defined global variables */

// the shared queue
extern struct Queue *q;

//shared mutex and conditional variable
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond_var = PTHREAD_COND_INITIALIZER;


int test_client(int*, FILE* , int);

void *terminate_client(int*, FILE*);

/*
*  This function is designed to send data to another device and read
*  the response back.
*  PARAM: file descriptor of opened socket
*/
int get_lifetime(int*, FILE*);

/*
* main thread function, each thread in the pool will loop through trying to get the lock
* and one will wait on a conditional variable to be signaled, meaning there is
* a job to dequeue
*/
void *thread_func(void*);

#endif
