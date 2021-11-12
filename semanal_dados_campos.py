#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import tweepy
import matplotlib.pyplot as plt
import numpy as np

class analiseCampos:
    
    def __init__(self, dataset):
        self.dataset = dataset
    
    def novos_casos(self):
        
        #CODIGO PARA SEPARAR NOVOS CASOS POR DIA
        #Ele pega a quantidade de casos totais por dia e subtrai pelo dia anterior
        novosCasos = [0]
        for x in range(1,self.dataset.shape[0]):
            novosCasos.append(self.dataset["Casos Confirmados"].iloc[x] - self.dataset["Casos Confirmados"].iloc[x-1])
    
        #print(novosCasos)
    
        self.dataset.insert(2, 'Novos Casos', novosCasos)
  
      
    def novos_obitos(self):
    
        #CODIGO PARA SEPARAR NOVOS OBITOS POR DIA
        #Ele pega a quantidade de obitos confirmados totais por dia e subtrai pelo dia anterior
        novosObitos = [0]
        for x in range(1,self.dataset.shape[0]):
            novosObitos.append(self.dataset["Obitos Confirmados"][x] - self.dataset["Obitos Confirmados"][x - 1])
    
        #print(novosObitos)

        self.dataset.insert(5, 'Novos Obitos Confirmados', novosObitos)
        
        
        
    def obitos_por_semana(self):
        print("Óbitos")
        #Script para separar os casos por semana
        #onde guarda os valores da semana
        somaSemana = [0]
        #semana analisada
        semana = 0
        #row no dataframe
        y = 0
        #valor do dia anterior

        last = self.dataset.index[-1]
        
        print(last)
        
        self.dataset['Data'] = pandas.to_datetime(self.dataset["Data"], format='%d/%m/%Y')
        
        #Como segunda = 0, eu transformo domingo em zero ao passar por essa lista
        fixWeek = [1, 2, 3, 4, 5, 6, 0]

        xBefore = fixWeek[self.dataset.Data.dt.dayofweek.iloc[0]]
        for x in self.dataset.Data.dt.dayofweek:

            #print("somaSemana: ", somaSemana)
            #print("semana: ", semana)
            #print("xBefore: " + str(xBefore))

            #CHECA SE EH UM PROXIMO DIA OU O PRIMEIRO DA SEMANA JA QUE 0 EH MENOR QUE 6
            if ((fixWeek[x] > xBefore) or fixWeek[x] == 0):
                #VOU SOMANDO O VALOR PARA O ESPACO DA LISTA
                somaSemana[semana] += self.dataset['Novos Obitos Confirmados'][y]
                print(str(x) + " | " + str(self.dataset["Data"].iloc[y]) + " | Valor fixado " + str(fixWeek[x]))
                print("--")


                #CASO MUDE DE SEMANA EU PASSO PRA PROXIMA PARTE DA LISTA
                if (fixWeek[x] == 6 and self.dataset.index[y] != last):
                    semana += 1
                    somaSemana.append(0)
                    print(" ---- SKIP -----")            


            y += 1
            xBefore = fixWeek[x]

        #cria novo dataframe por semana
        return(pandas.DataFrame(somaSemana, columns = ['Novos Óbitos']))
    
    
    def por_semana(self):
        print("Casos")
        #Script para separar os casos por semana
        #onde guarda os valores da semana
        somaSemana = [0]
        #semana analisada
        semana = 0
        #row no dataframe
        y = 0
        #valor do dia anterior

        last = self.dataset.index[-1]
        
        print(last)
        
        self.dataset['Data'] = pandas.to_datetime(self.dataset["Data"], format='%d/%m/%Y')
        
        #Como segunda = 0, eu transformo domingo em zero ao passar por essa lista
        fixWeek = [1, 2, 3, 4, 5, 6, 0]

        xBefore = fixWeek[self.dataset.Data.dt.dayofweek.iloc[0]]
        for x in self.dataset.Data.dt.dayofweek:

            #print("somaSemana: ", somaSemana)
            #print("semana: ", semana)
            #print("xBefore: " + str(xBefore))

            #CHECA SE EH UM PROXIMO DIA OU O PRIMEIRO DA SEMANA JA QUE 0 EH MENOR QUE 6
            if ((fixWeek[x] > xBefore) or fixWeek[x] == 0):
                #VOU SOMANDO O VALOR PARA O ESPACO DA LISTA
                somaSemana[semana] += self.dataset['Novos Casos'][y]
                print(str(x) + " | " + str(self.dataset["Data"].iloc[y]) + " | Valor fixado " + str(fixWeek[x]))
                print("--")


                #CASO MUDE DE SEMANA EU PASSO PRA PROXIMA PARTE DA LISTA
                if (fixWeek[x] == 6 and self.dataset.index[y] != last):
                    semana += 1
                    somaSemana.append(0)
                    print(" ---- SKIP -----")            


            y += 1
            xBefore = fixWeek[x]

        #cria novo dataframe por semana
        return(pandas.DataFrame(somaSemana, columns = ['Novos Casos']))
    
    def compara_dias(self, data):

        #Transforma a str em objeto datetime e comparar com o do excel
        date_object = datetime.strptime(data, '%d/%m/%Y').date()
        try:
            date_object2 = datetime.strptime(self.dataset.Data.iloc[-1], '%d/%m/%Y').date()
        except:
            date_object2 = self.dataset.Data.iloc[-1]
            
        #a hora eu ainda nao sei de onde tira calma la
        #hour_object = datetime.strptime(hora, '%H:%M')
        #hour_object2 = datetime.strptime('18:44', '%H:%M')

        if(date_object > (date_object2)):
            return(True)

        #elif(date_object == date_object2):
        #    if(hour_object > hour_object2):
        #        return(True)
        #    else: return(False)
        else: return(False)

    def salvar_excel(self, results):   
        #Pega os obitos separado por ser uma lista com CONFIRMADOS e INVESTIGANDO
        obitosLidos = obitos(results)

        newRow = [[dia_hora(results)[0], confirmados_total(results)[0], obitosLidos[0] + obitosLidos[1], obitosLidos[0], obitosLidos[1], sindrome_gripal(results)[0], sindrome_respiratoria(results)[0]]]

        df = pandas.DataFrame(newRow, columns = ['Data', 'Casos Confirmados', 'Obito', 'Obitos Confirmados', 'Investigando', 'Sindrome Gripal', 'Sindrome Respiratoria Aguda Grave']) 

        #self.dataset['Data'] = pandas.to_datetime(self.dataset["Data"])

        #self.dataset['Data'] = self.dataset.Data.dt.strftime('%d/%m/%Y')
        
 
        #df['Data'] = pandas.to_datetime(df["Data"])
        
        #df['Data'] = df.Data.dt.strftime('%d/%m/%Y')

        self.dataset = self.dataset.append(df)
        
        
        self.dataset['Data'] = pandas.to_datetime(self.dataset["Data"])

        self.dataset['Data'] = self.dataset.Data.dt.strftime('%d/%m/%Y')
        


        self.dataset.to_excel('/home/pi/Desktop/Casos_Campos.xlsx', index = False, header=True)
        
        
    def twitter_auth():
        # Authenticate to Twitter
        auth = tweepy.OAuthHandler("Insert here your credentials", "Insert here your credentials")
        auth.set_access_token("Insert here your credentials", "Insert here your credentials")

        # Create API object
        api = tweepy.API(auth)

    def graph_confirmados_obitos(self):
        plt.close()
        ax = plt.gca()

        self.dataset.plot(x ='Data', y='Obitos Confirmados', color = 'red', ax=ax)
        self.dataset.plot(x ='Data', y='Casos Confirmados', ax=ax, grid = True, figsize=(8, 6), title="Campos dos Goytacazes")

        plt.ylabel("Pessoas")
        plt.xlabel("Dias")
        plt.xticks(rotation=45)
        plt.savefig("/home/pi/Desktop/confirmados_e_obitos.png")
        plt.show
        #plt.close()

    def graph_confirmados_diarios(self):
        plt.close()
        ax2 = plt.gca()

        self.dataset.plot(x = 'Data', y = "Novos Casos", ax=ax2, grid=True, figsize=(8, 6))

        plt.ylabel("Pessoas")
        plt.xlabel("Dias")
        plt.xticks(rotation=18)
        plt.savefig("./confirmados_diarios.png")
        #plt.show()
        plt.close()

        
