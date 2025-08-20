fsp_test_record_sizes = executable('fsp_test_record_sizes', 'fsp_test_record_sizes.c', dependencies: [fsp_dep])
fsp_test_record_consistency = executable(
  'fsp_test_record_consistency',
  'fsp_test_record_consistency.c',
  dependencies: [fsp_dep],
)
fsp_test_record_compatibility = executable(
  'fsp_test_record_compatibility',
  'fsp_test_record_compatibility.c',
  dependencies: [fsp_dep],
)

test(
  'fsp_test_record_sizes',
  fsp_test_record_sizes,
  is_parallel: true,
  suite: ['fsp'],
  args: ['0'],
) # set args[0] to 1 for verbose output
test(
  'fsp_test_record_consistency',
  fsp_test_record_consistency,
  is_parallel: true,
  suite: ['fsp'],
  args: ['fsp_test_record_consistency.dat'],
)
test(
  'fsp_test_record_compatibility',
  fsp_test_record_compatibility,
  is_parallel: true,
  suite: ['fsp'],
  args: ['fsp_test_record_compatibility.dat'],
)
