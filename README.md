# XC-Flights-Dashboard

A simple but powerful dashboard to analyse and make stats from XC paragliding flights datas.

### Video Demo: 

https://www.youtube.com/watch?v=qOIYOUy1wuw

### Web App URL:

https://xcflightsdashboard.herokuapp.com/

## Description :

#### Introduction :
    
My main goal was to have statistical tools about cross country paragliding flights (XC flights) easily shareable with other pilots. 
To stay in the air a paraglider needs to thermal or soar in order to climb up and glide.
A cross country flight takes the paraglider pilot several hours and many kilometers far from the launch site (take off). It can last less than
1 hour or all the day long depending on the pilot level and the aerology/meteorology of the day. The longest you stay in the air the furthest you can go. 
The fastest you fly the furthest you can go. But there are also sites that seems better launch for a cross country. And it also depends on the seasons, months
and even locations. Mountains' XC are totally different from plains' XC. And many little things and parameters that makes free flight so magic and secrets full. 
So, the goal is to bring tools that kind of analyse XC flights based on 20 years of datas. (The largest the datas the better will be the conclusions) 
I though the simplest, the better it will be therefore I was looking for a dashboard kind of application as a single page layout with a simple user interface and several graphs.

#### Collection of datas :

The first part of the project was to collect some flights datas. When an XC flight is done, pilot use to register their flights on some databases.
There are many sites that collects "declared" XC flights. Such as XC contest (https://www.xcontest.org/world), syride (https://www.syride.com/en/vols) 
or FFVL CFD (https://parapente.ffvl.fr/cfd) for instance.

All three grouped as one would represent a huge amount of datas and a collection of worldwide XC flights. But it wasn't affordable at first. So I limited the datas based on the FFVL CFD.
Improving the database will improve the stats and conclusions made from.

The FFVL CFD is the french cross country competition. An XC is at least a 10km flight and there are different kind of flights susch as triangle or free distance.
You can search flights by entering some parameters and access some datas. But collecting bunch of datas would be really time consuming and impossible. The FFLV doesn't provide an API 
to remote access the datas but only the possibility to download .xls files.

Therefore I have written a program to automate collection and creation of .csv files that are joined to the app as a sample of what it is possible. 
This program was maily a console and selenium project that download an html datatable and with pandas
create a temporary dataframe in order to filter datas and make some changes to the frame, before wrtiting all to .csv file 
which name is the launch site/take off scrapped. ("maupuy.csv", "floirac.csv" etc) 
The code is available right there : /Stecathw/XC-Flights-Scrapper-To-Database

#### The dashboard :

Once the database created, the dashboard was created to explore and hopefully improve visualisation of datas collected. 
It is mainly made to have a quick look and intuitive exploration about performances, kind of flights, pilots stats, evolution, distribution 
and several kind of statistics that would be great to have access for XC pilots. Some conclusions and trends then 
can be made about what seems to be the best sites, best seasons, best months, best pilot...

##### User interface :

In order to make this exploration, in one hand high-level selection and on the other hand really deep and low-level, 
I tried to create as many as possible accessible parameters that can be changed and perform time real calculations 
and modifications on the graphs. A right panel with four tabs got everything needed to play with database.

Tab "Launch":
    - Launch site selection
    - Years selection
    - Month selection
    - Upload a csv file
    
Note that when opening the app for the first time, "locations" will be empty and so will be the graphs. All available locations are listed in the dropdown menu. 
Press "all" radio butttons or "customize" it. 

Tab "Flight":
    - Flight type selection
    - Flight distance selection
    - Flight duration selection
    - Presence of gps trace or not
    
Tab "Pilot":
    - Pilot sex selection
    - Wing category selection
    
Tab "Graphs":
    - Highlight best score on datatable
    - X and Y axis changes for historgram
    - X and Y axis changes for scatter plot
    - Log X and log Y possibility for scatter plot
    
##### Graphs:

Visualisation is then made across two main things, the datatable and the histogram. 
It is completed by a pie chart and scatter plot that will be more relevant for more performances indications. 
All the graphs have options accessible within tabs 'graphs'. Feel free to play with it.

Histogram :
    - show evolution of flights by years and months
    - hover on it to find informations

Pie chart:
    - show repartition on 3 levels (launch, flight type and category of wing). The lightest color entry is the longest flight performance.
    
Scatter plot:
    - show performance of each flights depending on distance, speed or max altitude.


    
#### Technologies and choices:

I wanted to improve my python skills and after some searching I find that most of datas sciences project use Pandas librairy.
For shareability and easy to use, I wanted a one page dashboard kind of application. I've found that dash plotlty was a good framework for my purposes.
(https://plotly.com/dash/) It is based on flask and written uppon react.js.
I've also used some CSS stylesheets.
For deployment, I used GIT to push on Heroku.

#### Limitations and troubles:

This is a web application with limited responsivness. It wont work properly on mobile phone. 

There might be some little quacks as it is the first time I coded something from 0. Feel free to report.


