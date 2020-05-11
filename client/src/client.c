#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/time.h>
#include <unistd.h>
#include <arpa/inet.h>

#define MAX 1024
#define PORT 8080
#define SA struct sockaddr
#define MAX_TRIALS 10
#define TESTS 10

void func(int sockfd, FILE *logfd)
{
	char *buff = malloc(MAX * sizeof(char));
	// long *elapsed = malloc(TESTS * sizeof(long));
	struct timeval curr_tm, prev_tm;
  long sum_rtt = 0;
	int n = 0;
	memset(buff, 0, MAX*sizeof(char));
	// memset(elapsed, 0, TESTS*sizeof(char));
	while(n <= TESTS){

		if (n == TESTS) {
			memset(buff, 1, MAX*sizeof(char));
      send(sockfd, buff, MAX*sizeof(char), 0);
			break;
		}
		gettimeofday(&prev_tm, NULL);
		send(sockfd, buff, MAX*sizeof(char), 0);

		while(recv(sockfd, buff, MAX*sizeof(char), 0)<0);
    gettimeofday(&curr_tm, NULL);

		sum_rtt += ((curr_tm.tv_sec*1e6 + curr_tm.tv_usec) - (prev_tm.tv_sec*1e6 + prev_tm.tv_usec));
		n++;
	}
	// free(elapsed);
	free(buff);
	fprintf(logfd, "avg trip time %.2f\n", (float)sum_rtt/TESTS);
}


int main(int argc, char const *argv[])
{
	int sockfd, connfd;
	struct sockaddr_in servaddr;
	FILE *logfd;

	if(argc < 2){
		fprintf(logfd, "ERROR: target server ip missing\n");
		return EXIT_FAILURE;
	}

	logfd = fopen("bench/client/log/client_log.txt", "a+");
	if(logfd == NULL){
		printf("CLIENT LOG FILE FAILED\n");
		return EXIT_FAILURE;
	}

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
		sleep(5);
		fprintf(logfd,"connection with the server failed...\n");
		trials++;
	}


	// function for chat
	func(sockfd, logfd);
	fclose(logfd);
	// close the socket
	close(sockfd);
  return EXIT_SUCCESS;
}
