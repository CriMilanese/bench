#ifndef QUEUE_H
#define QUEUE_H

// A linked list structure to represent a queue
struct Queue{
  int *head;
  int *tail;
  int *front;
  int *rear;
  int size, capacity;
};

struct Queue* createQueue(int);
int is_full(struct Queue*);
int is_empty(struct Queue*);
int *enqueue(struct Queue*, int);
int dequeue(struct Queue*);
int *front(struct Queue*);
int *back(struct Queue*);
void free_queue(struct Queue*);
void print_queue(FILE*, struct Queue*);

#endif
