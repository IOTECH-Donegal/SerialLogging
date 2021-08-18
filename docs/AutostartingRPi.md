To automate running scripts at startup, add a line to /etc/rc.local

    sudo /home/pi/autoexec.sh

Note that in modern **systemd** based systems, you may need to do this differently.

In /home/pi, a shell script called **autoexec.sh** is run each time the system reboots.

This file can be edited to start multiple other processes.

By default, only SerialMux1.py is executed.






