os = host_machine.system()

if os == 'windows'
  add_project_link_arguments(
    '-Wl,--allow-multiple-definition',
    language: 'fortran',
  )
endif

fc = meson.get_compiler('fortran')
fc_id = fc.get_id()

if fc_id == 'gcc'
  # from previous setup: "-g -O0 -Wall -fimplicit-none -fcheck=all,no-recursion
  # -fbacktrace -Wno-unused-dummy-argument -Wno-unused-function"
  add_project_arguments(
    '-fbacktrace',
    '-fcheck=all,no-recursion',
    '-ffree-line-length-none',
    '-fimplicit-none',
    '-Wno-unused-dummy-argument',
    '-Wno-unused-function',
    language: 'fortran',
  )
endif
