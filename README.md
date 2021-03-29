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

# Configuration
The 3D Geeks component has a few parameters which can be customised:

Underneath section `[geeks3d]` you can define the following values:

Machine is the name that gets displayed in the push notifications, Default: Klipper

```
machine_name: Klipper
```

 Percentage interval to notify phone, for example when set to 25
 You will be notified when the print hits the: 25%, 50%, 75%, 100% mark
 Default: 10, Minimum: 5, Maximum: 101
 Note: dont want update interval? set this value to 101
 
```
notify_update_interval: 10
```

 Wether or not notify whenever a print starts
 Default: True
```
notify_print_started: True
```

 Wether or not to notify user whenever a print pauses
 Default: True
```
notify_print_paused: True
```

 Wether or not to notify user whenever a print resumes, Default: True
```
notify_print_resumed: True
```

 Wether or not to notify user whenever a print completes
 Default: True
```
notify_print_completed: True
```

 Wether or not to notify user whenever a print fails, the reason will also be put in the notification
 Default: True
```
notify_print_failed: True
```

 Wether or not to notify user whenever a print is cancelled
 Default: True
```
notify_print_cancelled: True
```

 Wether or not to notify user when the server comes online
 Default: True
```
notify_klippy_disconnect: True
```

 Wether or not to notify user when klippy is ready
 Default: True
```
notify_klippy_ready: True
```

 Wether or not to notify user when klippy is shutdown
 Default: True
```
notify_klippy_shutdown: True
```
