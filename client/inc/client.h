#ifndef CLIENT_H
#define CLIENT_H

float *communicate(int sockfd, FILE *logfd, float* results);
int recv_all(int sockfd, FILE *logfd, ssize_t bytes_sent);


#endif //CLIENT_H
