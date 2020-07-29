// C program for array implementation of queue
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "queue.h"

struct Queue* createQueue(int capacity){
  struct Queue* queue = (struct Queue*) calloc(1, sizeof(struct Queue));
  queue->capacity = capacity;
  queue->size = 0;
  queue->head = (struct Node*) calloc(queue->capacity, sizeof(struct Node));
  queue->front = queue->rear = queue->head;
  queue->tail = queue->head + queue->capacity - 1;
  return queue;
}

int is_full(struct Queue* queue){
  return (queue->size == queue->capacity);
}

int is_empty(struct Queue* queue){
  return (queue->size == 0);
}

struct Node *enqueue(struct Queue* queue, int item, int lf){
  if (is_full(queue))
      return NULL;

  struct Node n = {item, lf};
  *queue->rear = n;

  // make it circular
  if(queue->rear == queue->tail){
    queue->rear = queue->head;
  } else {
    queue->rear += 1;
  }

  queue->size += 1;
  return queue->rear;
}

struct Node *dequeue(struct Queue* queue){
  if (is_empty(queue))
      return NULL;
  struct Node *item = queue->front;

  // make it circular
  if(queue->front == queue->tail){
    queue->front = queue->head;
  } else {
    queue->front += 1;
  }

  queue->size -= 1;
  return item;
}

struct Node *forefront(struct Queue* queue){
  if (is_empty(queue))
      return NULL;
  return queue->front;
}

struct Node *back(struct Queue* queue){
  if (is_empty(queue))
      return NULL;
  return queue->rear;
}

// TODO: take out in production
void print_queue(FILE* fd, struct Queue *queue){
  int sz = queue->size;
  fprintf(fd, "Printing the content of queue..\n");
  fprintf(fd, "size is: %d\n", sz);
  struct Node *tmp = queue->front;
  fprintf(fd, "%d\n", (queue->front)->lifetime_left);
  for(int i=0; i<sz; i++){
    fprintf(fd, "element %d is (sfd: %d, ll: %d)\n", i, (queue->front)->socket_fd, (queue->front)->lifetime_left);
    if(queue->front == queue->tail){
      queue->front = queue->head;
    } else {
      queue->front += 1;
    }
  }
  queue->front = tmp;
}

void free_queue(struct Queue *queue){
  // for(int i=queue->size; i>0;i--){
  //   free(queue->head[i])
  // }
  free(queue->head);
  free(queue);
}
