#include <netdb.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>
#include <arpa/inet.h>
#define MAX 50
#define PORT 8080
#define SA struct sockaddr

void func(int sockfd)
{
	char buff[MAX];
	while(1){
		bzero(buff, sizeof(buff));
		while(read(sockfd, buff, sizeof(buff))<MAX);
		// printf("Enter the string : ");
		// while ((buff[n++] = getchar()) != '\n');
//		if(fill_buff){
//			bzero(buff,  sizeof(buff));
//			for(long i=0; i<MAX; i++){
//				buff[i] = 'c';
//			}
//			fill_buff = 0;
//		}
		if ((strncmp(buff, "exit", 4)) == 0) {
			printf("Client Exit...\n");
			break;
		}
		printf("echoing message back\n");
		write(sockfd, buff, sizeof(buff));
	}
}

int main()
{
	int sockfd, connfd;
	struct sockaddr_in servaddr, cli;

	// socket create and varification
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
		exit(0);
	}
	else
		printf("connected to the server..\n");

	// function for chat
	func(sockfd);

	// close the socket
	close(sockfd);
  return 0;
}