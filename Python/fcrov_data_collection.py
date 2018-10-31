# -*- coding: utf-8 -*-
"""
Created on Tue Oct 22 08:32:22 2018

@author: hreilly
"""

import time
starttime=time.time()

while True:
    
    from bs4 import BeautifulSoup
    from bs4 import SoupStrainer
    import pandas as pd
    from pandas.core.groupby.groupby import DataError
    import requests
    from requests.exceptions import HTTPError
    from requests.exceptions import Timeout
    from requests.exceptions import TooManyRedirects
    
    # Initiate HTTP request

    try:
        
        # Initial request to Fresno County site
        res = requests.get("https://www.co.fresno.ca.us/departments/county-clerk-registrar-of-voters/election-information/election-results/results-for-june-5-2018-statewide-primary-election", allow_redirects=False, timeout=(10, 30))
        
        # Check status
        res.raise_for_status()
        
    except HTTPError:
        
        # Print description of status response
        print('Could not connect to remote source (fcrov_data.py). Trying again in 2 minutes...')
        
        # Time of capture
        t = time.ctime()
        print(t)
        
        # Set timer to try request again
        time.sleep(120.0 - ((time.time() - starttime) % 120.0))
        
    except Timeout:
        
        print('Connection timed out (fcrov_data.py). Trying again in 2 minutes...')
        
        t = time.ctime()
        print(t)
        
        time.sleep(120.0 - ((time.time() - starttime) % 120.0))
    
    except TooManyRedirects:
        
        print('Connection attempted a redirect (fcrov_data.py). Trying again in 2 minutes...')
        
        t = time.ctime()
        print(t)
        
        time.sleep(120.0 - ((time.time() - starttime) % 120.0))
    
    else:
        
        print('Connection successful (fcrov_data.py).')
        
        ########## Begin processing response from HTTP request
        
        # Create filter with SoupStrainer to limit parsing to main div
        res_filter = SoupStrainer('div',{'id': 'widget_328_7137_5329'})
        
        # Grab the strained soup
        soup = BeautifulSoup(res.content,'lxml',parse_only=res_filter)
        
        ########### Cooking soup / breaking down content
        
        # Create an array of tag attributes to remove
        REMOVE_ATTRIBUTES = [
            'style','style','class','border','align','valign','cellpadding',
            'cellspacing','colspan','width']
        
        # Filter out <hr>
        [x.decompose() for x in soup.findAll('hr')]
        
        # Filter out <hr>
        [x.decompose() for x in soup.findAll('br')]
        
        # Filter out <p>
        [x.decompose() for x in soup.findAll('p')]
        
        # Filter out <h3>
        [x.decompose() for x in soup.findAll('h3')]
        
        # Filter out <h2>
        [x.decompose() for x in soup.findAll('h2')]
        
        # Filter out <link>
        [x.decompose() for x in soup.findAll('link')]
        
        # Look for attributes from array and remove, then pass to soup
        for attribute in REMOVE_ATTRIBUTES:
            for tag in soup.find_all():
                del(tag[attribute])
        
        # Print the final result of all filters and functions (disable after data identification)
        # with open("../data/fcrov_data.html", "w") as file:
            # file.write(soup.prettify())
        
        # ----------------------------------------------- End Soup Functions, Begin Pandas
        
        # Convert soup to data frame objects
        dfs = pd.read_html(str(soup), header=None)
        
        # DataFrame.dropna(axis=0, how='any', thresh=None)
        
        # Define relevant data frames\
        overview_data = dfs[3]
        cc3 = dfs[64]
        cc5 = dfs[66]
        cc7 = dfs[68]
        
        # Drop useless rows
        cc3 = cc3.drop(cc3.index[[1,4,5,7,8,9]])
        cc5 = cc5.drop(cc5.index[[1,4,5,7,8,9]])
        cc7 = cc7.drop(cc7.index[[1,4,5,7,8,9]])
        
        # Var for naming cols
        new_cols = {0:'item', 1:'partyPref', 2:'voteNum', 3:'votePrcnt'}
        
        # Rename columns in single data frames
        cc3.rename(columns = new_cols, inplace = True)
        cc5.rename(columns = new_cols, inplace = True)
        cc7.rename(columns = new_cols, inplace = True)
        
        # Delete empty columns
        cc3 = cc3.dropna(axis=1, how='all', thresh=None)
        cc5 = cc5.dropna(axis=1, how='all', thresh=None)
        cc7 = cc7.dropna(axis=1, how='all', thresh=None)
        
        # Delete empty rows
        cc3 = cc3.dropna(axis=0, how='all', thresh=None)
        cc5 = cc5.dropna(axis=0, how='all', thresh=None)
        cc7 = cc7.dropna(axis=0, how='all', thresh=None)
        
        # Remove NaNs from data
        cc3 = cc3.fillna('')
        cc5 = cc5.fillna('')
        cc7 = cc7.fillna('')
        
        # All relevant data
        # list_df = [cc3, cc5, cc7]
        # all_data = pd.concat(list_df, axis=0, sort=False)
        
        try:
        
            cc3.to_json('../data/cc3.json', orient='table', index=True)
            cc5.to_json('../data/cc5.json', orient='table', index=True)
            cc7.to_json('../data/cc7.json', orient='table', index=True)
            
        except DataError:
            
            print('Error in pandas data processing (fcrov_data.py). Trying again in 2 mins...')
            
            t = time.ctime()
            print(t)
        
            time.sleep(120.0 - ((time.time() - starttime) % 120.0))
        
        except PermissionError:
            
            print('Permission error (fcrov_data.py). Check CSV file. Trying again in 2 mins...')
            
            t = time.ctime()
            print(t)
        
            time.sleep(120.0 - ((time.time() - starttime) % 120.0))
        
        else:
            
            print('Write to file successful. Process will refresh in 10 mins...')
            t = time.ctime()
            print(t)
            
            # Log list (disable in production environment)
            # print(list_df)
            
            # Update data in 10 minute intervals since start of last data update.
            time.sleep(600.0 - ((time.time() - starttime) % 600.0))


