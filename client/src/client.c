#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <fcntl.h>
#include <unistd.h>
#include <arpa/inet.h>
#include "client.h"

#define MAX_BUFFER 1024 * 1024 // 1 MB
#define TRANSFER_SIZE 4096
#define RECV_CHUNK_SIZE 512
#define PORT 8080
#define SA struct sockaddr
#define MAX_TRIALS 10
#define TESTS 1
#define RESULTS_NUM 2
#define BW_OPTION 1
#define RTT_OPTION 0
#define TIMEOUT 5

int recv_all(int sockfd, FILE *logfd, ssize_t bytes_sent){
  // receive buffer init
	char *chunk = malloc(RECV_CHUNK_SIZE*sizeof(char));
	fd_set set;
	struct timeval tm_out;
  int rt = 0;
	int bytes_recv = 0;
	int total_recv = 0;


	while(1){
		FD_ZERO(&set);
		FD_SET(sockfd, &set);

		// clear the receiving buffer
		memset(chunk, 0, RECV_CHUNK_SIZE*sizeof(char));

		rt = select(FD_SETSIZE, &set, NULL, NULL, &tm_out);

		// reset the timeout
		tm_out.tv_sec = TIMEOUT;

		if (rt < 0){
			fprintf(logfd, "select error\n");
		} else if (rt == 0){
			fprintf(logfd, "receiving timeout..\nexit..\n");
			break;
		} else {
			if(FD_ISSET(sockfd, &set)){
				bytes_recv = recv(sockfd, chunk, RECV_CHUNK_SIZE*sizeof(char), 0);
				fprintf(logfd, "%d bytes were received\n", bytes_recv);
				total_recv += bytes_recv;
			} else {
				fprintf(logfd, "sockfd is not set (FD_ISSET)\n");
			}
		}
		FD_CLR(sockfd, &set);
	}

	free(chunk);
	return total_recv;
}

float *communicate(int sockfd, FILE *logfd, float* results)
{
	char *buff = malloc(MAX_BUFFER * sizeof(char));
	struct timeval curr_tm, rtt_tm, bw_tm;
  long sum_rtt, sum_bw = 0;
	int n = 0;
	int bytes_transferred = 0;

	memset(buff, 0, MAX_BUFFER*sizeof(char));
	while(n <= TESTS){

		if (n == TESTS) {
			memset(buff, 1, MAX_BUFFER*sizeof(char));
      send(sockfd, buff, TRANSFER_SIZE*sizeof(char), 0);
			break;
		}
		gettimeofday(&rtt_tm, NULL);
		bytes_transferred = send(sockfd, buff, TRANSFER_SIZE*sizeof(char), 0);
		if(bytes_transferred < 0){
			fprintf(logfd, "send error\n");;
		} else {
			fprintf(logfd, "bytes sent: %d\n", bytes_transferred);
		}
		gettimeofday(&bw_tm, NULL);
		bytes_transferred = recv_all(sockfd, logfd, TRANSFER_SIZE*sizeof(char));
		gettimeofday(&curr_tm, NULL);

		fprintf(logfd, "total bytes received: %d\n", bytes_transferred);

		sum_rtt += ((curr_tm.tv_sec*1e6 + curr_tm.tv_usec) - (rtt_tm.tv_sec*1e6 + rtt_tm.tv_usec));
		sum_bw += ((curr_tm.tv_sec*1e6 + curr_tm.tv_usec) - (bw_tm.tv_sec*1e6 + bw_tm.tv_usec));
		n++;
	}
	results[RTT_OPTION] = (float)sum_rtt/TESTS;
	results[BW_OPTION] = ((bytes_transferred/TESTS)*1e6/((float)sum_bw/TESTS));
	free(buff);
	return results;
}


int main(int argc, char const *argv[])
{
	int sockfd, connfd;
	float *results = malloc(RESULTS_NUM * sizeof(float));
	struct sockaddr_in servaddr;
	FILE *logfd;

	logfd = fopen("bench/client/log/client_log.txt", "a+");
	if(logfd == NULL){
		printf("CLIENT LOG FILE FAILED\n");
		return EXIT_FAILURE;
	}

	if(argc < 2){
		fprintf(logfd, "ERROR: target server ip missing\n");
		fclose(logfd);
		return EXIT_FAILURE;
	}

	// init results buffer
	memset(results, 0, RESULTS_NUM*sizeof(float));

	// socket create and verification
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd == -1) {
		fprintf(logfd,"ERROR: socket creation failed...\n");
		exit(0);
	}
	bzero(&servaddr, sizeof(servaddr));

	// assign IP, PORT
	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = inet_addr(argv[1]);
	servaddr.sin_port = htons(PORT);

	// connect the client socket to server socket
	int trials = 0;
	while(connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
		if(trials == MAX_TRIALS){
			fprintf(logfd, "ERROR: server was unreachable\n");
			fclose(logfd);
			return EXIT_FAILURE;
		}
		sleep(1);
		fprintf(logfd,"connection with the server failed...\n");
		trials++;
	}

	// set the socket as non-blocking
  fcntl(sockfd, F_SETFL, O_NONBLOCK);

	// function for chat
	results = communicate(sockfd, logfd, results);
	fprintf(logfd, "avg round trip time with %s is %.2f us\n", inet_ntoa(servaddr.sin_addr), results[RTT_OPTION]);
	fprintf(logfd, "avg bandwidth with %s is %.2f KB/s\n", inet_ntoa(servaddr.sin_addr), results[BW_OPTION]);
	// close the file pointers
	free(results);
	fclose(logfd);
	close(sockfd);
  return EXIT_SUCCESS;
}
