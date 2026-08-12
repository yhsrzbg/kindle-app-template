project(
  'kindle_app_template',
  'cpp',
  license: 'MIT',
  default_options: ['cpp_std=c++17', 'warning_level=3'],
  meson_version: '>=1.1',
)

python = import('python').find_installation('python3')
config_tool = files('scripts/app_config.py')

app_id = run_command(python, config_tool, 'get', 'id', check: true).stdout().strip()
app_name = run_command(python, config_tool, 'get', 'name', check: true).stdout().strip()
binary_name = run_command(python, config_tool, 'get', 'binary_name', check: true).stdout().strip()
window_id = run_command(python, config_tool, 'get', 'window_id', check: true).stdout().strip()
app_version = run_command(python, config_tool, 'get', 'version_string', check: true).stdout().strip()

conf = configuration_data()
conf.set_quoted('APP_ID', app_id)
conf.set_quoted('APP_NAME', app_name)
conf.set_quoted('APP_BINARY_NAME', binary_name)
conf.set_quoted('APP_WINDOW_ID', window_id)
conf.set_quoted('APP_VERSION', app_version)

configure_file(
  input: 'src/include/app_config.hpp.in',
  output: 'app_config.hpp',
  configuration: conf,
)

gtk_dep = dependency('gtk+-2.0')
static_cpp_args = []
if get_option('static_libstdcpp')
  static_cpp_args += '-static-libstdc++'
endif

executable(
  binary_name,
  files('src/main.cpp'),
  include_directories: include_directories('src/include'),
  dependencies: gtk_dep,
  cpp_args: static_cpp_args,
  link_args: static_cpp_args,
  install: true,
)

test(
  'app metadata validation',
  python,
  args: [config_tool, 'validate'],
)
