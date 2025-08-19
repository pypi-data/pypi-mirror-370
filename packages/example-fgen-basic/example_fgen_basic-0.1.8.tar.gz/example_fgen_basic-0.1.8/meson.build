project(
  'example-fgen-basic',  # injected with scripts/make-version-consistent.py, don't edit by hand
  ['c', 'fortran'],  # C as f2py creates C files so we need a C compiler
  # Dev version (i.e. anything that isn't a release) will be 0.0.0
  # because meson doesn't support pre-release identifiers like `.a`, `.post`
  version: '0.1.8',  # injected with scripts/make-version-consistent.py, don't edit by hand
  license: 'BSD-3-Clause',
  meson_version: '>=1.3.0',
  default_options: [
    'buildtype=debugoptimized',
    'default_library=both',
  ],
)

# Some useful constants
pyprojectwheelbuild_enabled = get_option('pyprojectwheelbuild').enabled()

# Print out values if you want
# To set this, you have to run e.g.
# `uv run meson configure -Dverbose=0`
# first, then run all the compile and other steps
message('verbose: ', get_option('verbose'))
if get_option('verbose') > 0
  message('default_library', get_option('default_library'))
  message('pyprojectwheelbuild.enabled(): ', pyprojectwheelbuild_enabled)
  message('soversion', get_option('soversion'))
endif

if pyprojectwheelbuild_enabled
  ## Python wrapper
  python_project_name = 'example_fgen_basic'  # injected with scripts/make-version-consistent.py, don't edit by hand
  extension_module_name = '_lib'  # Doesn't need to be more specific I don't think (?)

  if get_option('verbose') > 0
    message('python_project_name: ', python_project_name)
    message('extension_module_name: ', extension_module_name)
  endif

  # Not actually required.
  # Useful to have to improve error messages
  # in the case where there is no Fortran compiler
  fc = meson.get_compiler('fortran')

  py = import('python').find_installation(pure: false)
  py_dep = py.dependency()

  # Specify all the wrapper Fortran files.
  # These are the src with which Python interacts.
  # Injected with `script/inject-srcs-into-meson-build.py`
  srcs = files(
    'src/example_fgen_basic/get_wavelength_wrapper.f90',
  )

  # Specify all the other source Fortran files (original files and managers)
  # Injected with `script/inject-srcs-into-meson-build.py`
  srcs_ancillary_lib = files(
    'src/example_fgen_basic/get_wavelength.f90',
    'src/example_fgen_basic/kind_parameters.f90',
  )

  # All Python files (wrappers and otherwise)
  # Injected with `script/inject-srcs-into-meson-build.py`
  python_srcs = files(
    'src/example_fgen_basic/__init__.py',
    'src/example_fgen_basic/exceptions.py',
    'src/example_fgen_basic/get_wavelength.py',
    'src/example_fgen_basic/operations.py',
    'src/example_fgen_basic/runtime_helpers.py',
  )

  # The ancillary library,
  # i.e. all the stuff for wrapping that isn't directly exposed to Python.
  ancillary_lib = library(
    '@0@-ancillary'.format(meson.project_name()),
    sources: srcs_ancillary_lib,
    version: meson.project_version(),
    dependencies: [],
    # any other dependencies which aren't in source e.g. fgen-core
    # e.g. dependencies: [fgen_core_dep],
    install: false,
  )

  ancillary_dep = declare_dependency(link_with: ancillary_lib)

  # Get numpy and f2py headers and setup dependencies
  incdir_numpy = run_command(py,
    ['-c', 'import os; import numpy; print(numpy.get_include())'],
    check : true
  ).stdout().strip()

  incdir_f2py = run_command(py,
    ['-c', 'import os; import numpy.f2py; print(numpy.f2py.get_include())'],
      check : true
  ).stdout().strip()

  inc_np = include_directories(incdir_numpy)
  np_dep = declare_dependency(include_directories: inc_np)

  # Run f2py to generate the Python-Fortran interface
  python_fortran_interface = custom_target(
    'f2py_extension_module',
    input: srcs,
    output: [
      # Naming controlled by f2py here hence slightly random use of hyphens
      '@0@module.c'.format(extension_module_name),
      '@0@-f2pywrappers2.f90'.format(extension_module_name),
    ],
    command: [
      py,
      '-m',
      'numpy.f2py',
      '@INPUT@',
      '-m',
      extension_module_name,
      '--lower'
    ]
  )
  # Build the extension module
  py.extension_module(
      extension_module_name,
      [srcs, python_fortran_interface],
      incdir_f2py / 'fortranobject.c',
      include_directories: [inc_np, incdir_f2py],
      dependencies : [ancillary_dep],
      # # If you need other deps, add them here too e.g.
      # dependencies : [ancillary_dep, fgen_core_dep],
      install: true,
      subdir: python_project_name,
  )

  # If some files (such as .py files) need to be copied to site-packages,
  # this is where that operation happens.
  # Files get copied to <python directory>/site-packages/<subdir>
  foreach python_src : python_srcs
    py.install_sources(
        python_src,
        subdir: python_project_name,
        pure: false,
    )

    # TODO: check if anything needs to happen here for e.g. LICENCE, Python source files

  endforeach

  # dist - script to reduce the *tar.gz
  meson.add_dist_script(py, files('scripts' / 'strip-sdist.py'))

