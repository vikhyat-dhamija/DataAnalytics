import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np

#This is the main data extractor function for extracting data from the ESPN Website
def data(team,year):
    #This is the link from which each year and team score cards are accessed
    link = 'https://stats.espncricinfo.com/ci/engine/records/team/match_results.html?class=3;id='+str(year)+';team='+str(team)+';type=year'
    #Page is requested from the link
    wp = requests.get(link)
    #Then the content of the page are converted into xml format using the Beautiful Soup package in the Python
    bs = BeautifulSoup(wp.content, 'lxml')
    # Here we access all the tables in the web page
    tb = bs.find_all('tbody')
    
    #Here we create a dataframe with the following columns 
    m_df= pd.DataFrame(columns=["MatchID","Team1","Team2","Winner","Year","Ground", "Runs", "Fours","Sixes","MatchTime","Ha1","Ha2","T1w","T2w","T1b","Groundcapacity","AvgSR"])

    #Here Now we loop into all the tables 
    for t in tb[0:4:1] :
        #then we access all the rows for each table
        rows = t.find_all('tr')
        #then we access each row in each of the table
        for row in rows[::1]:
            #Then we access all the columns in the table
            cols=row.find_all('td')
            #here we access the last column to extract the score card of the table
            mid=cols[-1].text.strip()
            #then we try to get result in desired format
            mid=mid.split(' ')[-1]
            #Using regex search we search the hyperlink to access the score card
            match = re.search(r'href=[\'"]?([^\'" >]+)',str(cols[-1]))
            #this is the url or link to access the score card of each match
            m_url="https://stats.espncricinfo.com" + match.group(1)
            
            #Then we access the text or the value of each column
            cols2=[x.text.strip() for x in cols]

            #then we extract the year of the score card or the match 
            year=cols2[5][-4:]

            #then we pass the year and the url and the team1 and team2 for extracting the daa related to that match
            z= data2(m_url,cols2[0],cols2[1],year)
            #the above data was in the form of dataframe and was then appended to the main dataframe created for the resulting final dataframe
            m_df=m_df.append(pd.Series([mid,cols2[0],cols2[1],cols2[2],year,cols2[4],z[0],z[1],z[2],z[3],z[4],z[5],z[6],z[7],z[8],z[9],z[10]],index = m_df.columns), ignore_index =True)
          
    return m_df

