# CS5700 Content Delivery Network
Overview???

# Requirements
- Python 3.8+
- Unix Shell
- SSH
- Dig (Testing)
- WGet/Curl (Testing)
- WireShark (Testing)

# Running
???

# High Level Approach
???


# Testing Overview
The testing of the project was done in three parts, namely HTTP server, DNS server and End-to-End testing.

#### HTTP Server
HTTP testing???

#### DNS Server
- Wireshark was used to examine DNS packet flow. We configure Wireshark to use a custom DNS port and filter it to validate the DNS header and body in a UDP packet.
- The DNS server was tested locally and remotely using following dig command.
```
dig @cdn-dns.5700.network -p 20200 -t A cs5700cdn.example.com
```
- We also tested DNS server using dig with multiple input CDN name.

#### End-to-End
An essential part of this project is end-to-end testing. We feel confident in the ability of our DNS and HTTP servers to work together as a result. End-to-end testing was carried out in isolation using following steps.

- Create a Ubuntu VM to test in isolation.
- Add `nameserver 198.74.61.103` to `/etc/resolv.conf`. Don't remove default nameserver as it will act as fallback. Note: `198.74.61.103` is ip address of dns server `cdn-dns.5700.network`
- Redirect traffic on port `53` of `198.74.61.103` to port `20200`. This is needed as `resolv.conf` by default sends DNS request to port `53` and does not support custom port.
```
sudo iptables -t nat -A OUTPUT -p udp -d 198.74.61.103 --dport 53 -j DNAT --to 198.74.61.103:20200
sudo iptables -t nat -A OUTPUT -p tcp -d 198.74.61.103 --dport 53 -j DNAT --to 198.74.61.103:20200
```
- Run following command to download file
```
wget http://cs5700cdn.example.com:20200/2026_FIFA_World_Cup
```

# Challenges
???

# Work Breakdown
???

# Reference
???
