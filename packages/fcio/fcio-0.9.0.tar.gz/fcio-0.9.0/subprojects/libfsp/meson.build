project(
  'libfsp',
  'c',
  'cpp',
  version: '1.0.0',
  license: 'MPL-2.0',
  license_files: 'LICENSE',
  default_options: [
    'warning_level=3',
    'c_std=c11',
    'buildtype=release',
    'default_library=static',
    'prefer_static=true',
  ],
)

# get systemlevel dependencies
cc = meson.get_compiler('c')
m_dep = cc.find_library('m', required: true)

fcio_dep = dependency('fcio', fallback: ['fcio', 'fcio_dep'])
fcio_utils_dep = dependency('fcio_utils', fallback: ['fcio', 'fcio_utils_dep'])

subdir('src')

fsp_lib = library(
  'fsp',
  fsp_sources,
  include_directories: fsp_inc,
  dependencies: [fcio_dep, m_dep],
  install: true,
)

fsp_dep = declare_dependency(
  include_directories: fsp_inc,
  link_with: fsp_lib,
  sources: fsp_sources,
  dependencies: [fcio_dep, fcio_utils_dep, m_dep],
)

subdir('tests')

pkg_mod = import('pkgconfig')
pkg_mod.generate(fsp_lib)