#This is the second data extraction function to extract the data from the url of the score card of particular match
def data2(ur,te1,te2,yr):
    #Here same we request the page
    p = requests.get(ur)
    #Extract Data in the xml format
    b = BeautifulSoup(p.content, 'lxml')
    #Find all the tables
    tbody=b.find_all('tbody')

    #these are all the initial variables to be used in the calculation
    run=0
    fours=0
    sixes=0
    dn=""
    t1=0
    t2=0
    tw1=0
    tw2=0
    tb= 0
    gc= 20000
    pc=0
    tsr=0
   
    #here we access each table in the all the tables in the body of the webpage
    for table in tbody :
        #these are the rows we access in each table
        rows = table.find_all('tr')
        #then we access each row in the rows array
        for row in rows[::1]:
            #then we access all the columns in the row
            cols=row.find_all('td')
            #then these are the columns i.e. td element with particular class 
            cols2=row.find_all('td' , class_="font-weight-bold match-venue")

            #then we see that whether we have got columns for the above mentioned class
            if len(cols2) > 0 :
                #Then we perfrom the regex search to try to make the url to get the ground information
                match = re.search(r'href=[\'"]?([^\'" >]+)', str(cols2[0]))
                if match:
                    #then we access the url we got from regex search
                    gr = requests.get(str(match.group(0))[6:])
                    #Then we access the page in xml format
                    bb = BeautifulSoup(gr.content, 'lxml')
                    #the we find the element with id stats
                    stat =  bb.find(id='stats')
                    #then using the strings manipulation based on the html information, the ground capacity is updated
                    if stat != None :                   
                        arr=str(stat).split('<label>')
                        arr=[x.strip() for x in arr if 'Capacity' in x]
                        if len(arr)==1:
                            gc=int(arr[0].rsplit('>')[1].split('<')[0].replace(',','').split(" ")[0])

            #then the columns are extracted to get the other attribute i.e. the time of the match    
            cols=[x.text.strip() for x in cols]

            if cols[0] == "Match days":
                #print(cols[1])
                se=str(cols[1])
                if "daynight" in se:
                    dn="daynight"
                elif "night" in se:
                    dn="night"
                else:
                    dn="day"
                #print(dn)

            #then we calculate the other attribute regarding the home ground
            if cols[0] == "Series":
                 if te1 in str(cols[1]) and str(cols[1]).find(te1) > 0 :
                            t1=1
                 elif te2 in str(cols[1]) and str(cols[1]).find(te2) > 0:
                            t2=1
            
            #then we calculate the toss related fields      
            if cols[0] == "Toss":
                if te1 == str(cols[1]).split(',')[0] :
                   tw1=1
                   if str(cols[1]).split(' ')[-2] == "bat":
                       tb=1
                elif te2 == str(cols[1]).split(',')[0] : 
                   tw2=1
                   if str(cols[1]).split(' ')[-2] == "field":
                       tb=1
            
            #then we move to eaxh batsmen cell to calculate the total fours, sixes and runs
            cols_out=row.find_all('td',{"class": "batsman-cell text-truncate out"})

            if len(cols_out) != 0 :
                pc+=1
                c_o=row.find_all('td')               
                c_o=[x.text.strip() for x in c_o]
                if c_o[2] != '-':
                    run+= int(c_o[2])
                if c_o[5] != '-':
                    fours+=int(c_o[5])
                if c_o[6] != '-':
                    sixes+=int(c_o[6])

                #the mean value to be imputed
                avgsr= 100.0

                #then we move to each batsmen record to get its strike rate in order to calculate the avearge trike rate of top 5-6 players
                #here we are accesing the batsmen which got out
                match = re.search(r'href=[\'"]?([^\'" >]+)', str(cols_out[0]))
                xx=str(match.group(0)).split('-')[-1]
                pp=requests.get("https://stats.espncricinfo.com/ci/engine/player/"+xx+".html?class=3;template=results;type=batting")

                b = BeautifulSoup(pp.content, 'lxml')
                t_body=b.find_all('tbody')

                sr=100.0

                for table in t_body :
                    rows = table.find_all('tr')
                    for row in rows[::1]:
                        cols=row.find_all('td')
                        cols=[x.text.strip() for x in cols]
                        if cols[0] == "year "+ yr:
                            sr=cols[9]
                            try:                           
                                if float(sr) < 15 :
                                        sr=cols[8]
                            except:
                                sr=100.0
                            #print(float(sr))
                try:
                    tsr+=float(sr)
                except:
                    tsr+=100.0

            #here we access the batsmen which remained not out
            #they are also used to adding their figures of fours, sixes and runs for the total figures of the match
            cols_notout=row.find_all('td',{"class": "batsman-cell text-truncate not-out"})

            #Same as above as in case of out batsmen
            if len(cols_notout) != 0 :
                pc+=1
                c_no=row.find_all('td')
                c_no=[x.text.strip() for x in c_no]
                if c_no[2] != '-':
                    run+= int(c_no[2])
                if c_no[5] != '-':
                    fours+=int(c_no[5])
                if c_no[6] != '-':    
                    sixes+=int(c_no[6])

                # here we search the url of each batsman to get its strike rate for an year under consideration to calculate average of the game
                match = re.search(r'href=[\'"]?([^\'" >]+)', str(cols_notout[0]))
                yy=str(match.group(0)).split('-')[-1]
                pp=requests.get("https://stats.espncricinfo.com/ci/engine/player/"+yy+".html?class=3;template=results;type=batting")

                b = BeautifulSoup(pp.content, 'lxml')
                t_body=b.find_all('tbody')

                sr=100.0

                for table in t_body :
                    rows = table.find_all('tr')
                    for row in rows[::1]:
                        cols=row.find_all('td')
                        cols=[x.text.strip() for x in cols]
                        if cols[0] == "year "+ yr:
                            sr=cols[9]
                            try:                           
                                if float(sr) < 15 :
                                    sr=cols[8]
                            except:
                                sr=100.0
                
                try:
                    tsr+=float(sr)
                except:
                    tsr+=100.0
            if pc == 0:
                avgsr= 100.0
            else:
                 avgsr= float(tsr/pc)
    return (run,fours,sixes,dn,t1,t2,tw1,tw2,tb,gc,avgsr)


#This is the main function to start the program
if __name__ == "__main__":
    #Here you can put any year ranging from 2007 to 2019 and the team will vary from 1 to 10
    #note the last element in the range function is last + 1 then it loops to the last
    for j in range(2012,2013):
        for i in range(1,10):            
            x=data(i,j)
            #the Data is collected and then the Data is put into the csv in the current directory loaction
            x.to_csv('T.csv', mode='a', header=False)

#Note that some help was taken from sources like medium.com and stackoverflow
#But as this is the dataset which is original based on the requirements of my project
#there is a lot of thought process for building this script and the web provided some help that how to reach the 
#HTML elements and other stuff using the Beautuful soup library of Python