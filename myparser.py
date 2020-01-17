def parse_addr_str(addr):
	i = 0
	ip = ''
	port = ''
	while i < len(addr):
		if   addr[i] == '(':
			pass
		elif addr[i] == ',':
			break
		elif addr[i] != '\'':
			ip = ip + addr[i]
		i = i+1
	i = i+1
	while i < len(addr):
		if   addr[i] == ')':
			break
		elif addr[i] != ' ':
			port = port + addr[i]
		i = i+1
	return (ip, int(port))


