#ifdef __linux__
#define _DEFAULT_SOURCE
#define _BSD_SOURCE
#define _POSIX_C_SOURCE 200809L
#else
#undef _POSIX_C_SOURCE
#endif

#include <stdio.h>
#include <sys/wait.h>
#include <stdlib.h>
#include <unistd.h>

#include "bufio.h"
#include "test.h"

int main(void)
{
  char buf[16];

  for (int i = 0; i < 1024; i++) {
    FORK_CHILD
    bufio_stream *input = bufio_open("tcp://listen/12345/localhost", "r", 1000, 0, "bufio_test_wait_on_tcpclose");
    assert(input != NULL);

    // No data initially
    assert(bufio_wait(input, 0) == 0);

    usleep(100000);

    // 4 bytes available
    assert(bufio_wait(input, 0) == 1);
    assert(bufio_read(input, buf, 4) == 4);
    assert(bufio_wait(input, 0) == 0);

    usleep(100000);

    // Other end closed
    bufio_timeout(input, 1000);
    assert(bufio_read(input, buf, 4) == 0);
    assert(bufio_wait(input, 1000) == -1);

    assert(bufio_close(input) == 0);

    FORK_PARENT
    usleep(200000);
    bufio_stream *output = bufio_open("tcp://connect/12345/localhost", "w", 1000, 0, "bufio_test_wait_on_tcpclose");
    assert(output != NULL);

    usleep(50000);

    // Transmit 4 bytes
    assert(bufio_write(output, buf, 4) == 4);
    assert(bufio_flush(output) == 0);

    usleep(100000);

    // Close
    assert(bufio_close(output) == 0);

    FORK_JOIN
  }

  return 0;
}
