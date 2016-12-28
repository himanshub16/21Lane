#!/bin/sh
pyuic5 window.ui -o window.py
pyrcc5 resources.qrc -o resources_rc.py
cp dialog.py ..
cp resources_rc.py ..