#-------------------------------------------------------------------------------
        

    
    
def urlFinder():

    URL = 'https://cidac.campos.rj.gov.br/coronavirus/'
    page = requests.get(URL)

    soup = BeautifulSoup(page.content, 'html.parser')

    #PROCURA ONDE O ID = BOLETIM
    return(soup.find(id='boletim'))


#RETORNA COMO STR DATA E HORA NUMA LISTA
def dia_hora(results):
    
    #PROCURA ONDE TEM class = card card-boletim card-obitos
    diaHoras = results.find_all(class_='boletim-title')

    #Separa as informacoes para leitura e retorna em uma string
    for diaHora in diaHoras:
        dia_e_hora = (diaHora.find("div", class_ = "container"))
        if None in (dia_e_hora):
            continue
            
    #pega os valores da string e retorna em uma lista

    data_hora_return = []
    
    data_hora_return.append(dia_e_hora.text.strip()[13:23])
    data_hora_return.append(dia_e_hora.text.strip()[26:].replace("h", ":"))

    
    return(data_hora_return)  

def plot_semanal_obitos(cmpsSemanal):
   
    plt.close()
    ax = plt.gca()

    cmpsSemanal.plot.bar(y = "Novos Óbitos", ax=ax, figsize=(10, 6), color = '#FF7B7B', width=0.85)

    plt.ylabel("Novos Obitos", fontsize = 15)
    plt.xlabel("Semanas", fontsize = 15)
    
    #size of the data
    tick_size = cmpsSemanal.shape[0]
    #Here I divide by 3 to get the offset
    tick_start = tick_size%3
    
    if tick_start - 1 < 0:
        tick_start = 3
    
    #Here changes the ticks to show skipping 3 columns by 3 columns 
    plt.xticks(np.arange(tick_start-1,tick_size,3), np.arange(tick_start,tick_size+1,3), rotation=0, fontsize = 13)
    
    plt.yticks(fontsize = 14)
    plt.title("Campos dos Goytacazes")
    ax.set_axisbelow(True)
    #cor do grid horizontal
    ax.yaxis.grid()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    plt.savefig("/home/pi/Desktop/obitos_acumulo_semanal.png", bbox_inches = 'tight')
    #plt.show()



