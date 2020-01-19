foo:
	echo 'do nothing'

install:
	pip3 install --target=./lib -i https://pypi.douban.com/simple pycryptodome

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

conn2:
	python3 client.py
