"""
Python version of npm yeast
Used in websockets for cache-busting
"""
import math
import time


class Yeast:

    alphabet = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz-_'
    length = len(alphabet)  # 64
    t_map = {k: i for i, k in enumerate(alphabet)}
    seed = 0
    prev = None

    @classmethod
    def yeast(cls):
        ts = int(time.time() * 1000)
        now = cls.encode(ts)
        if now != cls.prev:
            cls.seed = 0
            cls.prev = now
            return now
        else:
            r = now + '.' + cls.encode(cls.seed)
            cls.seed += 1
            return r

    @classmethod
    def encode(cls, num):
        encoded = ''
        while True:
            encoded = cls.alphabet[int(num % cls.length)] + encoded
            num = math.floor(num / cls.length)
            # simulate do-while
            if not num > 0:
                break
        return encoded

    @classmethod
    def decode(cls, enc_str):
        enc_str = enc_str.split('.')[0]
        decoded = 0
        for e in enc_str:
            decoded = decoded * cls.length + cls.t_map[e]
        return decoded


if __name__ == '__main__':
    print(Yeast.yeast())
