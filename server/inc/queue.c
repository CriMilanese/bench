// C program for array implementation of queue
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "queue.h"

// function to create a queue of given capacity.
// It initializes size of queue as 0
struct Queue* createQueue(int capacity){
  struct Queue* queue = (struct Queue*) calloc(1, sizeof(struct Queue));
  queue->capacity = capacity;
  queue->size = 0;
  queue->head = (int*) calloc(queue->capacity, sizeof(int));
  queue->front = queue->rear = queue->head;
  queue->tail = queue->head + queue->capacity - 1;
  return queue;
}

// Queue is full when size becomes equal to the capacity
int is_full(struct Queue* queue){
  return (queue->size == queue->capacity);
}

int is_empty(struct Queue* queue){
  return (queue->size == 0);
}

// Function to add an item to the queue.
int *enqueue(struct Queue* queue, int item){
  int *tmp = &item;
  if (is_full(queue))
      return NULL;
  *(queue->rear) = item;

  // make it circular
  if(queue->rear == queue->tail){
    queue->rear = queue->head;
  } else {
    queue->rear += 1;
  }

  queue->size = queue->size + 1;
  return tmp;
}

// Function to remove an item from queue.
int *dequeue(struct Queue* queue){
  if (is_empty(queue))
      return NULL;
  int *item = queue->front;

  // make it circular
  if(queue->front == queue->tail){
    queue->front = queue->head;
  } else {
    queue->front += 1;
  }

  queue->size = queue->size - 1;
  return item;
}

// Function to get front of queue
int *front(struct Queue* queue){
  if (is_empty(queue))
      return 0;
  return queue->front;
}

// Function to get rear of queue
int *back(struct Queue* queue){
  if (is_empty(queue))
      return 0;
  return queue->rear;
}

void print_queue(FILE* fd, struct Queue *que){
  int sz = que->size;
  fprintf(fd, "Printing the content of queue..\n");
  fprintf(fd, "size is: %d\n", sz);
  int *tmp = que->front;
  for(int i=0; i<sz; i++){
    fprintf(fd, "element %d is %d\n", i, *(que->front));
    if(que->front == que->tail){
      que->front = que->head;
    } else {
      que->front += 1;
    }
  }
  que->front = tmp;
}

void free_queue(struct Queue *queue){
  free(queue->head);
  free(queue);
}