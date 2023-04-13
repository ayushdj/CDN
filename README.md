# Content Delivery Network
The goal of this project is to build a Content Delivery Network (CDN) that can use DNS redirection to efficiently redirect clients to the replica server with the shortest response time. This will be accomplished by developing a basic Web server capable of handling client requests for content. In addition, the project will create a system that analyzes network performance data, server load data, and cached data on servers to determine the best replica server. The time it takes to download the content, which will typically consist of small files like most Web sites, will be used to measure performance.

# Requirements
- Python 3.10+ (Very important as we have used some features from Python 3.10. We went with 3.10 as its installed on given remote servers)
- Unix Shell
- SSH
- Scamper
- Dig (Testing)
- WGet/Curl (Testing)
- WireShark (Testing)

# High Level Approach
1. In Python, create a DNS server that can resolve an example CDN name and port. We will parse the incoming DNS question and then send answer in response by sending A type IP address.
2. We will use geo location incoming IP address and HTTP server to determine closest HTTP server on DNS.
3. We will also ping src ip from http server to calculate round trip time (RTT). Then we will call the RTT endpoint from DNS on all HTTP server to determine least RTT.
4. The RTT logic will be used as fallback for geo location.
5. Send refused response for all other DNS queries.
6. In Python, create a simple HTTP server that will be served by all replica servers.
7. The HTTP server will look in the cache directory for the request file. If it finds the file, it returns the cached file.
8. If the requested file is not in cache, we retrieve it from the origin server. The server script will be given the hostname of the origin server. If the file is not found the we return 404.
9. If the server is shut down, we will repopulate the cache based on the date the file was last modified. If the cache does not exist, we create a new directory and pre-populate it. And every time we access a file from the cache, we update the file's "last modified" attribute.
10. We will also have Shell scripts to deploy, run and stop the CDN (i.e DNS and all replica HTTP servers)

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
- Testing dig with Surfshark VPN to check if DNS server was responding with appropriate IP.

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
- **httpserver**: The main challenge with the http server was figuring out the caching mechanism.
Initially we went with the `pageviews.csv` file, however that proved to be quite inefficient because
that csv was being loaded in every time the http server redirected a request to the origin server.
Then the implementation changed to a time based LRU (i.e. if the file exists in the server, then the "last
modified" date changes). The code for this was unnecessarily complicated, so we finally changed to
using an OrderedDict() from python's `collections` module.
- **dnsserver**: Understanding the headers and payload for DNS requests and responses was a major challenge. I used WireShark to interpret the UDP packets and determine how to make it work. Another challenge was to test the DNS and HTTP servers jointly. We could test it all separately, but we wanted to see how everything worked together. For this, we devised end-to-end testing in isolation (details in testing overview).
- **[deploy,run,stop]CDN**: Most of the stuff with this scrips was pretty simple. However, one minor challenge was understanding the use of SSH to deploy and run remote commands, as well as becoming acquainted with Shell script.

# Work Breakdown
- Ayush: 
  - Implemented the core functionality of `httpserver` and created utilities (util.py) for codebase.
- Shubham: 
  - Implemented the `dnsserver` handling of question and responding with appropriate answer.
  - Worked on optimizing cache on http server
  - Handling geo location.
  - the `[deploy,run,stop]CDN` shell scripts and end-to-end testing.

# Reference
1. Python documentation for `urllib`, `os`, `csv`, `collections` and `socketserver` modules.
2. DNS query message format. Firewall.cx, Retrieved March 30, 2023, from https://www.firewall.cx/networking-topics/protocols/domain-name-system-dns/160-protocols-dns-query.html 
3. DNS message format. GeeksforGeeks. Retrieved March 30, 2023, from https://www.geeksforgeeks.org/dns-message-format/ 
4. Calculating distance between two geolocations in python. Medium. Retrieved April 13, 2023, from https://towardsdatascience.com/calculating-distance-between-two-geolocations-in-python-26ad3afe287b 
