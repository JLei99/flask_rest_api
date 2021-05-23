import requests

BASE = "http://127.0.0.1:5000/"

data = [{"rent":1000, "utilities":200,"groceries":300, "other":200},
{"rent":800,"groceries":400}, {}]

'''
response = requests.put(BASE + "expenses/2/15", data[0])
print(response.json())
response = requests.put(BASE + "expenses/2/16", data[1])
print(response.json())
response = requests.put(BASE + "expenses/2/17", data[2])
print(response.json())

input()
'''


response = requests.get(BASE + "expenses/2/15")
print(response.json())
input()

response = requests.get(BASE + "expenses/2/16")
print(response.json())

#input()
#response = requests.patch(BASE + "expenses/2/17", {"rent":2000})
#print(response.json())

input()
text = "rent"
response = requests.get(BASE + "max/2/groceries")
print(response.text())


"""
response = requests.delete(BASE + "expenses/2/17")
print(response.json())

input()
response = requests.delete(BASE + "expenses/2/17")
print(response.json())
"""

