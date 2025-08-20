# OASYS1-XRT

This is the official user interface for SHADOW4 (https://github.com/oasys-kit/shadow4). It is presented as an OASYS add-on.

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

