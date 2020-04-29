#!/usr/bin/env python3.8

import gene

p = gene.Parser("""((2+1-5)+2*10+1)*2""")

result = p.expr()
if result is None or not p.eof():
    print("result is", result)
    print("EOF:", p.eof())
    print(p.data)
else:
    print(result)
