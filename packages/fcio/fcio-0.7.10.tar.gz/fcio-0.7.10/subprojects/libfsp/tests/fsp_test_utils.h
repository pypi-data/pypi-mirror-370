#pragma once

#include <string.h>

#include <fsp.h>
#include <fcio.h>
#include "fsp/flags.h"
#include "fsp/stats.h"
#include "fsp/timestamps.h"

#include "test.h"

static inline void write_sequence(char* data, size_t size) {
  for (size_t i = 0; i < size; i++) {
    data[i] = (char)i;
  }
}

void fill_default_fspconfig(StreamProcessor* proc)
{
  write_sequence((char*)&proc->triggerconfig.hwm_min_multiplicity, sizeof(proc->triggerconfig.hwm_min_multiplicity));
  write_sequence((char*)&proc->triggerconfig.hwm_prescale_ratio, sizeof(proc->triggerconfig.hwm_prescale_ratio));
  write_sequence((char*)&proc->triggerconfig.wps_prescale_ratio, sizeof(proc->triggerconfig.wps_prescale_ratio));

  write_sequence((char*)&proc->triggerconfig.wps_coincident_sum_threshold, sizeof(proc->triggerconfig.wps_coincident_sum_threshold));
  write_sequence((char*)&proc->triggerconfig.wps_sum_threshold, sizeof(proc->triggerconfig.wps_sum_threshold));
  write_sequence((char*)&proc->triggerconfig.wps_prescale_rate, sizeof(proc->triggerconfig.wps_prescale_rate));
  write_sequence((char*)&proc->triggerconfig.hwm_prescale_rate, sizeof(proc->triggerconfig.hwm_prescale_rate));

  write_sequence((char*)&proc->triggerconfig.enabled_flags, sizeof(proc->triggerconfig.enabled_flags));
  write_sequence((char*)&proc->triggerconfig.pre_trigger_window, sizeof(proc->triggerconfig.pre_trigger_window));
  write_sequence((char*)&proc->triggerconfig.post_trigger_window, sizeof(proc->triggerconfig.post_trigger_window));

  write_sequence((char*)&proc->triggerconfig.wps_ref_flags_wps, sizeof(proc->triggerconfig.wps_ref_flags_wps));
  write_sequence((char*)&proc->triggerconfig.wps_ref_flags_ct, sizeof(proc->triggerconfig.wps_ref_flags_ct));
  write_sequence((char*)&proc->triggerconfig.wps_ref_flags_wps, sizeof(proc->triggerconfig.wps_ref_flags_wps));
  write_sequence((char*)&proc->triggerconfig.wps_ref_map_idx, sizeof(proc->triggerconfig.wps_ref_map_idx));
  proc->triggerconfig.n_wps_ref_map_idx = FCIOMaxChannels;

  proc->buffer->max_states = 100;
  write_sequence((char*)&proc->buffer->buffer_window, sizeof(proc->buffer->buffer_window));

  proc->dsp_hwm.tracemap.n_mapped = FCIOMaxChannels;
  proc->dsp_hwm.tracemap.n_enabled = FCIOMaxChannels;
  write_sequence((char*)&proc->dsp_hwm.tracemap.map, sizeof(proc->dsp_hwm.tracemap.map));
  write_sequence((char*)&proc->dsp_hwm.tracemap.enabled, sizeof(proc->dsp_hwm.tracemap.enabled));
  write_sequence((char*)&proc->dsp_hwm.fpga_energy_threshold_adc, sizeof(proc->dsp_hwm.fpga_energy_threshold_adc));

  proc->dsp_ct.tracemap.n_mapped = FCIOMaxChannels;
  proc->dsp_ct.tracemap.n_enabled = FCIOMaxChannels;
  write_sequence((char*)&proc->dsp_ct.tracemap.map, sizeof(proc->dsp_ct.tracemap.map));
  write_sequence((char*)&proc->dsp_ct.tracemap.enabled, sizeof(proc->dsp_ct.tracemap.enabled));
  write_sequence((char*)&proc->dsp_ct.thresholds, sizeof(proc->dsp_ct.thresholds));


  proc->dsp_wps.apply_gain_scaling = 1;
  proc->dsp_wps.sum_window_size = FCIOMaxSamples/2;
  proc->dsp_wps.sum_window_start_sample = 1;
  proc->dsp_wps.sum_window_stop_sample = FCIOMaxSamples;
  proc->dsp_wps.sub_event_sum_threshold = 10.0;

  proc->dsp_wps.tracemap.n_mapped = FCIOMaxChannels;
  proc->dsp_wps.tracemap.n_enabled = FCIOMaxChannels;
  write_sequence((char*)&proc->dsp_wps.tracemap.map, sizeof(proc->dsp_wps.tracemap.map));
  write_sequence((char*)&proc->dsp_wps.tracemap.enabled, sizeof(proc->dsp_wps.tracemap.enabled));
  write_sequence((char*)&proc->dsp_wps.gains, sizeof(proc->dsp_wps.gains));
  write_sequence((char*)&proc->dsp_wps.thresholds, sizeof(proc->dsp_wps.thresholds));
  write_sequence((char*)&proc->dsp_wps.lowpass, sizeof(proc->dsp_wps.lowpass));
  write_sequence((char*)&proc->dsp_wps.shaping_widths, sizeof(proc->dsp_wps.shaping_widths));

  proc->dsp_wps.dsp_max_margin_front = 3;
  proc->dsp_wps.dsp_max_margin_back = 3;

  write_sequence((char*)&proc->dsp_wps.dsp_margin_front, sizeof(proc->dsp_wps.dsp_margin_front));
  write_sequence((char*)&proc->dsp_wps.dsp_margin_back, sizeof(proc->dsp_wps.dsp_margin_back));
  write_sequence((char*)&proc->dsp_wps.dsp_start_sample, sizeof(proc->dsp_wps.dsp_start_sample));
  write_sequence((char*)&proc->dsp_wps.dsp_stop_sample, sizeof(proc->dsp_wps.dsp_stop_sample));

}

