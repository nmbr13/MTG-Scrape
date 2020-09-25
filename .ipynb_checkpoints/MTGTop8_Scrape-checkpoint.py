#!/usr/bin/env python
# coding: utf-8

# In[18]:


from bs4 import BeautifulSoup as bs
import re
import pandas as pd
import networkx as nx
import requests
import json

import os

dfs = []

# In[19]:


def get_colors(r):
  d = requests.get('http://api.scryfall.com/cards/named?fuzzy=' + str(r.replace(' ','+')))
  j = json.loads(d.text)

  if j['color_identity'] == []:
    return('None')
  else:
    return(str(j['color_identity']))
 
def get_deck_info(deck_url):
  page = requests.get(deck_url)
  soup = bs(page.content, 'lxml')  
  title = soup.find("td", attrs={'class':'S16'}).contents

  deck_name = re.split("#\d{1,2}(?:-\d)*",title[0])[1].split(" - ")[0].strip()
  player_name = title[1].text.strip()

  # # Get Prices
  prices = soup.find_all("span", attrs={'class':'O14'})
  price_breakout = [x.text for x in prices]
  return([deck_name,deck_url, player_name,int(price_breakout[0]),int(price_breakout[1]),float(price_breakout[2]),int(price_breakout[3])])  

def get_decks(list):
    deck_list = []
    for each in list:
        url = each
        page = requests.get(url)
        soup = bs(page.content, 'html.parser')
        links = soup.find_all('a')
        for l in links:
            q = l.get('href')
            if '&d' in q:
                deck_list.append('http://www.mtgtop8.com/' + q)
    return deck_list

def get_avg_price(price,f_mat):
    ['MO','ST',"PI",'PAU',"EDH"]
    if f_mat=='EDH':
        return price/100
    else:
        return price/60
# In[20]:




# get Decks
formats = ['MO','ST',"PI",'PAU',"EDH"]
for each in formats:
    format_name = each
    url = 'http://www.mtgtop8.com/format?f='+ each
    page = requests.get(url)
    soup = bs(page.content, 'html.parser')
    archetypes_URL = []
    archetype_Names = []
    for link in soup.find_all('a'):
        l = link.get('href')
        if 'archetype' in l:
            archetypes_URL.append('http://www.mtgtop8.com/' + link.get('href'))
            archetype_Names.append(link.text)
    print("Archetypes:",len(archetypes_URL))


    # In[28]:

    deck_urls=[]
    deck_urls = get_decks(archetypes_URL)
    print("Decks:", len(deck_urls))


    # In[29]:


    deck_info = []

    import concurrent.futures 
    with concurrent.futures.ThreadPoolExecutor(max_workers=30) as executor:
        # Start the load operations and mark each future with its URL
        future_to_url = {executor.submit(get_deck_info, url): url for url in deck_urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                data = future.result()
                deck_info.append(data)
            except Exception as exc:
                print('%r generated an exception: %s' % (url, exc))


    # In[23]:


    deck_info
    df = pd.DataFrame(deck_info)
    df.columns = ["Deck Name","URL","Player","Card Kingdom", "TCG Player", "Manatraders", "Cardhoarder"]
    for c in df.columns:
        data_types = set(df[c].apply(type))
    f = []
    for each in range(len(df)):
        f.append(format_name)
        
    df['Format'] = f
    dfs.append(df)

    file_name = format_name + ".csv"
    df.to_csv(file_name, index=False)  
    
    avgPrice = []
    for each in range(len(df)):
        local_df = df.iloc[each]
        avgPrice.append(get_avg_price(local_df['Card Kingdom'] + local_df['TCG Player']/2,local_df['Format']))

    df['Avg. Card Price'] = avgPrice
    df.groupby('Format').mean()

    # In[24]:
big_df = pd.concat(dfs)
big_df.to_csv("combo_decks.csv")

    # a = df.sort_values('Cardhoarder', ascending=True)


    # # In[25]:


    # df[df['TCG Player']<1000]


    # In[26]:


    # compression_opts = dict(method='zip', archive_name='out.csv')  

    # df.to_csv('out.zip', index=False, compression=compression_opts)  


# In[13]:


# data = pd.DataFrame()
# things = []
# csv = "Deck,Player,Placement,Card \n"

# for link in deck_urls:
#     get_deck_info(link)


#     player_name = p[1]
#     placement = re.split('#',p[0])[1][0]
#     cards = []
#     colors = []
#     for each in c:
#         e = each.text
#         cards.append(each.text)
# #         print(e)
# #         card_colors = get_colors(e)
# #         colors.append(card_colors)
        
#     for i in range(len(cards)):
# #         csv = csv + deck + "," + player + "," + placement + "," + cards[i]+ "," + colors[i] + "\n"
           
#       things.append((deck,player,placement,cards[i]))
            
# # f= open("data.csv","w+")
# # f.write(csv)
# # f.close


# # In[ ]:


# data = pd.DataFrame(things, columns=['Deck','Player','Placement','Card Name'])
# data.head()


# # In[ ]:


# r = 'Delver of Secrets'
# d = requests.get('https://api.scryfall.com/cards/named?fuzzy=' + str(r.replace(' ','+')))
# j = json.loads(d.text)

# j

# #   if j['colors'] == []:
# #     return('None')
# #   else:
# #     return(str(j['colors']))




# In[ ]:




