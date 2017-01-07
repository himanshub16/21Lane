#!/bin/bash

if [ $# != 1 ]; then
	echo "Please provide a version number."
	exit
fi

VERSION=$1

if [ ! -f "dist/21Lane/21Lane" ]; then
	echo "Build failed. Perhaps!"
	exit
fi

PRESENT_DIRECTORY=$(pwd)
DESTINATION="21lane_"$VERSION"-1"
cd dist
mkdir -p $DESTINATION/opt
mkdir -p $DESTINATION/DEBIAN
mkdir -p $DESTINATION/usr/share/applications

cp 21Lane $DESTINATION/opt -r
cp "$PRESENT_DIRECTORY"/debian/* $DESTINATION/DEBIAN/
cp "$PRESENT_DIRECTORY"/icon.png $DESTINATION/opt/21Lane/icon.png
cp "$PRESENT_DIRECTORY"/21lane.desktop $DESTINATION/usr/share/applications/21lane.desktop

dpkg-deb --build $DESTINATION