void fill_default_fspevent(FSPState* state)
{
  write_sequence((char*)&state->write_flags, sizeof(state->write_flags));
  write_sequence((char*)&state->proc_flags, sizeof(state->proc_flags));
  write_sequence((char*)&state->obs.evt, sizeof(state->obs.evt));
  write_sequence((char*)&state->obs.hwm, sizeof(state->obs.hwm));
  write_sequence((char*)&state->obs.wps, sizeof(state->obs.wps));

  state->obs.ct.multiplicity = FCIOMaxChannels;
  write_sequence((char*)&state->obs.ct.trace_idx, sizeof(state->obs.ct.trace_idx));
  write_sequence((char*)&state->obs.ct.max, sizeof(state->obs.ct.max));

  state->obs.sub_event_list.size = FCIOMaxSamples;
  write_sequence((char*)&state->obs.sub_event_list.start, sizeof(state->obs.sub_event_list.start));
  write_sequence((char*)&state->obs.sub_event_list.stop, sizeof(state->obs.sub_event_list.stop));
  write_sequence((char*)&state->obs.sub_event_list.wps_max, sizeof(state->obs.sub_event_list.wps_max));
  state->obs.ps.n_hwm_prescaled = FCIOMaxChannels;
  write_sequence((char*)&state->obs.ps.hwm_prescaled_trace_idx, sizeof(state->obs.ps.hwm_prescaled_trace_idx));

}

void fill_default_fspstatus(StreamProcessor* proc)
{
  write_sequence((char*)&proc->stats, sizeof(FSPStats));
}


int is_same_fspstatus(StreamProcessor *left, StreamProcessor *right)
{
  assert(0 == memcmp(&left->stats, &right->stats, sizeof(FSPStats)));
  return 1;
}

