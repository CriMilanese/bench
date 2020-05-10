#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
// #include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#define MAX 1024
#define PORT 8080
#define SA struct sockaddr
#define MAX_TRIALS 10

void func(int sockfd)
{
	char *buff = malloc(MAX * sizeof(char));
	memset(buff, 0, MAX*sizeof(char));
	while(1){

		read(sockfd, buff, MAX*sizeof(char));

		if (buff[0] == 1) {
			break;
		}

		write(sockfd, buff, MAX*sizeof(char));
	}
	free(buff);
}


int main(int argc, char const *argv[])
{
	int sockfd, connfd;
	struct sockaddr_in servaddr;
	FILE *logfd;

	logfd = fopen("bench/client/log/client_log.txt", "w");
	if(logfd == NULL){
		printf("CLIENT LOG FILE FAILED\n");
		return EXIT_FAILURE;
	}

	if(argc < 2){
		fprintf(logfd, "ERROR: target server ip missing\n");
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
		sleep(1);
		fprintf(logfd,"connection with the server failed...\n");
		trials++;
	}


	// function for chat
	func(sockfd);
	fclose(logfd);
	// close the socket
	close(sockfd);
  return EXIT_SUCCESS;
}