else
  ## Fortran library standalone compilation

  # Copied from https://github.com/toml-f/toml-f/blob/main/meson.build
  # Not clear what the right choice is here yet
  install = not (meson.is_subproject() and get_option('default_library') == 'static')

  if get_option('testing').auto()
    testing_enabled = not meson.is_subproject()
  else
    testing_enabled = get_option('testing').enabled()
  endif

  if get_option('verbose') > 0
    message('install', install)
    message('get_option("testing"): ', get_option('testing'))
    message('meson.is_subproject(): ', meson.is_subproject())
    message('testing_enabled: ', testing_enabled)
  endif

  # Purpose not 100% clear, but compiler flags look useful so following
  # https://github.com/toml-f/toml-f/blob/main/meson.build for now.
  # TODO: think about this more carefully.
  # General configuration information
  subdir('config')

  # Collect source of the Fortran dependencies
  srcs = []
  subdir('src')

  # Library target
  # TODO: think about whether this should be in `src/example.meson.build`
  # as that nesting seems to be the more common pattern
  example_lib = library(
    meson.project_name(),
    sources: srcs,
    version: meson.project_version(),
    soversion : get_option('soversion'),
    install: pyprojectwheelbuild_enabled ? false : install,
  )

  # Export dependency for other projects and test suite to use
  example_inc = example_lib.private_dir_include()
  example_dep = declare_dependency(
    link_with: example_lib,
    include_directories: example_inc,
  )

  if install

    # Package the license files
    example_lic = files('LICENCE')
    install_data(
      example_lic,
      install_dir: get_option('datadir')/'licenses'/meson.project_name()
    )

    module_id = meson.project_name() / 'modules'

    # Copy .mod files into includedir
    meson.add_install_script(
      find_program(files('config'/'install-mod.py')),
      get_option('includedir') / module_id,
    )

    # Generate package config
    # https://mesonbuild.com/Pkgconfig-module.html
    # https://people.freedesktop.org/~dbn/pkg-config-guide.html
    pkg = import('pkgconfig')
    pkg.generate(
      example_lib,
      description: 'Basic example of using fgen. This is the standalone Fortran library.',  # injected with scripts/make-version-consistent.py, do not edit by hand
      subdirs: ['', module_id],
    )

    # TODO: check if anything needs to happen here for e.g. LICENCE, something else

  endif

  if testing_enabled
    # add the Fortran testsuite
    subdir('tests')
  endif

endif
