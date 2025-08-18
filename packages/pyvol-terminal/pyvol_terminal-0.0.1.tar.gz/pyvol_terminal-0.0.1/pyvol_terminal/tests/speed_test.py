
from py_vollib.black.implied_volatility import implied_volatility
import py_vollib_vectorized

import time
price = 10.
S = 100.
K=102.
t=0.002
r=0.05
q=0.02
flag="c"




s =time.time()
for _ in range(20000):
    py_vollib_vectorized.vectorized_implied_volatility_black(price, S, K, r, t, flag)

print(time.time() - s)
print(py_vollib_vectorized.vectorized_implied_volatility_black(price, S, K, r, t, flag))





s =time.time()
for _ in range(20000):
    implied_volatility(price, S, K, r, t, flag)

print(time.time() - s)
print(implied_volatility(price, S, K, r, t, flag))
