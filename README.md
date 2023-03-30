# CS5700_CDN


# Testing
### End to End
- Create a Ubuntu VM to test in isolation.
- Add `nameserver 198.74.61.103` to /etc/resolv.conf. Don't remove default nameserver as it will act as fallback.
- Redirect traffic on port `53` to `198.74.61.103:20200`
```
sudo iptables -t nat -A OUTPUT -p udp -d 198.74.61.103 --dport 53 -j DNAT --to 198.74.61.103:20200
sudo iptables -t nat -A OUTPUT -p tcp -d 198.74.61.103 --dport 53 -j DNAT --to 198.74.61.103:20200
```
- Run following command to download file
```
wget http://cs5700cdn.example.com:20200/2026_FIFA_World_Cup
```