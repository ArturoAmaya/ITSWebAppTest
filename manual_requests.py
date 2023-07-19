import urllib.parse as p

params = {'commands':[{'command': 'add', 'payload': {'stuff':90}}, {'command': 'remove', 'payload': {'stuff':90}}], 'cumulative': True}
print(p.urlencode(params))
