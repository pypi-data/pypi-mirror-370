#ifdef __linux__
#define _DEFAULT_SOURCE
#define _BSD_SOURCE
#define _POSIX_C_SOURCE 200809L
#else
#undef _POSIX_C_SOURCE
#endif

#include <sys/wait.h>
#include <stdlib.h>
#include <unistd.h>

#include "bufio.h"
#include "test.h"


int main(void)
{
  char buf[16];

  bufio_stream *so = bufio_open("file://test_bufio_file.dat", "w", 0, 8, "bufio_test_file");
  assert(so != NULL);

  bufio_stream *si = bufio_open("file://test_bufio_file.dat", "r", 0, 8, "bufio_test_file");
  assert(si != NULL);

  // Assert no initial data
  assert(bufio_wait(si, 0) == 0 && bufio_status(si) == BUFIO_EOF);

  // Assert no data immediately after buffered write
  assert(bufio_write(so, buf, 4) == 4);
  assert(bufio_read(si, buf, 4) == 0 && bufio_status(si) == BUFIO_EOF);
  assert(bufio_wait(si, 0) == 0 && bufio_status(si) == BUFIO_EOF);

  // Assert data after flush
  assert(bufio_flush(so) == 0);
  assert(bufio_read(si, buf, 4) == 4);

  // Assert data immediately after unbuffered write
  assert(bufio_write(so, buf, 16) == 16);
  assert(bufio_read(si, buf, 16) == 16 && bufio_status(si) == BUFIO_EOF);

  // Clean up
  assert(bufio_close(si) == 0);
  assert(bufio_close(so) == 0);
  return 0;
}
