httpserver:
	cp httpserver.py httpserver && chmod +x httpserver

clean:
	rm httpserver
	rm -rf bitbusters_cache