int is_same_fspconfig(StreamProcessor *left, StreamProcessor *right)
{
  assert(left->triggerconfig.hwm_min_multiplicity == right->triggerconfig.hwm_min_multiplicity);
  assert(0 == memcmp(left->triggerconfig.hwm_prescale_ratio, right->triggerconfig.hwm_prescale_ratio, sizeof(left->triggerconfig.hwm_prescale_ratio)));
  assert(left->triggerconfig.wps_prescale_ratio == right->triggerconfig.wps_prescale_ratio);
  assert(left->triggerconfig.wps_coincident_sum_threshold == right->triggerconfig.wps_coincident_sum_threshold);
  assert(left->triggerconfig.wps_sum_threshold == right->triggerconfig.wps_sum_threshold);
  assert(left->triggerconfig.wps_prescale_rate == right->triggerconfig.wps_prescale_rate);
  assert(0 == memcmp(left->triggerconfig.hwm_prescale_rate, right->triggerconfig.hwm_prescale_rate, sizeof(left->triggerconfig.hwm_prescale_rate)));
  assert(0 == memcmp(&left->triggerconfig.enabled_flags, &right->triggerconfig.enabled_flags, sizeof(FSPWriteFlags)));
  assert(0 == memcmp(&left->triggerconfig.pre_trigger_window, &right->triggerconfig.pre_trigger_window, sizeof(Timestamp)));
  assert(0 == memcmp(&left->triggerconfig.post_trigger_window, &right->triggerconfig.post_trigger_window, sizeof(Timestamp)));
  assert(0 == memcmp(&left->triggerconfig.wps_ref_flags_hwm, &right->triggerconfig.wps_ref_flags_hwm, sizeof(HWMFlags)));
  assert(0 == memcmp(&left->triggerconfig.wps_ref_flags_ct, &right->triggerconfig.wps_ref_flags_ct, sizeof(CTFlags)));
  assert(0 == memcmp(&left->triggerconfig.wps_ref_flags_wps, &right->triggerconfig.wps_ref_flags_wps, sizeof(WPSFlags)));
  assert(left->triggerconfig.n_wps_ref_map_idx == right->triggerconfig.n_wps_ref_map_idx);
  assert(0 == memcmp(&left->triggerconfig.wps_ref_map_idx, &right->triggerconfig.wps_ref_map_idx, FCIOMaxChannels * sizeof(int)));

  assert(left->buffer->max_states == right->buffer->max_states)
  assert(left->buffer->buffer_window.seconds == right->buffer->buffer_window.seconds)
  assert(left->buffer->buffer_window.nanoseconds == right->buffer->buffer_window.nanoseconds)

  assert(left->dsp_hwm.tracemap.n_enabled == right->dsp_hwm.tracemap.n_enabled);
  assert(left->dsp_hwm.tracemap.n_mapped == right->dsp_hwm.tracemap.n_mapped);
  assert(0 == memcmp(left->dsp_hwm.tracemap.map, right->dsp_hwm.tracemap.map, FCIOMaxChannels * sizeof(int)));
  assert(0 == memcmp(left->dsp_hwm.fpga_energy_threshold_adc, right->dsp_hwm.fpga_energy_threshold_adc, FCIOMaxChannels * sizeof(unsigned short)));

  assert(left->dsp_ct.tracemap.n_enabled == right->dsp_ct.tracemap.n_enabled);
  assert(left->dsp_ct.tracemap.n_mapped == right->dsp_ct.tracemap.n_mapped);
  assert(0 == memcmp(left->dsp_ct.tracemap.map, right->dsp_ct.tracemap.map,FCIOMaxChannels * sizeof(int)));
  assert(0 == memcmp(left->dsp_ct.thresholds, right->dsp_ct.thresholds, FCIOMaxChannels * sizeof(unsigned short)));

  assert(left->dsp_wps.tracemap.n_enabled == right->dsp_wps.tracemap.n_enabled);
  assert(left->dsp_wps.tracemap.n_mapped == right->dsp_wps.tracemap.n_mapped);
  assert(0 == memcmp(left->dsp_wps.tracemap.map, right->dsp_wps.tracemap.map,FCIOMaxChannels * sizeof(int)));

  assert(left->dsp_wps.apply_gain_scaling == right->dsp_wps.apply_gain_scaling);
  assert(left->dsp_wps.sum_window_size == right->dsp_wps.sum_window_size);
  assert(left->dsp_wps.sum_window_start_sample == right->dsp_wps.sum_window_start_sample);
  assert(left->dsp_wps.sum_window_stop_sample == right->dsp_wps.sum_window_stop_sample);
  assert(left->dsp_wps.sub_event_sum_threshold == right->dsp_wps.sub_event_sum_threshold);
  assert(left->dsp_wps.dsp_max_margin_front == right->dsp_wps.dsp_max_margin_front);
  assert(left->dsp_wps.dsp_max_margin_back == right->dsp_wps.dsp_max_margin_back);
  assert(left->dsp_wps.apply_gain_scaling == right->dsp_wps.apply_gain_scaling);

  assert(0 == memcmp(left->dsp_wps.gains, right->dsp_wps.gains, FCIOMaxChannels * sizeof(float)));
  assert(0 == memcmp(left->dsp_wps.thresholds, right->dsp_wps.thresholds, FCIOMaxChannels * sizeof(float)));
  assert(0 == memcmp(left->dsp_wps.lowpass, right->dsp_wps.lowpass, FCIOMaxChannels * sizeof(float)));
  assert(0 == memcmp(left->dsp_wps.shaping_widths, right->dsp_wps.shaping_widths, FCIOMaxChannels*  sizeof(int)));
  assert(0 == memcmp(left->dsp_wps.dsp_margin_front, right->dsp_wps.dsp_margin_front, FCIOMaxChannels * sizeof(int)));
  assert(0 == memcmp(left->dsp_wps.dsp_margin_back, right->dsp_wps.dsp_margin_back, FCIOMaxChannels * sizeof(int)));
  assert(0 == memcmp(left->dsp_wps.dsp_start_sample, right->dsp_wps.dsp_start_sample, FCIOMaxChannels * sizeof(int)));
  assert(0 == memcmp(left->dsp_wps.dsp_stop_sample, right->dsp_wps.dsp_stop_sample, FCIOMaxChannels * sizeof(int)));

  return 1;
}

