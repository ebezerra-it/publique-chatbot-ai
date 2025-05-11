from Context.contextPublique import ContextPublique, ContextData
import os

def main():
    context = ContextPublique('https://www.frg.com.br/site/rest/xpublique/info/?format=json')
    #print('loading context data')
    data = context.loadContextData()
    print(len(data))

if __name__ == "__main__":
    main()