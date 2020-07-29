/*
 the following data structure prioritize re-usability
 documentation is specific to the author's case
*/

#ifndef QUEUE_H
#define QUEUE_H

// every item contains the fd and its remaining lifetime
struct Node {
  int socket_fd;
  int lifetime_left;
};

// A linked list structure to represent a queue
struct Queue {
  Node *head;
  int *tail;
  int *front;
  int *rear;
  int size, capacity;
};

// initiate a queue by defining its max size
struct Queue* createQueue(int);

//  the following operations take the queue object as thieir first parameters
int is_full(struct Queue*);
int is_empty(struct Queue*);

/*
  it requires a extra two parameters, the socket file descriptor and its
  expected lifetime
*/
int *enqueue(struct Queue*, int, int);
int dequeue(struct Queue*);
int *front(struct Queue*);
int *back(struct Queue*);
void free_queue(struct Queue*);
void print_queue(FILE*, struct Queue*);

#endif
