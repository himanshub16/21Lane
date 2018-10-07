## [21Lane](https://github.com/himanshub16/21lane/)

**This project is no longer maintained.**

A simple, point-to-point / group file sharing solution.
For old version, consider [branch v1](https://github.com/himanshub16/21lane/tree/v1), or find older releases [here](https://drive.google.com/open?id=0B7BS3b01XjwCOTlPYk00UE1IQ3c).

## What can I do with this ?
* Share some folder on your system, to be available to other device/group.
* Download from other device / from other peers on the same group.

## Are there any requirements ?
No. The application is built to click and run.

## I cannot access my system using IP address!
Your computer should be accessible by your IP address.<br> 
This is a problem when you are behind a router, proxy, wifi etc.<br>
For systems on same network & behind proxy, make sure `localhost` is not using proxy settings.<br>
There are some geeky methods like port forwarding, you can go for.

## What if I don't want to share to other peers ? Any use in that case ?
* Leave the **Group URL** field empty, and start sharing.
* You have the link. Copy that link and use it the way you want.

If you are a developer, trying to tinker with it, just install the dependencies from `requirements.txt` file.

## How to tinker with / contribute to it ?
```
git clone https://github.com/himanshub16/21lane.git 
cd 21lane 
virtualenv -p python3 myftp
source myftp/bin/activate 
pip3 install -r requirements.txt 

python3 21Lane/start.py
```
You are all set. 
