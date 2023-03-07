#@Autor: Diego Rodrigues Pereira

import nmap

# Definindo o objeto para usar o Nmap
nm = nmap.PortScanner()

# Definindo as opções do Nmap
nmap_args = '-sn -Pn -PE -PA21,23,80,3389'

# Escaneando a rede IPv4
nm.scan(hosts='192.168.1.0/24', arguments=nmap_args)

# Imprimindo os resultados
for host in nm.all_hosts():
    if nm[host].state() == 'up':
        print(f'Host : {host} ({nm[host].hostname()})\tState : {nm[host].state()}')
        print(f'MAC Address: {nm[host]["addresses"]["mac"]}')
        print('----------------------------------------------------')

# Escaneando a rede IPv6
nm.scan(hosts='fe80::/64', arguments=f'{nmap_args} -6')

# Imprimindo os resultados
for host in nm.all_hosts():
    if nm[host].state() == 'up':
        print(f'Host : {host} ({nm[host].hostname()})\tState : {nm[host].state()}')
        print(f'MAC Address: {nm[host]["addresses"]["mac"]}')
        print('----------------------------------------------------')
