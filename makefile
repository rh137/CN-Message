install:
	echo 'do nothing'

clean:
	rm *~

rmdb:
	rm UserInfo.db

showdb:
	python3 peep.py

run:
	python3 server.py

conn:
	python3 client.py


