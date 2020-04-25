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

int main()
{
	int sockfd, connfd;
	struct sockaddr_in servaddr;

	// socket create and verification
	sockfd = socket(AF_INET, SOCK_STREAM, 0);
	if (sockfd == -1) {
		printf("socket creation failed...\n");
		exit(0);
	}
	else
		printf("Socket successfully created..\n");
	bzero(&servaddr, sizeof(servaddr));

	// assign IP, PORT
	servaddr.sin_family = AF_INET;
	servaddr.sin_addr.s_addr = inet_addr("192.168.1.143");
	servaddr.sin_port = htons(PORT);

	// connect the client socket to server socket
	if (connect(sockfd, (SA*)&servaddr, sizeof(servaddr)) != 0) {
		printf("connection with the server failed...\n");
		return EXIT_FAILURE;
	}
	else
		printf("connected to the server..\n");

	// function for chat
	func(sockfd);

	printf("connection closed..\n");

	// close the socket
	close(sockfd);
  return EXIT_SUCCESS;
}
