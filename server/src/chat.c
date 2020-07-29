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

#define MAX_BUFFER 16
#define SEND_CHUNK 4*1024
#define PORT 8080
#define SA struct sockaddr
#define BACKLOG 10  // holds a pool of maximum open ports
#define TIMEOUT 10  // sec
#define MAX_JOBS 10
#define THREAD_POOL_SIZE 4
#define WIN_TIME 1 // sec for each host

// shared data structure
struct Queue *q;

//shared mutex and conditional variable
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond_var = PTHREAD_COND_INITIALIZER;

int test_client(int *sockfd, FILE *logfd, char* lifetime){
  int sent = 0;

  struct timeval elapsed;
  fd_set orig_set, copy_set;
  int total_sent = 0;
  int lt = atoi(lifetime);
  char *chunk = malloc(SEND_CHUNK * sizeof(char));
  int rv = 0; // returning value for select

  FD_ZERO(&orig_set);
  FD_ZERO(&copy_set);
  FD_SET(sockfd, &orig_set);

  elapsed = {WIN_TIME, 0}; // 1 sec

  /*
    start sending chunks to the client until select will return the timeout,
    which indicates that the current time frame to test the current client has
    passed and its socket fd must be re-enqueued
  */
  while(1){
    copy_set = orig_set;
    rv = select(FD_SETSIZE, copy_set, NULL ,NULL, &elapsed);
    if(rv < 0){
      fprintf(logfd,"ERROR: server select() failed..\n");
      return EXIT_FAILURE;
    } else if (rv == 0){
      pthread_mutex_lock(&mutex);
      enqueue(q, *sockfd, lt);
      // fprintf(logfd , "from main thread\n");
      // print_queue(logfd, q);
      pthread_cond_signal(&cond_var);
      pthread_mutex_unlock(&mutex);
      break;
    }
    memset(chunk, 0, SEND_CHUNK * sizeof(char));
    if((sent = send(*sockfd, chunk, SEND_CHUNK*sizeof(char), 0)) < 0){
      if(errno == EAGAIN || errno == EWOULDBLOCK){
        fprintf(logfd, "send would block, maybe..\n");
        break;
      } else {
        fprintf(logfd, "sending chunk error\n");
      }
    } else {
      // fprintf(logfd, "%d bytes were sent\n", sent);
      total_sent += sent;
    }
  }
  free(chunk);
  return total_sent;
}

/*
*  This function is designed to send data to another device and read
*  the response back.
*  PARAM: file descriptor of opened socket
*/
void communicate(int *sockfd, FILE *logfd){
  char *buff = malloc(MAX_BUFFER * sizeof(char));
  int bytes_transferred  = 0;

  // fill buffer with zeros
  memset(buff, 0, MAX_BUFFER*sizeof(char));

  // read the message from client to assess its readiness
  bytes_transferred = recv(*sockfd, buff, MAX_BUFFER*sizeof(char), 0);
  fprintf(logfd, "bytes received: %d\n", bytes_transferred);
  fprintf(logfd, "content recevied: %s\n", buff);

  // the last iteration we break early by sending an exit message
  // to the server, which terminates the communication
  // if(buff[0]==1)
  //   break;

  // receive the expected timelife for this connection

  if(strcmp(buff, "ready") == 0){
    bytes_transferred = test_client(sockfd, logfd, buff);
  } else {
    fprintf(logfd, "client was not ready\n");
  }
  fprintf(logfd, "bytes sent: %d\n", bytes_transferred);
  free(buff);
}

// main thread function, each thread in the pool will loop through trying to get the lock
// and one will wait on a conditional variable to be signaled, meaning there is
// a job to dequeue
void *thread_func(void *output){
  int active_fd = 0;
  while(1){
    pthread_mutex_lock(&mutex);
    pthread_cond_wait(&cond_var, &mutex);
    active_fd = dequeue(q);
    pthread_mutex_unlock(&mutex);
    if(active_fd != 0){
      // make the socket non-blocking
      fcntl(active_fd, F_SETFL, O_NONBLOCK);
      // start the actual communication process
      communicate(&active_fd, (FILE *)output);
    }
  }
}

