# JSON-structure

```sh
./json-structure.py -f example.json
```

### Identified types / structures

```json
{
  "1": "String",
  "2": "Number",
  "3": {
    "name": "String",
    "surname": "String",
    "age": "Number"
  },
  "4": [
    "3"
  ],
  "5": [
    "Number"
  ],
  "6": {
    "integers": "5",
    "numbers": "5"
  },
  "7": [],
  "8": {
    "person": "3",
    "people": "4",
    "silly": "6",
    "emptylist": "7"
  }
}
```

Note that the last identified structure is the same as the entire JSON result
output.

### Result

```json
{
  "person": "3",
  "people": "4",
  "silly": "6",
  "emptylist": "7"
}
```

#
