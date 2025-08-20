#include <stdlib.h>

#include <fsp/io_fcio.h>
#include "fsp/processor.h"

#include "test.h"
#include "fsp_test_utils.h"

#define FCIODEBUG 0
int main(int argc, char* argv[])
{
  assert(argc == 2);

  const char* peer = argv[1];

  FCIODebug(FCIODEBUG);
  int tag = 0;

  /* write test file*/
  FCIOStream stream = FCIOConnect(peer, 'w', 0, 0);
  FCIOData* input = FCIOOpen(peer, 0, 0);

  StreamProcessor* proc_out = FSPCreate(0);
  StreamProcessor* proc_in = FSPCreate(0);

  fill_default_fspconfig(proc_out);
  FCIOPutFSPConfig(stream, proc_out);
  tag = FCIOGetRecord(input);
  assert(tag == FCIOFSPConfig);
  FCIOGetFSPConfig(input,proc_in);
  assert(is_same_fspconfig(proc_in, proc_out));

  fill_default_fspevent(proc_out->fsp_state);
  FCIOPutFSPEvent(stream, proc_out);
  tag = FCIOGetRecord(input);
  assert(tag == FCIOFSPEvent);
  FCIOGetFSPEvent(input, proc_in);
  assert(is_same_fspevent(proc_in->fsp_state, proc_out->fsp_state));

  fill_default_fspstatus(proc_out);
  FCIOPutFSPStatus(stream, proc_out);
  tag = FCIOGetRecord(input);
  assert(tag == FCIOFSPStatus);
  FCIOGetFSPStatus(input,proc_in);
  assert(is_same_fspstatus(proc_in, proc_out));

  FCIODisconnect(stream);
  FCIOClose(input);
  FSPDestroy(proc_out);
  FSPDestroy(proc_in);

  return 0;

}
