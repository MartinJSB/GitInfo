from github import Github
from pprint import pprint
import pandas as pd
from getpass import getpass
import matplotlib.pyplot as plt
from tqdm import tqdm
import pdb

#Workaround so I can have my private access token on github publicly
not_so_private_token = ''.join(open('private_access_token.txt').read().splitlines())
g = Github(not_so_private_token)

if g.get_rate_limit().core.remaining < 10:
    print("Github login required for additional calls")
    username = input("Github Username: ")
    password = getpass("Github Password: ")
    try:
        g = Github(username, password)
    except:
        print("Failed to login")
user = None        
print("This program generates pie charts for a Github users Programming Language uses.")
user_input = input("Enter a Github Username: (Press Enter for defualt user) ")

def defualtUser():
    return(g.get_user('SebLague'))

if user_input:
    try:
        user = g.get_user(user_input)
        user.name
    except:
        user = defualtUser()
        print("Couldn't find user, getting user " + user.name + "'s Programming Language uses instead...")
else:
    user = defualtUser()
    print("Getting user " +user.name+ "'s Programming Language uses...")
repos = user.get_repos()

def pushDict(dict, key, value):
    #Value has to be list or int
    if key not in dict:
        dict[key] = value
    else:
        dict[key] += value
    return dict
    
language_loc = {}
language_proj = {}

rate_limit = g.get_rate_limit().core.remaining
for repo in tqdm(repos, total=repos.totalCount):
    rate_limit -= 1
    if not rate_limit:
        print("quitting early, rate limit was exceeded!")
        break
    lang_obj = repo.get_languages()
    for lang in lang_obj:
        language_loc = pushDict(language_loc, lang if lang is not None else 'Other', lang_obj[lang])

    language_proj = pushDict(language_proj, repo.language if repo.language is not None else 'Other', 1)
    

def dictToPieChart(dict, ax, title):
    labels = dict.keys()
    sizes = [dict[key] for key in dict]
    explode = [0 if elem != max(sizes) else 0.1 for elem in sizes]

    # Sort on sizes which is second element in zipped list.
    (labels, sizes, explode) = zip(*sorted(zip(labels, sizes, explode), key=lambda x: x[1]))
    labels = list(labels)
    wedges, texts, percentages = ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=90)
    
    small_wedges = []
    for i, percentage in enumerate(percentages):
        #Only show text on wedges larger than 8% to avoid clutter
        if float(percentage.get_text()[:-1]) < 8:
            percentage.set(alpha = 0)
            texts[i].set(alpha=0)
            #Keep legends list with 7 largest wedges under 8 %
            if len(small_wedges) > 7:
                small_wedges = small_wedges[1:] + [wedges[i]]
            else:
                small_wedges += [wedges[i]]
    
    #Reverse gives largest wedges on top
    small_wedges.reverse()

    ax.legend(handles = small_wedges)
    ax.set_title(title)
    # Equal aspect ratio ensures that pie is drawn as a circle.
    ax.axis('equal')  

fig1, ax1 = plt.subplots(2)
dictToPieChart(language_proj, ax1[0], 'Projects per Programming Language')
dictToPieChart(language_loc, ax1[1], 'Lines of Code per Programming Language')
plt.show()
