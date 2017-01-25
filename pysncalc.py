#!/usr/bin/env python

from math import log, ceil
import sys

MAX_IP = (2 ** 32) - 1

def ip2dec(addr):
    ip_int_list = map(int, addr.split('.'))
    dec_ip = 0
    offset = 3

    for num in ip_int_list:
        dec_ip |= num << (offset * 8)
        offset -= 1 

    return dec_ip

def dec2ip(num):
    ip_int_list = []
    offset = 3

    while offset >= 0:
        ip_int_list.append(num >> (offset * 8) & 255)
        offset -= 1

    return '.'.join(map(str, ip_int_list))

def get_network_addr(ip, mask):
    dec_ip = ip2dec(ip)
    dec_mask = ip2dec(mask)
    
    dec_net = dec_ip & dec_mask
    return dec2ip(dec_net)

def get_bcast_addr(ip, mask):
    net = get_network_addr(ip, mask)
    bcast_portion = dec2ip(ip2dec(mask) ^ MAX_IP)
    
    net_list = map(int, net.split('.'))
    bcast_list = map(int, bcast_portion.split('.'))

    for i in range(len(net_list)):
        bcast_list[i] += net_list[i]

    return '.'.join(map(str, bcast_list))

def cidr2mask(cidr):
    mask_dec = (2 ** cidr - 1) << (32 - cidr) 
    return dec2ip(mask_dec)

def mask2cidr(mask):
    mask_dec = ip2dec(mask)
    cidr = 32 - int(log((mask_dec ^ MAX_IP) + 1, 2))
    return cidr

def get_num_hosts(mask):
    return ip2dec(mask) ^ MAX_IP - 1

def gen_subnet_data(ip, mask):
    net = get_network_addr(ip, mask)
    bcast = get_bcast_addr(ip, mask)
    num_hosts = get_num_hosts(mask)
    first_usable = dec2ip(ip2dec(net) + 1)
    last_usable = dec2ip(ip2dec(bcast) - 1)
    next_network_addr = dec2ip(ip2dec(bcast) + 1)

    print("Network Address:   {0}".format(net))
    print("Subnet Mask:       {0}".format(mask))
    print("Broadcast Address: {0}".format(bcast))
    print("Usable Hosts:      {0}".format(num_hosts))
    print("Usable Host Range: {0} - {1}".format(first_usable, last_usable))
    print("================================")

    return next_network_addr

def gen_subnet_data_cidr(ip_cidr):
    ip = ip_cidr.split('/')[0]
    mask = cidr2mask(int(ip_cidr.split('/')[1]))
    next_network_addr = gen_subnet_data(ip, mask)
    return next_network_addr

def gen_new_subnet(base_ip, base_mask, num_hosts):
    new_cidr = 32 - int(ceil(log(num_hosts + 2, 2)))
    old_cidr = mask2cidr(base_mask)

    if (new_cidr >= old_cidr and new_cidr <= 32):
        new_mask = cidr2mask(new_cidr)
        next_network_addr = gen_subnet_data(base_ip, new_mask)
        return [next_network_addr, new_mask]

    else:
        print("Not Possible to Subnet!")
        return 0

def gen_new_subnets_multi(base_ip, base_mask, num_hosts_list):
    for num_hosts in num_hosts_list:
        next_base = gen_new_subnet(base_ip, base_mask, num_hosts)
        base_ip = next_base[0]
        base_mask = next_base[1]

        if base_ip == 0:
            return 0

def gen_new_subnet_cidr(base_ip_cidr, num_hosts):
    base_ip = base_ip_cidr.split('/')[0]
    base_mask = cidr2mask(int(base_ip_cidr.split('/')[1]))
    next_network_addr = gen_new_subnet(base_ip, base_mask, num_hosts)
    return next_network_addr

def gen_new_subnets_cidr_multi(base_ip_cidr, num_hosts_list):
    base_ip = base_ip_cidr.split('/')[0]
    base_mask = cidr2mask(int(base_ip_cidr.split('/')[1]))
    gen_new_subnets_multi(base_ip, base_mask, num_hosts_list)

def print_help():
    print("\n")
    print("================================")
    print("     Subnet Calculator Help")
    print("================================\n")
    print("{0} -i <IP> <MASK>               Give info for the given subnet in IP and MASK format".format(sys.argv[0]))
    print("{0} -c <IP>/<CIDR>               Give info for the given subnet in IP/CIDR format".format(sys.argv[0]))
    print("{0} -n <IP> <MASK> <# HOSTS,...,N>     Generate a new subnet from the base IP and MASK to accomodate # HOSTS given in a comma seperated list with no spaces".format(sys.argv[0]))
    print("{0} -nc <IP>/<CIDR> <# HOSTS,...,N>     Generate a new subnet from the base IP/CIDR to accomodate # HOSTS given in a comma sperated list with no spaces".format(sys.argv[0]))
    print("\nExamples:\n")
    print("{0} -i 192.168.1.55 255.255.255.0".format(sys.argv[0]))
    print("{0} -i 192.168.1.55/24".format(sys.argv[0]))
    print("{0} -n 192.168.1.0 255.255.255.0 65,70,12".format(sys.argv[0]))
    print("{0} -nc 192.168.1.0/24 65,70,12".format(sys.argv[0]))

def print_header():
    print("================================")
    print("     Subnet Calculator Data")
    print("================================")

def main():
    if len(sys.argv) < 2:
        print_help()

    elif sys.argv[1] == '-i':
        if len(sys.argv) < 4:
            print_help()
        else:
            print_header()
            gen_subnet_data(sys.argv[2], sys.argv[3])

    elif sys.argv[1] == '-c':
        if len(sys.argv) < 3:
            print_help()
        else:
            print_header()
            gen_subnet_data_cidr(sys.argv[2])

    elif sys.argv[1] == '-n':
        if len(sys.argv) < 5:
            print_help()
        else:
            print_header()
            host_num_list = sorted(map(int, sys.argv[4].split(',')))
            host_num_list.reverse()
            gen_new_subnets_multi(sys.argv[2], sys.argv[3],  host_num_list) 

    elif sys.argv[1] == '-nc':
        if len(sys.argv) < 4:
            print_help()
        else:
            print_header()
            host_num_list = sorted(map(int, sys.argv[3].split(',')))
            host_num_list.reverse()
            gen_new_subnets_cidr_multi(sys.argv[2], host_num_list)

    else:
        print_help()
    


if __name__ == '__main__':
    main()
