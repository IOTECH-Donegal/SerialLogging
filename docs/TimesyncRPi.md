Making time work
A Raspberry Pi has no real-time clock (RTC). You must either:
- Fit an RTC as a hardware module.
- Synch using NTP over a network. If you have an Internet connection, this occurs by default.
- Synch using the GPS.

A script file is provided as SetUTC.py which carries out this function.
