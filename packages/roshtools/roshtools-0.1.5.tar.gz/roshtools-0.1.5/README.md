# roshtools 🛠️


[![PyPI version](https://badge.fury.io/py/roshtools.svg)](https://pypi.org/project/roshtools/)
[![Build](https://github.com/roshandec29/roshtools/actions/workflows/python-publish.yml/badge.svg)](https://github.com/roshandec29/roshtools/actions)


A lightweight Python utility library with handy functions for **strings, files, timers, and networking**.  
Save time on common coding tasks with clean, reusable helpers.  

---

## ✨ Features
- 🔤 String helpers (`slugify`, `camel_to_snake`)
- 📂 File helpers (`read_file`, `write_file`)
- ⏱️ Time a function takes to execute (`timer`)
- 🌐 Simple networking (`get_json`)

---

## 📦 Installation
```bash
pip install roshtools
```
## 🚀 Usage Examples

### 1. String Utilities
```python
from roshtools.strings import slugify, camel_to_snake

print(slugify("Hello World!"))       # hello-world
print(camel_to_snake("CamelCase"))   # camel_case
```
### 2. File Utilities
```python
from roshtools.files import write_file, read_file

write_file("hello.txt", "Hello, World!")
print(read_file("hello.txt"))        # Hello, World!
```
### 3. Timing Functions
```python
from roshtools import timer

@timer("Processing")
def slow_function():
    import time
    time.sleep(2)
    return "done"

slow_function()
# Output: Processing: 2.0001 seconds
```
### 4. Networking
```python
from roshtools import get_json

data = get_json("https://api.github.com")
print(data["current_user_url"])
```


