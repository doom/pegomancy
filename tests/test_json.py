#!/usr/bin/env python3.8

import json
import gene

value = {
    "object": {
        "list": [1, 2, 3],
        "integer": 123,
        "float": 123.123,
        "string": "123",
        "bool": True
    }
}

data = json.dumps(value, indent=2)

p = gene.Parser(data)
result = p.value()
if result is None or not p.eof():
    print("result is", result)
    print("EOF:", p.eof())
    print(p.data)
else:
    print(result)
