import os

print(os.path.dirname(os.path.abspath(__file__)))
print(os.getcwd())

print(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../public/')))