def plot_semanal(cmpsSemanal):
   
    plt.close()
    ax = plt.gca()

    cmpsSemanal.plot.bar(y = "Novos Casos", ax=ax, figsize=(10, 6), color = '#3AA6E2', width=0.85)

    plt.ylabel("Novos Casos", fontsize = 15)
    plt.xlabel("Semanas", fontsize = 15)

    #size of the data
    tick_size = cmpsSemanal.shape[0]
    #Here I divide by 3 to get the offset
    tick_start = tick_size%3

    if tick_start - 1 < 0:
        tick_start = 3
        
    #Here changes the ticks to show skipping 3 columns by 3 columns 
    plt.xticks(np.arange(tick_start-1,tick_size,3), np.arange(tick_start,tick_size+1,3), rotation=0, fontsize = 13)
    plt.yticks(fontsize = 14)
    plt.title("Campos dos Goytacazes")
    ax.set_axisbelow(True)
    #cor do grid horizontal
    ax.yaxis.grid()
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['left'].set_visible(False)
    #plt.show()
    plt.savefig("/home/pi/Desktop/acumulo_semanal.png", bbox_inches = 'tight')
    
#RODA ROTINA
def __init__():


    #Coloca o dataframe num objeto para ser trabalhado
    cmps = analiseCampos(pandas.read_excel('/home/pi/Desktop/Casos_Campos.xlsx'))
    
    print("analisei")
    
    cmps.novos_casos()
    cmpsSemanal = cmps.por_semana()
    cmps.novos_obitos()
    obitosSemanal = cmps.obitos_por_semana()
    
    
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("Insert here your credentials", "Insert here your credentials")
    auth.set_access_token("Insert here your credentials", "Insert here your credentials")

    # Create API object
    api = tweepy.API(auth)
    
    plot_semanal(cmpsSemanal)
    plot_semanal_obitos(obitosSemanal)
    
    img_path = [['t'],['t']]
    
    img_path[0] = '/home/pi/Desktop/acumulo_semanal.png'
    img_path[1] = api.media_upload('./obitos_acumulo_semanal.png')
    
    #index da Pirmeira data que sera mostrada
    indexComeco = (cmps.dataset.index[cmps.dataset.Data.dt.dayofweek == 6][-1])

    #index da ultima data que sera mostrada
    indexFinal = (cmps.dataset.index[-1])
    
    cmps.dataset['Data'] = cmps.dataset.Data.dt.strftime('%d/%m/%Y')
    
    #Primeiro dia a ser mostrado
    diaComeco = (cmps.dataset.Data.iloc[indexComeco])
    
    #ultimo dia a ser mostrado
    diaFinal = (cmps.dataset.Data.iloc[indexFinal])
    
    #acumulo de novos casos
    acumulado = (cmpsSemanal["Novos Casos"].iloc[-1])
    
    obitosAcumulados = (obitosSemanal["Novos Óbitos"].iloc[-1])
    
    msg = [['t'],['t']]
    
    msg[0] = "Foram %s novos casos e %s óbitos confirmados na última semana\n\nDo dia %s ao dia %s \n1/2" % (acumulado, obitosAcumulados, diaComeco, diaFinal)

    msg[1] = "Gráfico de óbitos por semana: \n2/2"

    print(msg)
    
    print(cmpsSemanal)
    
    tweet = api.update_status_with_media(msg[0], img_path[0])
    
    tweetAntes = tweet.id_str
    
    for i in range(1,2):

        tweet = api.update_status(msg[i], in_reply_to_status_id = tweetAntes, media_ids = [img_path[i].media_id])
        tweetAntes = tweet.id_str

        
__init__()
