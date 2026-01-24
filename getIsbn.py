#library
import requests
import re
#get api response
url= f"https://openlibrary.org/search.json?title=the%20sea%20of%20monsters&author=rick%20riordan&fields=key,%20title,%20editions&limit=1"
response = requests.get(url)
key= response.json()['docs'][0]['editions']['docs'][0]['key']
ol=re.split('/', key)
#starts with ol
olid=ol[2]
#print olid
print(olid)
#get books from library that do not have olid

#add olid to database