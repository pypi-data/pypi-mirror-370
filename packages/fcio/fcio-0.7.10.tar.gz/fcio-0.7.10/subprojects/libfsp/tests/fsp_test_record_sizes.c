

#include <stdio.h>
#include <stdlib.h>
#include <sys/types.h>

#include "fsp/io_fcio.h"
#include "fcio_utils.h"

#include "test.h"

void print_sizes(FCIORecordSizes sizes)
{
  fprintf(stderr, "..protocol    %zu bytes\n", sizes.protocol);
  fprintf(stderr, "..fspconfig   %zu bytes\n", sizes.fspconfig);
  fprintf(stderr, "..fspevent    %zu bytes\n", sizes.fspevent);
  fprintf(stderr, "..fspstatus   %zu bytes\n", sizes.fspstatus);
}

void set_parameters(StreamProcessor* processor, FSPState* fspstate, unsigned int nchannels, int verbose)
{

  processor->dsp_hwm.tracemap.n_mapped = (nchannels) * 3 / 5;
  processor->dsp_wps.tracemap.n_mapped = (nchannels) * 2 / 5;
  processor->dsp_ct.tracemap.n_mapped = nchannels - processor->dsp_hwm.tracemap.n_mapped - processor->dsp_wps.tracemap.n_mapped;
  processor->triggerconfig.n_wps_ref_map_idx = processor->dsp_ct.tracemap.n_mapped / 2;

  fspstate->obs.ct.multiplicity = processor->dsp_ct.tracemap.n_mapped;
  fspstate->obs.sub_event_list.size = 2;

  if (verbose) {
    fprintf(stderr,
      "set_parameters:\n"
      "fspevent: ct.multiplicity %d sub_event_list.size %d\n"
      "fspconfig: hwm.ntraces %d wps.ntraces %d ct.ntraces %d\n",
      fspstate->obs.ct.multiplicity, fspstate->obs.sub_event_list.size,
      processor->dsp_hwm.tracemap.n_mapped, processor->dsp_wps.tracemap.n_mapped, processor->dsp_ct.tracemap.n_mapped
    );
  }
}

void check(StreamProcessor* processor, unsigned int nchannels, int verbose) {

  set_parameters(processor, processor->fsp_state, nchannels, verbose);
  FCIORecordSizes measured_sizes = {0};
  FCIORecordSizes calculated_sizes = {0};
  FSPMeasureRecordSizes(processor, &measured_sizes);
  FSPCalculateRecordSizes(processor, &calculated_sizes);

  if (verbose) {
    fprintf(stderr, "nadcs %u:\n", nchannels);
    fprintf(stderr, "measured:\n");
    print_sizes(measured_sizes);
    fprintf(stderr, "calculated:\n");
    print_sizes(calculated_sizes);
    fprintf(stderr, "\n");
  }

  assert(measured_sizes.protocol == calculated_sizes.protocol);
  assert(measured_sizes.fspconfig == calculated_sizes.fspconfig);
  assert(measured_sizes.fspevent == calculated_sizes.fspevent);
  assert(measured_sizes.fspstatus == calculated_sizes.fspstatus);
}

int main(int argc, char* argv[])
{
  int verbose = 0;
  if (argc >= 2)
    verbose = atoi(argv[1]);

  StreamProcessor* processor = FSPCreate(0);

  check(processor, 0, verbose); // min
  check(processor, 1, verbose); // min
  check(processor, 181, verbose); // lgnd
  check(processor, 576, verbose); // max 16-bit
  check(processor, 2304, verbose); // max 12-bit

  FSPDestroy(processor);

  return 0;
}
