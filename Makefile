.PHONY: httpserver dnsserver clean

httpserver:
	chmod +x ./httpserver

dnsserver:
	chmod +x ./dnsserver

clean:
	rm httpserver
	rm -rf bitbusters_cache

default: httpserver dnsserver

.DEFAULT_GOAL := default