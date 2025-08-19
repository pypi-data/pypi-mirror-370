


from KeyisBClient import Url

u = Url()

u.path = '/examplePath/2'
u.hostname = '43.54.23.5:2433'
u.scheme = 'gn'
u.params = {'d': 6}

print(u.getUrl())
