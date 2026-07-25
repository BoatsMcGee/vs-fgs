project('vsfgs', ['c', 'cpp'],
  version: '0.5.0',
  default_options: ['cpp_std=c++17', 'c_std=c99', 'buildtype=release']
)

# Statically link all MinGW runtime libraries on Windows to avoid
# dependencies on libgcc_s_seh-1.dll, libstdc++-6.dll, and
# libwinpthread-1.dll which are not present on end-user machines.
if host_machine.system() == 'windows' and meson.get_compiler('c').get_id() == 'gcc'
  add_project_link_arguments('-static-libgcc', language: 'c')
  add_project_link_arguments('-static-libgcc', '-static-libstdc++', language: 'cpp')
  add_project_link_arguments('-Wl,-Bstatic', '-lwinpthread', '-Wl,-Bdynamic', language: 'c')
  add_project_link_arguments('-Wl,-Bstatic', '-lwinpthread', '-Wl,-Bdynamic', language: 'cpp')
endif

py = import('python').find_installation(pure: false)

dav1d_proj = subproject('dav1d', default_options: ['default_library=static', 'enable_tools=false', 'enable_tests=false', 'bitdepths=8,16'])
dav1d_dep = dav1d_proj.get_variable('dav1d_dep')

incdir = include_directories('include', 'subprojects/dav1d')

# VapourSynth plugin core
vs_fgs_sources = [
  'src/vs_fgs.cpp'
]

plugin = shared_library('vsfgs',
  vs_fgs_sources,
  include_directories: incdir,
  dependencies: [dav1d_dep],
  name_prefix: '',
  install: true,
  install_dir: py.get_install_dir(pure: false, subdir: 'vapoursynth/plugins')
)

py.install_sources(
  'vsfgs/__init__.py',
  subdir: 'vsfgs'
)
