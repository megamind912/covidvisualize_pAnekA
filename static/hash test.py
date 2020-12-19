import hashlib

passw = hashlib.sha224(bytes(input(), encoding='utf-8'))
passw = passw.hexdigest()
print(passw)