int main(){
  int master_socket_fd, len, maxfd, newfd;
  int opt = 1;
  FILE *logfd;

  struct sockaddr_in servaddr, client;
  pthread_t thread_pool[THREAD_POOL_SIZE];
  q = createQueue(MAX_JOBS);
  //local copy of list, cause select is disruptive
  fd_set master_read;
  // temporary file descriptor list for select()
  fd_set read_fds;

  // open a new fd instead of using stdout and stderr
  logfd = fopen("../server/log/server_log.txt", "w+");
  if(logfd == NULL){
    printf("ERROR: log file opening failed..\n");
    return EXIT_FAILURE;
  }

  // socket create and verification
  master_socket_fd = socket(AF_INET, SOCK_STREAM, 0);
  if (master_socket_fd == -1) {
      fprintf(logfd , "ERROR: socket creation failed...\n");
      return EXIT_SUCCESS;
  }
  bzero(&servaddr, sizeof(servaddr));

  // /*"address already in use" error message */
  if(setsockopt(master_socket_fd, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(int)) == -1){
    fprintf(logfd, "ERROR: Server setsockopt() failed\n");
    return EXIT_FAILURE;
  }

  // assign IP, PORT
  servaddr.sin_family = AF_INET;
  servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
  servaddr.sin_port = htons(PORT);

  // Binding newly created socket to given IP and verification
  if ((bind(master_socket_fd, (SA*)&servaddr, sizeof(servaddr))) != 0) {
      fprintf(logfd , "ERROR: socket bind failed...\n");
      return EXIT_FAILURE;
  }

  // Now server is ready to listen and verification
  if ((listen(master_socket_fd, BACKLOG)) != 0) {
      fprintf(logfd , "ERROR: Listen failed...\n");
      return EXIT_FAILURE;
  }

  len = sizeof(client);

  /* keep track of the biggest file descriptor starting from master */
  maxfd = master_socket_fd;

  // Accept the data packet from client and verification
  FD_ZERO(&master_read);
  FD_ZERO(&read_fds);

  /* add the listening file descriptor to the master set */
  FD_SET(master_socket_fd, &master_read);

  /* initialize time value*/
  struct timeval expiration = {TIMEOUT, 0};

  /* Initialize thread pool */
  for(int i=0; i<THREAD_POOL_SIZE; i++){
    pthread_create(&thread_pool[i], NULL, thread_func, (void *)logfd);
  }

  while(1){
    /* copy fds over, because select is disrupting */
    read_fds = master_read;

    int rt = select(maxfd+1, &read_fds, NULL, NULL, &expiration);
    /* reinitialize timeout value*/
    expiration.tv_sec = TIMEOUT;

    if((rt) == -1){
      fprintf(logfd,"ERROR: server select() failed..\n");
      return EXIT_FAILURE;
    } else if(rt == 0){
      fprintf(logfd, "time has expired....\n");
      break;
    }

    /*run through the existing connections looking for data to be read*/
    for(int i = 4; i <= maxfd; i++){
      // incoming connection for server
      if(FD_ISSET(i, &read_fds)){
        if(i == master_socket_fd){
          if((newfd = accept(master_socket_fd, (struct sockaddr *)&client, &len)) == -1){
            fprintf(logfd , "ERROR: server accept() failed..\n");
            return EXIT_FAILURE;
          }
          /* add to master set */
          FD_SET(newfd, &master_read);
          if(newfd > maxfd){
            /* keep track of the maximum */
            maxfd = newfd;
          }
        } else {
          // data coming from an existing connection, we need to handle the message
          // output for parent process
          fprintf(logfd , "INFO: testing %s with fd: %d\n", inet_ntoa(client.sin_addr), i);
          pthread_mutex_lock(&mutex);
          enqueue(q, i, 0);
          // fprintf(logfd , "from main thread\n");
          // print_queue(logfd, q);
          pthread_cond_signal(&cond_var);
          pthread_mutex_unlock(&mutex);
          FD_CLR(i, &master_read);
          // close(i);
        }
      }
    }
  } // while
  // close the socket when done with all clients
  free_queue(q);
  // free(t_args);
  close(master_socket_fd);
  fclose(logfd);
  return EXIT_SUCCESS;
}
