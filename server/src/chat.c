
#include <stdio.h>
#include <stdlib.h>
#include <netdb.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>
#define MAX 1024
#define PORT 8080
#define SA struct sockaddr
#define TRIALS 100

/*
*  This function is designed to send data to another device and read
*  the respose back.
*  PARAM: file descriptor of opened socket
*/
void func(int sockfd)
{
    char *buff = malloc(MAX * sizeof(char));
    int *elapsed = malloc(TRIALS * sizeof(int));
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
          printf("Server Exit...\n");
          break;
        }

        gettimeofday(&prev_tm, NULL);
        // and send that buffer to client
        write(sockfd, buff, MAX*sizeof(char));

        printf("trial number %d, message sent\n", n);
        // read the message from client and copy it in buffer
        while(read(sockfd, buff, MAX*sizeof(char))<=0);

        gettimeofday(&curr_tm, NULL);

        elapsed[n] = ((curr_tm.tv_usec - prev_tm.tv_usec));
        avg_rtt += elapsed[n];
        // print buffer which contains the client contents
        printf("back from client in: %d us\n", elapsed[n]);
        n++;
    }
    free(buff);
    free(elapsed);
    printf("the average round trip time is: %f us\n", (float)avg_rtt/TRIALS);
}

int main()
{
    int sockfd, connfd, len;
    struct sockaddr_in servaddr, cli;

    // socket create and verification
    sockfd = socket(AF_INET, SOCK_STREAM, 0);
    if (sockfd == -1) {
        printf("socket creation failed...\n");
        return 0;
    }
    else
        printf("Socket successfully created..\n");
    bzero(&servaddr, sizeof(servaddr));

    // assign IP, PORT
    servaddr.sin_family = AF_INET;
    servaddr.sin_addr.s_addr = htonl(INADDR_ANY);
    servaddr.sin_port = htons(PORT);

    // Binding newly created socket to given IP and verification
    if ((bind(sockfd, (SA*)&servaddr, sizeof(servaddr))) != 0) {
        printf("socket bind failed...\n");
        return 0;
    }
    else
        printf("Socket successfully binded..\n");

    // Now server is ready to listen and verification
    if ((listen(sockfd, 5)) != 0) {
        printf("Listen failed...\n");
        return 0;
    }
    else
        printf("Server listening..\n");
    len = sizeof(cli);

    // Accept the data packet from client and verification
    connfd = accept(sockfd, (SA*)&cli, &len);
    if (connfd < 0) {
        printf("server accept failed...\n");
        return 0;
    }
    else
        printf("server accept the client...\n");

    // Function for chatting between client and server
    func(connfd);

    // After chatting close the socket
    close(sockfd);
}
