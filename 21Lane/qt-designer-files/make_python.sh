#!/bin/sh
pyuic5 dialog.ui -o dialog.py
pyrcc5 resources.qrc -o resources_rc.py
cp dialog.py ..
cp resources_rc.py ..