int is_same_fspevent(FSPState *left, FSPState *right)
{
  assert(0 == memcmp(&left->write_flags, &right->write_flags, sizeof(FSPWriteFlags) ));
  assert(0 == memcmp(&left->proc_flags, &right->proc_flags, sizeof(FSPProcessorFlags) ));
  assert(0 == memcmp(&left->obs.evt, &right->obs.evt, sizeof(evt_obs) ));
  assert(0 == memcmp(&left->obs.hwm, &right->obs.hwm, sizeof(hwm_obs) ));
  assert(0 == memcmp(&left->obs.wps, &right->obs.wps, sizeof(wps_obs) ));
  assert(left->obs.ct.multiplicity == right->obs.ct.multiplicity);
  assert(0 == memcmp(left->obs.ct.trace_idx, right->obs.ct.trace_idx, right->obs.ct.multiplicity ));
  assert(0 == memcmp(left->obs.ct.max, right->obs.ct.max, right->obs.ct.multiplicity ));
  assert(left->obs.sub_event_list.size == right->obs.sub_event_list.size);
  assert(0 == memcmp(left->obs.sub_event_list.start, right->obs.sub_event_list.start, right->obs.sub_event_list.size ));
  assert(0 == memcmp(left->obs.sub_event_list.stop, right->obs.sub_event_list.stop, right->obs.sub_event_list.size ));
  assert(0 == memcmp(left->obs.sub_event_list.wps_max, right->obs.sub_event_list.wps_max, right->obs.sub_event_list.size ));
  assert(0 == memcmp(left->obs.ps.hwm_prescaled_trace_idx, right->obs.ps.hwm_prescaled_trace_idx, right->obs.ps.n_hwm_prescaled ));

  return 1;
}
