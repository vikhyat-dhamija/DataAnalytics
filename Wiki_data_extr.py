#these are the packages impoted to be used in the program 
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np

#This is the function to extract the data from the wikipedia
def data_wiki(year):
    #This is the link for getting to the page of Wikipedia for the particular year 
    link = "https://en.wikipedia.org/wiki/International_cricket_in_"+str(year)
    #This makes requests to the link 
    wp = requests.get(link)
    #convert the content of the webpage into XML format
    bs = BeautifulSoup(wp.content, 'lxml')

    #Here we access all the tables in the body
    t_body=bs.find_all('tbody')

    #created a datframe with certain columns
    df_= pd.DataFrame(columns=["Year","Country","Rating"])

    x=0

    #here we loop across each table in all the tables 
    for table in t_body:
        #Then we access all the rows in each table
        rows = table.find_all('tr')
        
        #then we move to each row in the rows array
        for j,row in enumerate(rows[::1]) :
            #then we access all the columns in each row
            cols=row.find_all('th')
            cols=[x.text.strip() for x in cols]

            #then access the row with first column as rank
            if len(cols) > 0 and cols[0] == "Rank":
                x+=1
                #here we access the ranks of the T20 
                #note that for T20 x is 3 and for some years as the ICC has not used T20 format ranking 
                #then we used x as 2 to access the 50 overs format as they closely resemble the T20 format
                if x == 3:
                    #here we access all the top 10 teams to get their ranks
                    for m in range(11):
                        cols1=rows[j+1+m].find_all('td')
                        cols1=[x.text.strip() for x in cols1]
                        df_=df_.append(pd.Series([year,cols1[1],cols1[4]],index = df_.columns), ignore_index =True)
                    break
    
    #Here the Data was written into CSV file in the current working directory
    df_.to_csv('ratings.csv', mode='a', header=False)

if __name__ == "__main__":
    year=2007
    # Note the range of i was changed to access the data for various years
    for i in range(5):            
        data_wiki(year+i)

