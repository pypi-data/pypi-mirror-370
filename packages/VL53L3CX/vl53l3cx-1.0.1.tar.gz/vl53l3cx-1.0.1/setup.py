from setuptools import setup, Extension

extension = Extension(
    'vl53l3cx_python',
    extra_compile_args=['-std=c99'],
    include_dirs=['.', 'api/core', 'api/platform'],
    sources=[
        'api/core/vl53lx_api.c',
        'api/core/vl53lx_api_calibration.c',
        'api/core/vl53lx_api_core.c',
        'api/core/vl53lx_api_debug.c',
        'api/core/vl53lx_api_preset_modes.c',
        'api/core/vl53lx_core.c',
        'api/core/vl53lx_core_support.c',
        'api/core/vl53lx_dmax.c',
        'api/core/vl53lx_hist_algos_gen3.c',
        'api/core/vl53lx_hist_algos_gen4.c',
        'api/core/vl53lx_hist_core.c',
        'api/core/vl53lx_hist_funcs.c',
        'api/core/vl53lx_hist_char.c',
        'api/core/vl53lx_nvm.c',
        'api/core/vl53lx_nvm_debug.c',
        'api/core/vl53lx_register_funcs.c',
        'api/core/vl53lx_sigma_estimate.c',
        'api/core/vl53lx_silicon_core.c',
        'api/core/vl53lx_wait.c',
        'api/core/vl53lx_xtalk.c',
        'api/platform/vl53lx_platform.c',
        'api/platform/vl53lx_platform_init.c',
        'api/platform/vl53lx_platform_ipp.c',
        'api/platform/vl53lx_platform_log.c',
        'python_lib/vl53l3cx_python.c'
    ]
)

setup(
    name='VL53L3CX',
    version='1.0.1',
    description='VL53L3CX distance sensor driver for Raspberry Pi',
    maintainer='Jakub Frgal',
    maintainer_email='buemicz@gmail.com',
    url='https://github.com/FrgyCZ/VL53L3CX-python',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    ext_modules=[extension],
    install_requires=['smbus2'],
)
