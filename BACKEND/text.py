from xata.client import XataClient
xata = XataClient()

data = xata.data().query("Users",
{"columns": ['id','name','email','bio']})
print(data)