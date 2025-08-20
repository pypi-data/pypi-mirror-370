# OASYS1-XRT

This is the OASYS user interface for XRT (https://xrt.readthedocs.io/).
It is in development phase.

## OASYS1-XRT installation as developper

To install the add-on as developper: 

+ git clone https://github.com/oasys-esrf-kit/OASYS1-XRT
+ cd OASYS1-XRT
+ with the python that Oasys is using: python -m pip install -e . --no-deps --no-binary :all:
+ Restart Oasys: python -m oasys.canvas -l4 --force-discovery

## OASYS1-XRT installation as user

To install the add-on as user: 

+ In the Oasys window, open "Options->Add-ons..."
+ Click the button: Add more..."
+ Enter: OASYS1-XRT
+ In the add-ons list, check the option "XRT"
+ Click "OK"
+ Restart Oasys.


## Workspaces with examples

You can use "Open Remote" in Oasys and load

+ Simple example: https://raw.githubusercontent.com/oasys-esrf-kit/OASYS1-XRT/refs/heads/main/example_workspaces/xrt_test.ows
+ ESRF ID09 beamline: https://raw.githubusercontent.com/oasys-esrf-kit/modelling_team_scripts_and_workspaces/refs/heads/main/id09/ID09_ray_tracing_secondary_source_lens_s4_xrt_comparison_v2.ows

