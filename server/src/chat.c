#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#include <arpa/inet.h>
#define MAX 1024
#define PORT 8080
#define SA struct sockaddr
#define TRIALS 100
#define BACKLOG 5
#define TIMEOUT 10  // sec

/*
*  This function is designed to send data to another device and read
*  the respose back.
*  PARAM: file descriptor of opened socket
*/
void func(int sockfd)
{
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
          write(sockfd, buff, MAX*sizeof(char));
          printf("test done..\n");
          break;
        }

        gettimeofday(&prev_tm, NULL);
        // and send that buffer to client
        write(sockfd, buff, MAX*sizeof(char));

        // printf("trial number %d, message sent\n", n);
        // read the message from client and copy it in buffer
        while(read(sockfd, buff, MAX*sizeof(char))<=0);

        gettimeofday(&curr_tm, NULL);

        elapsed[n] = ((curr_tm.tv_sec*1e6 + curr_tm.tv_usec) - (prev_tm.tv_sec*1e6 + prev_tm.tv_usec));
        avg_rtt += elapsed[n];
        n++;
    }
    free(buff);
    free(elapsed);
    printf("the average round trip time is: %f us\n", (float)avg_rtt/TRIALS);
}

int main()
{
    int master_socket_fd, len, maxfd, newfd, rt;

    struct sockaddr_in servaddr, client;

    char *welcome_msg = "welcome to this server";
    int opt = 1;

    fd_set master;
    // temp file descriptor list for select()
    fd_set read_fds;
    // clear the master and temp sets
    FD_ZERO(&master);
    FD_ZERO(&read_fds);
    // socket create and verification
    master_socket_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (master_socket_fd == -1) {
        printf("socket creation failed...\n");
        return EXIT_SUCCESS;
    }
    else
        printf("Socket successfully created..\n");
    bzero(&servaddr, sizeof(servaddr));

    /*"address already in use" error message */
    if(setsockopt(master_socket_fd, SOL_SOCKET, SO_REUSEADDR, (char *)&opt, sizeof(int)) == -1){
      printf("Server-setsockopt() failed\n");
      return EXIT_FAILURE;
    }

    // assign IP, PORT
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(PORT);

    // Binding newly created socket to given IP and verification
    if ((bind(master_socket_fd, (SA*)&servaddr, sizeof(servaddr))) != 0) {
        printf("socket bind failed...\n");
        return EXIT_FAILURE;
    }
    else
        printf("Socket successfully binded..\n");

    // Now server is ready to listen and verification
    if ((listen(master_socket_fd, BACKLOG)) != 0) {
        printf("Listen failed...\n");
        return EXIT_FAILURE;
    }
    else
        printf("Server listening..\n");

    FD_SET(master_socket_fd, &master);
    len = sizeof(client);
    /* add the listening file descriptor to the master set */
    /* keep track of the biggest file descriptor */
    maxfd = master_socket_fd; /* so far, it's this one*/
    // printf("max_fd is: %d\n", maxfd);

    // Accept the data packet from client and verification
    while(1){
      struct timeval expiration = {TIMEOUT, 0};
      /* copy fds over, because select is disrupting */
      int tmp_maxfd = maxfd;
      memcpy(&read_fds, &master, sizeof(master));
      if(rt = select(tmp_maxfd+1, &read_fds, NULL, NULL, NULL) == -1){
        printf("Server-select() failed..\n");
        return EXIT_FAILURE;
      // } else if (rt == 0) {
      //   printf("Listening has timed out\n");
      //   return EXIT_SUCCESS;
      }

      // check the available number of fds
      printf("[DEBUG] rt is: %d\n", rt);

      /*run through the existing connections looking for data to be read*/
      for(int i = 0; i <= maxfd; i++){
        if(FD_ISSET(i, &read_fds)){
          if(i == master_socket_fd){
             /* handle new connections */
            if((newfd = accept(master_socket_fd, (struct sockaddr *)&client, &len)) == -1){
              printf("Server-accept() failed..\n");
              return EXIT_FAILURE;
            }
            FD_SET(newfd, &master); /* add to master set */
            if(newfd > maxfd){
              /* keep track of the maximum */
              maxfd = newfd;
            }
            // printf("New connection from %s on socket %d\n", inet_ntoa(client.sin_addr), newfd);
            if(write(newfd, welcome_msg, strlen(welcome_msg))<0){
                printf("welcome message failed..\n");
            }
          } else {
            // data coming from an existig connection, we need to handle the message
            func(i);
            close(i);
            FD_CLR(i, &master);
          }
        }
      }
    }

    // close the socket when done with all clients
    close(master_socket_fd);
    return EXIT_SUCCESS;
}
