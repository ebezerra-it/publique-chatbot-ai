import sys
import requests
from markdownify import markdownify as md
from urllib.parse import urlparse
from Context.contextBase import ContextBase, ContextData

class ContextPublique(ContextBase):

    urlEndPointGetAllArticlesFromPublique: str
    publiqueDomain: str


    def __init__(self, urlEndPointGetAllArticlesFromPublique) -> None:
        super().__init__()
        self.urlEndPointGetAllArticlesFromPublique = urlEndPointGetAllArticlesFromPublique
        
        parsedUrl = urlparse(self.urlEndPointGetAllArticlesFromPublique)
        
        if parsedUrl.scheme == '':
            parsedUrl._replace(scheme='https')
        
        self.publiqueDomain =  parsedUrl.scheme + '://' + parsedUrl.netloc


    def loadContextData(self) -> ContextData:
        url = self.urlEndPointGetAllArticlesFromPublique

        contextData = []

        articlesCount = 0
        while url:
            parsedUrl = urlparse(url)
            url = self.publiqueDomain + parsedUrl.path + '?' + parsedUrl.query

            try:
                responseData = requests.get(url)
            except:
                raise SystemError('Unable to retrieve context data from url(' + url + '): ' + str(sys.exc_info()[1]))
            
            jsonData = responseData.json()
            
            for article in jsonData['results']:
                html = '\n\nTítulo: ' + article['title'].strip() + '\nSumário: ' + article['summary'].strip() + '\n Conteúdo: ' + article['text'].strip()
                contextData.append(md(html).replace('(/site', '(' + self.publiqueDomain + '/site'))
                articlesCount += 1

            url = jsonData['next']

        print(articlesCount)
        return ContextData('\n\n'.join(contextData))

    
