#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <arpa/inet.h>
#include <fcntl.h>
#include <pthread.h>
#include "queue.h"

#define MAX 1024
#define PORT 8080
#define SA struct sockaddr
#define BACKLOG 10
#define TIMEOUT 10  // sec
#define MAX_JOBS 10
#define THREAD_POOL_SIZE 4

// shared data structure
struct Queue *q;
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
pthread_cond_t cond_var = PTHREAD_COND_INITIALIZER;

/*
*  This function is designed to send data to another device and read
*  the response back.
*  PARAM: file descriptor of opened socket
*/
void communicate(int *sockfd, FILE *logfd){
  // int curr_fd = *sockfd;
  char *buff = malloc(MAX * sizeof(char));

  // fill buffer with zeros
  memset(buff, 0, MAX*sizeof(char));

  while(1){
      // read the message from client and copy it in buffer
      while(recv(*sockfd, buff, MAX*sizeof(char), 0)<0);

      // the last iteration we break early by sending an exit message
      // to the client, which will terminate its loop too
      if(buff[0]==1)
        break;
      // and send that buffer back to client
      send(*sockfd, buff, MAX*sizeof(char), 0);
  }
  free(buff);
}

void *thread_func(void *input){
  // struct Queue *q_tmp = (struct Queue *)input;
  // free(input);
  int active_fd = 0;
  while(1){
    pthread_mutex_lock(&mutex);
    // fprintf((FILE *)input, "from other thread\n");
    // print_queue((FILE *)input, q);
    pthread_cond_wait(&cond_var, &mutex);
    active_fd = dequeue(q);
    // fprintf((FILE *)input, "%d\n", active_fd);
    pthread_mutex_unlock(&mutex);
    if(active_fd != 0){
      communicate(&active_fd, (FILE *)input);
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
  // fd_set master_write;
  // temporary file descriptor list for select()
  fd_set read_fds;
  // fd_set write_fds;

  // open a new fd instead of using stdout and stderr
  logfd = fopen("bench/server/log/server_log.txt", "w+");
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
    fprintf(logfd, "ERROR: Server-setsockopt() failed\n");
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
  // FD_ZERO(&master_write);
  FD_ZERO(&read_fds);
  // FD_ZERO(&write_fds);

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
    // write_fds = master_write;

    /* reinitialize timeout value*/
    expiration.tv_sec = TIMEOUT;

    int rt = select(maxfd+1, &read_fds, NULL, NULL, &expiration);
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
          FD_SET(newfd, &master_read); /* add to master set */
          if(newfd > maxfd){
            /* keep track of the maximum */
            maxfd = newfd;
          }
        } else {
          // data coming from an existing connection, we need to handle the message
          // output for parent process
          fprintf(logfd , "INFO: testing %s with fd: %d\n", inet_ntoa(client.sin_addr), i);
          pthread_mutex_lock(&mutex);
          enqueue(q, i);
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
