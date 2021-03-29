# 3D Geeks: Moonraker Component
This Moonraker component plugin allows users to receive remote push notifications directly from klipper into the 3D Geeks Android Appplication


# Requirements:
- Raspberry Pi or any other type of server connected to your printer running the following software:
  - Installed Klipper: https://github.com/KevinOConnor/klipper
  - Installed Moonraker API: https://github.com/Arksine/moonraker
  - Note: There is an awesome all-in-one installer available from here: https://github.com/th33xitus/kiauh
- Android Phone or Tablet
  - Installed 3D Geeks Application: https://www.3dgeeks.app/u/android


# Getting started:
Got all the requirements running?! Great! Let's get started:
Any command from here on out assumes you have installed the above requirements, and is runnning from the `pi` username, if you are using another username please be sure to subsitute the username where applicable.

1. SSH into your klipper server

```
$ ssh pi@local_ip
```

1. Clone 3D Geeks Component 
