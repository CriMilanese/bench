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

int recv_all(int *sockfd, FILE *logfd){
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
		if (rt < 0){
			fprintf(logfd, "select error\n");
			break;
		} else if (rt == 0){
			fprintf(logfd, "receiving timeout..\nexit..\n");
			break;
		} else {
			if(FD_ISSET(*sockfd, &copy_set)){
				bytes_recv = recv(*sockfd, chunk, RECV_CHUNK_SIZE*sizeof(char), 0);
				if(bytes_recv < 0){
					if(errno == EAGAIN || errno == EWOULDBLOCK){
						fprintf(logfd, "recv would block\n");
						// continue;
					} else {
						fprintf(logfd, "receiving chunk error\n");
					}
				} else if(chunk[0]==1){
						fprintf(logfd, "terminator received\n");
						break;
				} else if(!bytes_recv){
					fprintf(logfd, "terminating for the wrong reason\n");
					break;
				} else {
					total_recv += bytes_recv;
				}
				FD_CLR(*sockfd, &copy_set);
			} else {
				fprintf(logfd, "sockfd is not set (FD_ISSET)\n");
			}
		}
	}
	free(chunk);
	return total_recv;
}

double communicate(int *sockfd, int lifespan, FILE *logfd){
	char msg[16];
	struct timeval curr_tm, rtt_tm, bw_tm;
  long sum_bw = 0;
	int n = 0;
	int bytes_transferred = 0;

	sprintf(msg, "%d", lifespan);
	bytes_transferred = send(*sockfd, msg, strlen(msg), 0);
	if(bytes_transferred < 0)
		return EXIT_FAILURE;
	gettimeofday(&bw_tm, NULL);
	bytes_transferred = recv_all(sockfd, logfd);
	gettimeofday(&curr_tm, NULL);

	fprintf(logfd, "total bytes received: %d\n", bytes_transferred);

	sum_bw += (((curr_tm.tv_sec)*1e6 + curr_tm.tv_usec) - (bw_tm.tv_sec*1e6 + bw_tm.tv_usec));

	return ((bytes_transferred)*1e6/(sum_bw));
}

double start(char* target_server, int lifetime){
	int sockfd, connfd;
	struct sockaddr_in servaddr;
	FILE *logfd;
	//
	logfd = fopen("../client/log/client_log.txt", "a+");
	if(logfd == NULL){
		printf("CLIENT LOG FILE FAILED\n");
		return EXIT_FAILURE;
	}
	// logfd = stdout;
	// socket create and verification
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd == -1)
		return EXIT_FAILURE;

	bzero(&servaddr, sizeof(servaddr));

	fprintf(logfd, "[DEBUG] trying to connect to: %s\n", target_server);
	// assign IP, PORT
	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = inet_addr(target_server);
	servaddr.sin_port = htons(PORT);

	// connect the client socket to server socket
	int trials = 0;
	while(connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
		if(trials == MAX_CONN_TRIALS){
			fprintf(logfd, "ERROR: server was unreachable\n");
			fclose(logfd);
			close(sockfd);
			return EXIT_FAILURE;
		}
		sleep(1);
		fprintf(logfd,"connection with the server failed...\n");
		trials++;
	}

	// set the socket as non-blocking
  fcntl(sockfd, F_SETFL, O_NONBLOCK);

	// function for chat
	double result = communicate(&sockfd, lifetime, logfd);
	fprintf(logfd, "avg bandwidth with %s is %.2f KB/s\n", inet_ntoa(servaddr.sin_addr), result);
	fclose(logfd);
	close(sockfd);
  return result;
}

// to please compiler because I also want the exec for testing purposes
int main(int argc, char *argv[]) {
	char* t = argv[1];
	float result = start(t, 10);
	printf("%.2f\n", result);
	return 0;
}
