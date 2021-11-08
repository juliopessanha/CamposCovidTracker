# What is it:
That's a twitter bot that report the evolution of covid in Campos dos Goytacazes using public data. I made this code in 2020 and I've been updating it every time it's needed.

# Why I made it:
In early 2020, when the first covid cases where reported in Campos dos Goytacazes, Brazil, information about it became an essential aspect of it's citizens. The local government started a daily report on their social media and official website. Although that data was public, it wasn't easy to understand the evolution of the desease by a glance. Although the local goverment made a more detailed reports two times a month, it wasn't easy to understand nor appealing for everyone.

I made this twitter bot to make information more palatable and easy to understand by removing the necessity to access a governamental site and find the, usually outdated, data about Campos dos Goytacazes. This robot extract that data daily and posts on a site that those citizens are already online, showing more detailed information in a easy way to understand and digest.

Information is one of the strongest weapons to fight Covid-19. It glues all together.

# Understanding the functions:
The robot has 3 functions currently:

1. dados_campos.py (Data_Campos): Checks if there's new data, extracts it from the web, organizes it, loads it to an excel spreadsheet and posts on Twitter. It runs every 20 minutos.

2. semanal_dados_campos.py (Weekly_Data_Campos): Uses the extracted data to make a week report to show the desease behaviour on a weekly basis. It runs every sunday.

3. vacinometro.py (Vaccinometer): Uses the extracted data to report the percentage of vaccinated Campos dos Goytacazes' adult citizens. It creates an easy to understand graph to show this information. It runs thrice a week.
