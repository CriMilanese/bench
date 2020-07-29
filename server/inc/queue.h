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
  struct Node *head;
  struct Node *tail;
  struct Node *front;
  struct Node *rear;
  int size, capacity;
};

// typedef struct Queue q;

// initiate a queue by defining its max size
struct Queue* createQueue(int);

/*
  add the socket file descriptor and its expected lifetime. It first checks whether
  the queue is full, in which case it will return NULL, otherwise it will go ahead
  and create a new Node item containg the given parameters. Enqueuing returns
  the item just for
*/
struct Node *enqueue(struct Queue*, int, int);
struct Node *dequeue(struct Queue*);

// retuns the front pointer
struct Node *forefront(struct Queue*);

// returns the rear pointer
struct Node *back(struct Queue*);

// a user needs to use this function to clean up the queue allocated memory
void free_queue(struct Queue*);

int is_full(struct Queue*);
int is_empty(struct Queue*);
void print_queue(FILE*, struct Queue*);

#endif
