Python WiFi Positionion system
==============================

The purpose of this system is ultimately to act as an indoor positioning system using RSSI trilateration from multiple receivers. The code is under development. Currently it is capable of capturing packets from multiple USB WiFi cards attached to the system, and filtering those packets based on whatever criteria is nessecary. The data is then published to a Redis server on the network, where another machine is listening and collating it.

###Sniffer variants

There are two sniffer files:
* *sniffer.py*: Gets packets using scapy's sniff function. For some reason, this appears to run extremely slowly, and another method had to be devised.
* *sniffer_2.py*: Parses _dumpcap_'s pcap output, and feeds that data to scapy for parsing. This runs much faster. It could be improved even more by parsing the data manually instead of relying on scapy, but that will be done later.

#Layout

The idea behind this system is to figure out the location of a transmitter based on its RSSI, or received signal strength indicator, at multiple known locations around a building. There are many methods to accomplish this, but I will focus on two:
    
###Relative position calculation
In this scheme, the signal strengths will be treated as rough distance measurements. They will form the radii for circles centered on each receiver, and the position of the transmitter will be calculated using trilateration. Using this scheme, the accuracy of the information relies heavily on the accurate positioning of each receiver.

There are, of course, problems with this naiive method. Most importantly, signal strength does not tend to fall off perfectly linearly (or even exponentially) as distance increases. This is because of obstructions, and the fact that signals can take multiple paths around/through these obstructions. As such, a scheme must be devised to compensate for this.

#####More accurate position calculation
In order to calculate the position of the transmitter taking into account discrepancies in signal strength, a lookup map must be generated. Say a person was to walk in a one meter by one meter grid around the buildin to be mapped. The system would store the signal strength fingerprint for each grid point, and then be able to much more accurately interpolate the position in realtime.

###Fingerprint positioning
This scheme does not rely on knowing the position of each transmitter, as long as they don't move during operation. It doesn't care about signal strength attenuation either. In this scheme, instead of figuring out position of a transmitter, it figures out relative closeness to a known *fingerprint*. This means that when the system is first started, a training phase must be completed in which all of the fingerprints in the system are entered.

A fingerprint simply consists of a set of RSSI measurements (possibly averaged over a period of time) that correlate to a specific location. Then, when the system receives new data, it can attempt to correlate it to known fingerprints, and give a statistic 'closeness' to each one.
