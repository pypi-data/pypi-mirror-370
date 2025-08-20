#include <stdlib.h>


#include <fsp.h>
#include <fcio.h>
#include <fsp/io_fcio.h>
#include "fsp/processor.h"
#include "fsp/flags.h"
#include "fsp/state.h"
#include "fsp/stats.h"
#include "fsp/timestamps.h"

#include "test.h"
#include "fsp_test_utils.h"

int FCIOPutFSPEvent_v0_f43d383ec5093bbe09658c59ae9bb45e8237893f(FCIOStream output, StreamProcessor* processor)
/*
  The version of PutFSPEvent before the obs.ps.hwm_prescaled_trace_idx got added.
  A better test would be to checkout this commit and try the permutations.
  This tests only of the old data can be read.
*/
{
  if (!output || !processor || !processor->fsp_state)
    return -1;

  FSPState* fsp_state = processor->fsp_state;

  FCIOWriteMessage(output, FCIOFSPEvent);
  FCIOWrite(output, sizeof(fsp_state->write_flags), &fsp_state->write_flags);
  FCIOWrite(output, sizeof(fsp_state->proc_flags), &fsp_state->proc_flags);

  FCIOWrite(output, sizeof(fsp_state->obs.evt), &fsp_state->obs.evt);
  FCIOWrite(output, sizeof(fsp_state->obs.hwm), &fsp_state->obs.hwm);
  FCIOWrite(output, sizeof(fsp_state->obs.wps), &fsp_state->obs.wps);

  FCIOWriteInts(output, fsp_state->obs.ct.multiplicity, fsp_state->obs.ct.trace_idx);
  FCIOWriteUShorts(output, fsp_state->obs.ct.multiplicity, fsp_state->obs.ct.max);

  FCIOWriteInts(output, fsp_state->obs.sub_event_list.size, fsp_state->obs.sub_event_list.start);
  FCIOWriteInts(output, fsp_state->obs.sub_event_list.size, fsp_state->obs.sub_event_list.stop);
  FCIOWriteFloats(output, fsp_state->obs.sub_event_list.size, fsp_state->obs.sub_event_list.wps_max);

  return FCIOFlush(output);
}

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

  StreamProcessor* proc_out_v0 = FSPCreate(0);
  StreamProcessor* proc_out = FSPCreate(0);
  StreamProcessor* proc_in = FSPCreate(0);

  /* first send previous versions */
  fill_default_fspevent(proc_out->fsp_state);
  FCIOPutFSPEvent_v0_f43d383ec5093bbe09658c59ae9bb45e8237893f(stream, proc_out_v0);

  /* write current version */
  fill_default_fspevent(proc_out->fsp_state);
  FCIOPutFSPEvent(stream, proc_out);

  tag = FCIOGetRecord(input);
  assert(tag == FCIOFSPEvent);
  FCIOGetFSPEvent(input, proc_in);
  // if the record is not written, the length is supposed to be set to 0
  proc_out_v0->fsp_state->obs.ps.n_hwm_prescaled = 0;
  assert(is_same_fspevent(proc_in->fsp_state, proc_out_v0->fsp_state));

  tag = FCIOGetRecord(input);
  assert(tag == FCIOFSPEvent);
  FCIOGetFSPEvent(input, proc_in);
  assert(is_same_fspevent(proc_in->fsp_state, proc_out->fsp_state));

  FCIODisconnect(stream);
  FCIOClose(input);
  FSPDestroy(proc_out);
  FSPDestroy(proc_in);

  return 0;

}
