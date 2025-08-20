fsp_inc = include_directories('.')

fsp_sources = files(
  'fsp/buffer.c',
  'fsp/dsp.c',
  'fsp/stats.c',
  'fsp/timestamps.c',
  'fsp/io.c',
  'fsp/io_fcio.c',
  'fsp/record_processor.c',
  'fsp/processor.c',
  'fsp_l200.c'
)

install_headers(
  'fsp/processor.h',
  'fsp/timestamps.h',
  'fsp/record_processor.h',
  'fsp/dsp.h',
  'fsp/buffer.h',
  'fsp/state.h',
  'fsp/stats.h',
  'fsp/flags.h',
  'fsp/observables.h',
  'fsp/tracemap.h',
  'fsp/io.h',
  subdir : 'fsp'
)

install_headers(
  'fsp.h'
)
