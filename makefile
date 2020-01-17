run:
	python3 server.py

clean:
	rm *~

rmdb:
	rm UserInfo.db

showdb:
	python3 peep.py

conn:
	python3 client.py
