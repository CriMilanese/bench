#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <fcntl.h>
#include <unistd.h>
#include <arpa/inet.h>
#include <errno.h>
#include "client.h"
#include <signal.h>

#define RECV_CHUNK_SIZE 4 * 1024
#define PORT 8080
#define SA struct sockaddr
#define MAX_CONN_TRIALS 10

static float *results;

int recv_all(int *sockfd){
  // receive buffer init
	char *chunk = malloc(RECV_CHUNK_SIZE*sizeof(char));
	fd_set orig_set, copy_set;
  int rt, bytes_recv, total_recv = 0;

	FD_ZERO(&orig_set);
	FD_ZERO(&copy_set);
	FD_SET(*sockfd, &orig_set);

	while(1){

		copy_set = orig_set;
		// clear the receiving buffer
		memset(chunk, 0, RECV_CHUNK_SIZE*sizeof(char));

		rt = select(FD_SETSIZE, &copy_set, NULL, NULL, NULL);
		if (rt <= 0){
			break;
		} else {
			if(FD_ISSET(*sockfd, &copy_set)){
				bytes_recv = recv(*sockfd, chunk, RECV_CHUNK_SIZE*sizeof(char), 0);
				if(bytes_recv < 0){
					if(errno != EAGAIN && errno != EWOULDBLOCK){
						return EXIT_FAILURE;
					}
				} else if(chunk[0]==1 || bytes_recv==0){
						break;
				} else {
					total_recv += bytes_recv;
				}
				FD_CLR(*sockfd, &copy_set);
			}
		}
	}
	free(chunk);
	return total_recv;
}

double communicate(int *sockfd, int lifespan){
	char msg[16];
	int n = 0;
	int bytes_transferred = 0;

	sprintf(msg, "%d", lifespan);
	bytes_transferred = send(*sockfd, msg, strlen(msg), 0);
	if(bytes_transferred < 0)
		return EXIT_FAILURE;
	bytes_transferred = recv_all(sockfd);
	return ((bytes_transferred)*1e6/(lifespan*1e6));
}

double start(char* target_server, int lifetime){
	int sockfd, connfd;
	struct sockaddr_in servaddr;

	// socket create and verification
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd == -1)
		return EXIT_FAILURE;

	bzero(&servaddr, sizeof(servaddr));

	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = inet_addr(target_server);
	servaddr.sin_port = htons(PORT);

	// connect the client socket to server socket
	int trials = 0;
	while(connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
		if(trials == MAX_CONN_TRIALS){
			close(sockfd);
			return EXIT_FAILURE;
		}
		sleep(1);
		trials++;
	}

	// set the socket as non-blocking
  fcntl(sockfd, F_SETFL, O_NONBLOCK);

	double result = communicate(&sockfd, lifetime);
	close(sockfd);
  return result;
}

// to please compiler because I also want the exec for testing purposes
int main(int argc, char *argv[]) {
	char* t = argv[1];
	char *string_result[32];

	double result = start(t, 10);
	FILE *logfd = fopen("./log/logging_info", "w+");
	fprintf(logfd, "returning bandwidth: %f", result);
	fclose(logfd);
	return 0;
}
