"""
Python version of npm yeast
TODO refactor & test
"""
import math
import time

alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
length = len(alphabet)  # 64
t_map = {k: i for i, k in enumerate(alphabet)}
seed = 0
i = 0
prev = None


def encode(num):
    encoded = ''
    while True:
        encoded = alphabet[int(num % length)] + encoded
        num = math.floor(num / length)
        # simulate do-while
        if not (num > 0):
            break
    return encoded


def decode(enc_str):
    decoded = 0
    for i in range(len(enc_str)):
        decoded = decoded * length + t_map[enc_str[i]]
    return decoded


def yeast():
    global prev, seed
    ts = int(time.time() * 1000)
    now = encode(ts)
    if now != prev:
        seed = 0
        prev = now
        return now
    else:
        r = now + '.' + encode(seed)
        seed += 1
        return r


if __name__ == '__main__':
    print(yeast())