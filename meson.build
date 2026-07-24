project('vs-fgs', ['c', 'cpp'],
  version: '0.1.0',
  default_options: ['cpp_std=c++17', 'c_std=c99', 'buildtype=release']
)

py = import('python').find_installation(pure: false)

# Configure dav1d as static subproject without tools/tests to speed up build
dav1d_proj = subproject('dav1d', default_options: ['default_library=static', 'enable_tools=false', 'enable_tests=false', 'bitdepths=16'])
dav1d_dep = dav1d_proj.get_variable('dav1d_dep')

incdir = include_directories('include', 'subprojects/dav1d')

# VapourSynth plugin core
vs_fgs_sources = [
  'src/vs_fgs.cpp'
]

# The C++ core built as a Python extension module (can be loaded by LoadPlugin)
plugin = py.extension_module('vs_fgs_plugin',
  vs_fgs_sources,
  include_directories: incdir,
  dependencies: [dav1d_dep],
  install: true,
  subdir: 'vs_fgs'
)

# Install python wrapper
py.install_sources(
  'vs_fgs/__init__.py',
  subdir: 'vs_fgs'
)
