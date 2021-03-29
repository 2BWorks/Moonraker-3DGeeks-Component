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
$ ssh pi@klipper_ip
```

2. Clone 3D Geeks Component into home folder

```
cd ~
git clone https://github.com/2BWorks/Moonraker-3DGeeks-Component
cd Moonraker-3DGeeks-Component
```

3. Copy component into Moonraker Components

_substitute: your components folder if you used kiauh it should be similar _
```
cp geeks3d.py /home/pi/moonraker/moonraker/components/geeks3d.py
```

4. Update moonraker.conf

Copy the contents from `example_geeks3d_moonraker.conf` and paste it into `moonraker.conf`

5. Make adjustments to the config as you see fit.

6. Reboot system

```
sudo reboot
```

7. Verify 
On your webbrowser of choice head over to:
```
http://{klipper_ip}/server/geeks3d/push_token
```
Should see something like this:

```
{
  result: {
    push_token: "XXXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXXX",
    is_fresh: true
  }
}
```
8. Setup the app
```
Open side menu > Integrations > Klipper > '+'-icon > Follow setup instructions
```



