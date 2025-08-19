



from KeyisBClient import *






url1 = Url('https://example.com/path?query=1#fragment')

url2 = Url(url1)

print(url1.getUrl())
print(url2.getUrl())

