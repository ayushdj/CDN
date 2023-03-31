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
- localhost was used to test the http server. Before deploying to the replica server, the httpserver was run on our
local machines, and the `wget` command was run. Once this was successful, it was tested remotely.
  - In order to confirm that we received the correct files, we ran a wget on the server that was hosted
  locally and a wget directly from the origin server. Once both files were downloaded, a `diff` command was run
  to see the differences between both files. If there was no difference, that constituted a successful httpserver imp
  lementation.
- To test the caching system, we tested accessing files that don't exist on the replica server and ones that do.
  - We also tested what the cache looks like after loading in all the files after the server was restarted (i.e. the cache
  should have the files based on the last modified dates of all the files in teh cache.)

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
- `httpserver`: The main challenge with the http server was figuring out the caching mechanism.
Initially we went with the `pageviews.csv` file, however that proved to be quite inefficient because
that csv was being loaded in every time the http server redirected a request to the origin server.
Then the implementation changed to a time based LRU (i.e. if the file exists in the server, then the "last
modified" date changes). The code for this was unnecessarily complicated, so we finally changed to
using an OrderedDict() from python's `collections` module.
- `dnsserver`:

# Work Breakdown
- Ayush: all of httpserver and utils.py
- 

# Reference
- httpserver: Python documentation for `urllib`, `os`, `csv`, `collections` and `socketserver` modules.