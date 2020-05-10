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
#define TRIALS 100
#define BACKLOG 10
#define TIMEOUT 10  // sec
#define MAX_JOBS 10
#define THREAD_POOL_SIZE 4

struct thread_args{
  struct Queue *which_queue;
  pthread_cond_t *c_var;
  FILE *logfile_descriptor;
  pthread_mutex_t *mtx;
};
/*
*  This function is designed to send data to another device and read
*  the respose back.
*  PARAM: file descriptor of opened socket
*/
void communicate(int *sockfd, FILE *logfd){
  fprintf(logfd, "entering communication process..");
  char *buff = malloc(MAX * sizeof(char));
  long *elapsed = malloc(TRIALS * sizeof(long));
  int avg_rtt = 0;
  int n = 0;
  struct timeval curr_tm, prev_tm;

  // init buffers with some bytes
  memset(buff, 0, MAX*sizeof(char));
  memset(elapsed, 0, TRIALS*sizeof(int));

  // the +1 is to end the connection
  while(n < (TRIALS + 1)){

      // the last iteration we break early by sending an exit message
      // to the client, which will terminate its loop too
      if(n == TRIALS){
        memset(buff, 1, MAX*sizeof(char));
        write(*sockfd, buff, MAX*sizeof(char));
        break;
      }

      gettimeofday(&prev_tm, NULL);
      // and send that buffer to client
      write(*sockfd, buff, MAX*sizeof(char));

      // fprintf(logfd , "trial number %d, message sent\n", n);
      // read the message from client and copy it in buffer
      while(read(*sockfd, buff, MAX*sizeof(char))<=0);

      gettimeofday(&curr_tm, NULL);

      elapsed[n] = ((curr_tm.tv_sec*1e6 + curr_tm.tv_usec) - (prev_tm.tv_sec*1e6 + prev_tm.tv_usec));
      avg_rtt += elapsed[n];
      n++;
  }
  free(buff);
  free(elapsed);
  fprintf(logfd , "INFO: avg RTT: %.2f us\n", (float)avg_rtt/TRIALS);
}

void *thread_func(void *input){
  struct Queue *q_tmp = (struct Queue *)input;
  free(input);
  while(1){
    int *active_fd;
    pthread_mutex_lock(((struct thread_args *)input)->mtx);
    active_fd = dequeue(((struct thread_args *)input)->which_queue);
    fprintf(((struct thread_args *)input)->logfile_descriptor, "[DEBUG] thread is running\n");
    if(active_fd != 0){
      communicate(active_fd, ((struct thread_args *)input)->logfile_descriptor);
    } else {
      fprintf(((struct thread_args *)input)->logfile_descriptor, "[DEBUG] thread is waiting\n");
      pthread_cond_wait(((struct thread_args *)input)->c_var, ((struct thread_args *)input)->mtx);
    }
  }
}

int main(){
  int master_socket_fd, len, maxfd, newfd;
  int opt = 1;
  FILE *logfd;

  struct sockaddr_in servaddr, client;
  struct Queue *q = createQueue(MAX_JOBS);
  pthread_t thread_pool[THREAD_POOL_SIZE];
  pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;
  pthread_cond_t cond_var = PTHREAD_COND_INITIALIZER;
  struct thread_args *t_args = (struct thread_args *)calloc(1,sizeof(struct thread_args));
  //local copy of list, cause select is disruptive
  fd_set master_read;
  fd_set master_write;
  // temporary file descriptor list for select()
  fd_set read_fds;
  fd_set write_fds;

  // open a new fd instead of using stdout and stderr
  logfd = fopen("server/log/server_log.txt", "w");
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
  FD_ZERO(&master_write);
  FD_ZERO(&read_fds);
  FD_ZERO(&write_fds);

  /* add the listening file descriptor to the master set */
  FD_SET(master_socket_fd, &master_read);

  /* initialize time value*/
  struct timeval expiration = {TIMEOUT, 0};

  /* initiliaze thread function arguments */
  t_args->c_var = &cond_var;
  t_args->which_queue = q;
  t_args->logfile_descriptor = logfd;
  t_args->mtx = &mutex;

  /* Initialize thread pool */
  for(int i=0; i<THREAD_POOL_SIZE; i++){
    pthread_create(&thread_pool[i], NULL, thread_func, (void *)t_args);
  }


  while(1){
    /* copy fds over, because select is disrupting */
    read_fds = master_read;
    write_fds = master_write;
    int rt = select(maxfd+1, &read_fds, &write_fds, NULL, &expiration);
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
          if((newfd = accept(master_socket_fd, (struct sockaddr *)&client, &len)) == -1){
            fprintf(logfd , "ERROR: server accept() failed..\n");
            return EXIT_FAILURE;
          }
          FD_SET(newfd, &master_write); /* add to master set */
          if(newfd > maxfd){
            /* keep track of the maximum */
            maxfd = newfd;
          }
      }
      // data coming from an existing connection, we need to handle the message
      else if (FD_ISSET(i, &write_fds)) {
          // output for parent process
          fprintf(logfd , "INFO: testing %s with fd: %d\n", inet_ntoa(client.sin_addr), i);
          pthread_mutex_lock(&mutex);
          enqueue(q, i);
          pthread_cond_signal(&cond_var);
          pthread_mutex_unlock(&mutex);
          FD_CLR(i, &master_write);
          close(i);
      }
    }
  } // while
  // close the socket when done with all clients
  free_queue(q);
  free(t_args);
  close(master_socket_fd);
  fclose(logfd);
  return EXIT_SUCCESS;
}
