rm -f /usr/bin/21lane
ln -s /opt/21Lane/21Lane /usr/bin/21lane

if hash desktop-file-install 2> /dev/null; then
	desktop-file-install /usr/share/applications/21lane.desktop
	chown root:root /usr/share/applications/21lane.desktop
fi

