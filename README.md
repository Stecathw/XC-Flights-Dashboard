# XC-Flights-Dashboard

A simple but powerful dashboard to analyse and make stats from XC paragliding flights datas.
Deployed here : https://xcflightsdashboard.herokuapp.com/

The first part of the project was to collect, analyse, filter and store datas. Therefore I have written a program to automate collection and creation of .csv files that are joined to the app as a sample. This program was maily a selenium project that download an xls file (old excel format) and with pandas create a temporary dataframe in order to filter datas and make some changes to the frame, before wrtiting all to .csv file which name is the launch site/take off scrapped. ("maupuy.csv", "floirac.csv" etc) 
The code is available right there : https://github.com/Stecathw/XC-Flights-Scrapper-To-Database


Once the database created, the dashboard was created to explore and hopefully improve visualisation of datas collected. It is mainly made to have a quick look about performances, kind of flights, pilots stats, evolution, distribution and several kind of statistics that would be great to have access for XC pilots. Some conclusions and trends then can be made about what seems to be the best sites, best seasons, best months, best pilot...

In order to make this exploration, in one hand high-level and on the other hand really deep and low-level, I tried to create as many as possible accessible parameters that can be changed and perform time real calculations and modifications on the graphs. A right panel with four tabs got everything needed to play with database.

Visualisation is then made across two main things, the datatable and the histogram. It is completed by a pie chart and scatter plot that will be more relevant for more performances indications. All the graphs have options accessible within tabs 'graphs'. Feel free to play with it.

All the application is coded with Python using Dash, a framework based on flask and react.js and deployed on Heroku via Git.

This is a web application with limited responsivness. It wont work properly on mobile phone. 
There might be some little quacks as it is the first time I coded something from 0.



