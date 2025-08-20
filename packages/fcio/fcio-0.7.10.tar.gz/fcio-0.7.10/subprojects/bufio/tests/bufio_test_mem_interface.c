#ifdef __linux__
#define _DEFAULT_SOURCE
#define _BSD_SOURCE
#define _POSIX_C_SOURCE 200809L
#define _GNU_SOURCE
#else
#undef _POSIX_C_SOURCE
#endif

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/wait.h>
#include <unistd.h>

#include "bufio.h"
#include "test.h"

int main(void) {

  #define BUF_SIZE 64ul
  char mem_buf[BUF_SIZE] = {0};

  char write_buf[BUF_SIZE];
  for (size_t i = 0; i < BUF_SIZE; i++) {
    write_buf[i] = (char)i + 33;
  }

  char read_buf[BUF_SIZE] = {0};

  char* mem_string;
  size_t mem_string_size = asprintf(&mem_string, "mem://%p/%zu", (void*)mem_buf, BUF_SIZE);

  // require that fixed characters (7) and at least two 0 are written.
  assert(mem_string_size >= 9);

  bufio_stream* fail_stream = bufio_open(mem_string, "x", 0, 0, "bufio_test_mem_interface");
  assert(fail_stream == NULL);

  bufio_stream *writer =
      bufio_open(mem_string, "w", 0, 0, "bufio_test_mem_interface");
  assert(writer != NULL);
  assert(bufio_set_mem_field(writer, mem_buf, BUF_SIZE) == 0);

  bufio_stream *reader =
      bufio_open(mem_string, "r", 0, 0, "bufio_test_mem_interface");
  assert(reader != NULL);
  assert(bufio_set_mem_field(reader, mem_buf, BUF_SIZE) == 0);

  // Transmit 2x 4 bytes, flush & close
  assert(bufio_write(writer, write_buf, 4) == 4);
  assert(bufio_write(writer, write_buf + 4, 4) == 4);
  assert(bufio_flush(writer) == 0);
  assert(strncmp(write_buf, mem_buf, 8) == 0);

  // Test on the reading side, as long as there are unread bytes in the current
  assert(bufio_wait(reader, 0) == 1);
  assert(bufio_read(reader, read_buf, 4) == 4);
  assert(bufio_wait(reader, 1000) == 1);
  assert(bufio_read(reader, read_buf + 4, 4) == 4);
  assert(strncmp(read_buf, mem_buf, 8) == 0);

  assert(strncmp(write_buf, read_buf, 8) == 0);

  assert(bufio_write(writer, write_buf, BUF_SIZE) == BUF_SIZE);
  // writing beyond the buffer should not work
  assert(bufio_write(writer, write_buf, 1) == 0);

  // reset the read buffers offsets
  assert(bufio_set_mem_field(reader, mem_buf, BUF_SIZE) == 0);
  assert(bufio_read(reader, read_buf, BUF_SIZE) == BUF_SIZE);
  assert(strncmp(write_buf, read_buf, BUF_SIZE) == 0);

  // reading beyond the buffer should not work
  assert(bufio_read(reader, read_buf, 1) == 0);

  assert(bufio_close(writer) == 0);
  assert(bufio_close(reader) == 0);

  bufio_stream* bfs = bufio_open("mem://0/0","w",0, 0, "bufio_test_mem_interface");
  assert(bfs != NULL);
  bufio_set_mem_field(bfs, mem_buf, BUF_SIZE);
  assert(bufio_close(bfs) == 0);

  bfs = bufio_open("mem://0/0","w",0, 0, "bufio_test_mem_interface");
  bufio_set_mem_field(bfs, mem_buf, 2);
  assert(bufio_write(bfs, write_buf, 4) == 2);
  assert(bufio_status(bfs) == BUFIO_NOSPACE);
  assert(bufio_close(bfs) == 0);

  bfs = bufio_open("mem://0/0","r",0, 0, "bufio_test_mem_interface");
  bufio_set_mem_field(bfs, mem_buf, 2);
  assert(bufio_read(bfs, read_buf, 4) == 2);
  assert(bufio_status(bfs) == BUFIO_EOF);
  assert(bufio_close(bfs) == 0);

  free(mem_string);

  return 0;
}
