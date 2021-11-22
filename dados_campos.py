#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pandas
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import tweepy
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import random
import re
import os

folder_path = os.path.abspath("./")

class Covid_Data():
    
    def __init__(self):
        self.soup = ''
    
    def get_url(self):
        
        page = requests.get('https://www.campos.rj.gov.br/search.php?PGpagina=1&PGporPagina=10&s=boletim')
        soup = BeautifulSoup(page.content, 'lxml')
        html_content = str(soup.select('.destaques-lista li:nth-child(1)'))
        link = re.findall( r'href="(.+)">', html_content)[0]
        
        return('https://www.campos.rj.gov.br/'+link)
    
    def urlFinder(self, url):
        page = requests.get(url)

        self.soup = BeautifulSoup(page.content, 'html.parser')
        self.results = self.soup.find(class_='col-md-12 imateria')
        self.casos = (self.results.get_text())
        self.casos = self.casos.replace(" ","")
        self.casos = self.casos.replace("  ","")
        self.casos = self.casos.replace("   ","")
        self.casos = self.casos.replace("    ","")
        #self.casos = self.casos.replace(",",".")
        self.casos = self.casos.replace(".","")
        self.casos = self.casos.lower()
        self.casos = self.casos.replace("ú","u")
        self.casos = self.casos.replace("ó","o")
        self.casos = self.casos.replace("é","e")
        self.casos = self.casos.replace("ã","a")
        self.casos = self.casos.replace('í', 'i')
        self.casos = self.casos.replace("%","")
        self.casos = self.casos.replace("-","–")
        self.casos = self.casos.replace("confirmados:","confirmation")
        self.casos = self.casos.replace(":","")
        self.casos = self.casos.replace("obitosconfirmation","obitos")
        self.casos = re.sub(r"\s+", "", self.casos, flags=re.UNICODE)
        
        return(self.soup)

    
    def last_page(self):
        if self.soup.find(class_='col-md-12 imateria') == '':
            return(True)

    def date_finder(self):

        results_date = self.soup.find(class_='col-md-12')

        date_check = (results_date.get_text())
        print(date_check)
        match = re.search(r'(\d+/\d+/\d+)',date_check)

        try: #a prefeitura decidiu mandar um 1°/11/2021 entao agora existe essa excecao
            date = match.group(1)
            return(date)
        except: #motivo? nao sei
            match = re.search(r'(boletimcoronavirus–(\d+/\d+/\d+))', self.casos)[0]
            match = match.replace("boletimcoronavirus–", "")            
            return(match)
            
    def numero_casos(self):

        match = re.search(r'(confirmation(\d+))', self.casos)[0]
        match = match.replace("confirmation", "")
        
        return(match)

    def sindrome_gripal(self):

        match = re.search(r'(gripal\(sg\)(\d+))', self.casos)[0]
        match = match.replace("gripal(sg)", "")
        
        return(match)
    
    def srag(self):

        match = re.search(r'(grave\(srag\)(\d+))', self.casos)[0]
        match = match.replace("grave(srag)", "")
        
        return(match)
    
    def obitos(self):
        
        match = re.search(r'(obitos(\d+))', self.casos)[0]
        match = match.replace("obitos", "")
        
        return(match)
    
    def vacina(self):
        
        primeira_dose = re.search(r'(primeiradose–(\d+))', self.casos)[0]
        primeira_dose = primeira_dose.replace("primeiradose–", "")
        
        segunda_dose = re.search(r'(segundadose–(\d+))', self.casos)[0]
        segunda_dose = segunda_dose.replace("segundadose–", "")       
        
        dose_unica = re.search(r'(doseunica–(\d+))', self.casos)[0]
        dose_unica = dose_unica.replace("doseunica–", "")       
        
        
        return([primeira_dose, segunda_dose, dose_unica])
    
    def ocupacao_leitos(self):
        
        try:
            uti = re.search(r'(dauti–(\d+,\d+))', self.casos)[0]
            uti = uti.replace("dauti–", "")
            uti = uti.replace(",",".")
            
        except:
            uti = re.search(r'(dauti–(\d+))', self.casos)[0]
            uti = uti.replace("dauti–", "")            
        
        try:
            clinica = re.search(r'(medica–(\d+,\d+))', self.casos)[0]
            clinica = clinica.replace("medica–", "")
            clinica = clinica.replace(",",".")
        
        except:
            clinica = re.search(r'(medica–(\d+))', self.casos)[0]
            clinica = clinica.replace("medica–", "")
            clinica = clinica + '.00'
        
        return([uti, clinica])
    
    def fila_espera(self):
        
        try:
            match = re.search(r'(espera(\d+))', self.casos)[0]
            match = match.replace("espera", "")
            return(match.lstrip("0"))
        except TypeError:
            return("0")
    

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
    
    def por_semana(self):

        #Script para separar os casos por semana
        #onde guarda os valores da semana
        somaSemana = [0]
        #semana analisada
        semana = 0
        #row no dataframe
        y = 0
        #valor do dia anterior

        df = self.dataset
        df['Data'] = pandas.to_datetime(self.dataset["Data"], format='%d/%m/%Y')

        #Como segunda = 0, eu transformo domingo em zero ao passar por essa lista
        fixWeek = [1, 2, 3, 4, 5, 6, 0]

        xBefore = fixWeek[df.Data.dt.dayofweek.iloc[0]]
        for x in df.Data.dt.dayofweek:

            #print("xBefore: " + str(xBefore))

            #CHECA SE EH UM PROXIMO DIA OU O PRIMEIRO DA SEMANA JA QUE 0 EH MENOR QUE 6
            if ((fixWeek[x] > xBefore) or fixWeek[x] == 0):
                #VOU SOMANDO O VALOR PARA O ESPACO DA LISTA
                somaSemana[semana] += df['Novos Casos'][y]
                #print(str(x) + " | " + str(self.dataset["Data"].iloc[y]) + " | Valor fixado " + str(fixWeek[x]))
                #print("--")


                #CASO MUDE DE SEMANA EU PASSO PRA PROXIMA PARTE DA LISTA
                if (fixWeek[x] == 6):
                    semana += 1
                    somaSemana.append(0)
                    #print(" ---- SKIP -----")            


            y += 1
            xBefore = fixWeek[x]
    
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

    def salvar_excel(self, get):   

        newRow = [[get.date_finder(), get.numero_casos(), get.obitos(), get.obitos(), '0', get.sindrome_gripal(), get.srag(), get.vacina()[0], get.ocupacao_leitos()[0], get.ocupacao_leitos()[1], get.fila_espera(), get.vacina()[1], get.vacina()[2]]]

        df = pandas.DataFrame(newRow, columns = ['Data', 'Casos Confirmados', 'Obito', 'Obitos Confirmados', 'Investigando', 'Sindrome Gripal', 'Sindrome Respiratoria Aguda Grave', 'Vacinados', 'UTI', 'Clinica', 'Fila de Espera', 'Segunda Dose', 'Dose Única']) 

        #print(df)

        self.dataset = self.dataset.append(df)

        self.dataset.to_excel(folder_path + '/Casos_Campos.xlsx', index = False, header=True)
        
        
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

        plt.ylabel("Casos")
        plt.xlabel("Dias")
        plt.xticks(rotation=18)
        plt.savefig(folder_path + "/confirmados_e_obitos.png", bbox_inches = 'tight')
        plt.show
        #plt.close()

    def graph_confirmados_diarios(self):
        
            plt.close('all')
            
            df = self.dataset.copy()
            df['Data'] = pandas.to_datetime(df["Data"], format='%d/%m/%Y')

            df["ultimo_dia"] = df["Data"].dt.dayofweek == df["Data"].max().dayofweek
            df["Media Móvel"] = df["Novos Casos"].rolling(7).mean()

            fig, ax = plt.subplots(1, 1, figsize=(16, 9))

            df1 = df[df["ultimo_dia"]]
            df2 = df[~df["ultimo_dia"]]
            ax.set_axisbelow(True)
            ax.plot(df["Data"], df["Media Móvel"], color="darkslateblue", linewidth=3)
            ax.bar(df1["Data"], df1["Novos Casos"], color="#a9dbde", width=1)
            ax.bar(df2["Data"], df2["Novos Casos"], color="#dff2f9", width=1)

            # Defining x ticks
            ticks, ticklabels, min_date, max_date = date_ticks_spitter(df["Data"])

            ax.set_xticks(ticks)
            ax.set_xticklabels(ticklabels)
            ax.set_title("Campos dos Goytacazes", fontsize=20)
            ax.set_xlabel("Datas", fontsize=20)
            ax.set_ylabel("Novos Casos", fontsize=20)
            plt.xticks(fontsize=11)
            plt.yticks(fontsize=20)
            ax.yaxis.grid(color='lightgray')

            ax.set_xlim(min_date - 0.6, max_date + 0.6)
            
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)

            plt.legend(['Média Móvel', 'Novos Casos'], fontsize = 14)
            plt.show()

            plt.savefig(folder_path + "/confirmados_diarios.png", bbox_inches = 'tight')
            plt.close()
            
    def graph_obitos_diarios(self):
        
            plt.close('all')
            
            df = self.dataset.copy()
            df['Data'] = pandas.to_datetime(df["Data"], format='%d/%m/%Y')

            df["ultimo_dia"] = df["Data"].dt.dayofweek == df["Data"].max().dayofweek
            df["Media Móvel"] = df["Novos Obitos Confirmados"].rolling(7).mean()

            fig, ax = plt.subplots(1, 1, figsize=(16, 18))

            df1 = df[~df["ultimo_dia"]]
            df2 = df[df["ultimo_dia"]]
            ax.set_axisbelow(True)
            ax.plot(df["Data"], df["Media Móvel"], color="#4d0000", linewidth=3)
            ax.bar(df1["Data"], df1["Novos Obitos Confirmados"], color="#ffe6e6", width=1)
            ax.bar(df2["Data"], df2["Novos Obitos Confirmados"], color="#ffb3b3", width=1)

            # Defining x ticks
            ticks, ticklabels, min_date, max_date = date_ticks_spitter(df["Data"])

            plt.title('Óbitos em Campos dos Goytacazes', fontdict = {'fontsize' : 26})
            ax.set_xticks(ticks)
            ax.set_xticklabels(ticklabels)
            #ax.set_title("Campos dos Goytacazes", fontsize=20)
            ax.set_xlabel("Datas", fontsize=25)
            ax.set_ylabel("Novos Óbitos", fontsize=25)

            ax.yaxis.grid(color='lightgray')

            ax.set_xlim(min_date - 0.6, max_date + 0.6)
            
            ax.spines['right'].set_visible(False)
            ax.spines['top'].set_visible(False)
            ax.spines['left'].set_visible(False)

            if self.dataset['Novos Obitos Confirmados'].max() % 2 == 0:
            
                yint = range(0, (self.dataset['Novos Obitos Confirmados'].max() + 1), 2)

            elif (self.dataset['Novos Obitos Confirmados'].max() + 1) % 2 == 0:

                yint = range(0, (self.dataset['Novos Obitos Confirmados'].max() + 2), 2)
            
            plt.yticks(yint,fontsize=24)
            plt.xticks(fontsize=11)
            
            
            plt.legend(['Média Móvel', 'Novos Óbitos'], fontsize = 16)
            plt.show()

            plt.savefig(folder_path + "/confirmados_e_obitos.png", bbox_inches = 'tight')
            plt.close()
        
        
    #Retorna na ordem SRAG e Sindrome Gripal
    #Caso a prefeitura tenha postado invertido, desinverte
    def value_checker(self, results):
        #flag para checar. Se for 1,1 está tudo certo, se for 0,0 está trocado. Qualquer outra combinacao fodeu
        flag = [0,0]

        #NO COEMCO CHECA SE SRAG E SINDROME GRIPAL ESTAO INVERTIDOS
        SRAG = sindrome_respiratoria(results)[0]
        gripal = sindrome_gripal(results)[0]

        #Para checar se o SRAG novo eh mais proximo do antigo
        if (abs(SRAG - int(self.dataset["Sindrome Respiratoria Aguda Grave"].iloc[-1]))) <= abs(SRAG - int(self.dataset["Sindrome Gripal"].iloc[-1])):
            flag[0] = 1

        if (abs(gripal - int(self.dataset["Sindrome Gripal"].iloc[-1]))) <= abs(gripal - int(self.dataset["Sindrome Respiratoria Aguda Grave"].iloc[-1])):
            flag[1] = 1

        #print(flag)
        if (flag == [1,1]):
            return([SRAG, gripal, 1, 1])
        elif (flag == [0,0]):
            return([gripal, SRAG, 0, 0])
        else:
            return([SRAG, gripal, 2, 2])
        
#-------------------------------------------------------------------------------
        

def date_ticks_spitter(date_vector):
    month_dict = {
        "Jan": "Jan",
        "Feb": "Fev",
        "Mar": "Mar",
        "Apr": "Abr",
        "May": "Mai",
        "Jun": "Jun",
        "Jul": "Jul",
        "Aug": "Ago",
        "Sep": "Set",
        "Oct": "Out",
        "Nov": "Nov",
        "Dec": "Dez"
    }
    
    num_dates = mdates.date2num(date_vector.sort_values()).tolist()
    min_date = num_dates[0]
    max_date = num_dates[-1]
    num_dates.reverse()
    num_dates_of_interest = list(reversed(num_dates[0::14]))

    date_ticks = pandas.to_datetime(mdates.num2date(num_dates_of_interest))
    date_ticks = ["{}\n{}".format(tick.day, month_dict[tick.strftime("%b")]) for tick in date_ticks]
    return num_dates_of_interest, date_ticks, min_date, max_date
    
    
def analiseLoop(get):
    print("analisei")
    #camposDataframe = pandas.read_excel(folder_path + '/Casos_Campos.xlsx')

    
    tipo = random.randint(1, 100)

    cmps = analiseCampos(pandas.read_excel(folder_path + '/Casos_Campos.xlsx'))
    
    cmps.novos_casos()
    cmps.novos_obitos()
    cmps.graph_confirmados_diarios()
    
    #Aqui define se sera postado no segundo tweet um grafico de obitos ou acumulo total
    if tipo > 90: 

        cmps.graph_confirmados_obitos()
    else:

        cmps.graph_obitos_diarios()
        
    
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("Insert here your credentials", "Insert here your credentials")
    auth.set_access_token("Insert here your credentials", "Insert here your credentials")

    # Create API object
    api = tweepy.API(auth)
    
    #print(cmps.dataset)
    
    #cmps.graph_confirmados_obitos()
    #cmps.graph_confirmados_diarios()
    
    #cmps.twitter_auth
    
    #a prefeitura troca SRAG e gripal, então aqui checa e sempre retorna SRAg e gripal nessa ordem
    #SRAG_gripal = cmps.value_checker(results)
    
    img_path = [['t'],['t']]
    

    img_path[0] = folder_path + '/confirmados_diarios.png'
    img_path[1] = api.media_upload(folder_path + "/confirmados_e_obitos.png")
    
    msg = [['t'],['t']]
    
    #Se tiver algum obito em investigacao, ele especifica
    if int(cmps.dataset.Obito.iloc[-1]) > int(cmps.dataset['Obitos Confirmados'].iloc[-1]):
        msg[0] = "DIA " + str(data_hoje) + " \n\nCasos confirmados: " + str(cmps.dataset['Casos Confirmados'].iloc[-1]) + " (+" + str(cmps.dataset["Novos Casos"].iloc[-1]) + ") " + "  \n\nÓbitos: " + str(cmps.dataset.Obito.iloc[-1]) + " (" + str(cmps.dataset.Obito.iloc[-1] - cmps.dataset['Obitos Confirmados'].iloc[-1]) + " em investigação)" + "\n\nÓbitos Confirmados: " + str(cmps.dataset['Obitos Confirmados'].iloc[-1]) + " (" + str(cmps.dataset["Novos Obitos Confirmados"].iloc[-1]) + " novos)" + "\n\nSíndrome Respiratória Aguda Grave: " + str(int(cmps.dataset['Sindrome Respiratoria Aguda Grave'].iloc[-1])) + "\n\nSíndrome Gripal: " + str(int(cmps.dataset['Sindrome Gripal'].iloc[-1])) + "\n\nVacinados: " + str(int(cmps.dataset['Vacinados'].iloc[-1])) + " (" + str(int(cmps.dataset['Vacinados'].iloc[-1] - cmps.dataset['Vacinados'].iloc[-2])) + " novos)" + "\n\nGráfico com número de casos por dia:\n(1/2)"

        #Caso nao haja obito em investigacao, ele apenas posta os confirmados
    else:
        msg[0] = "DIA " + str(cmps.dataset['Data'].iloc[-1]) + " \n\nCasos confirmados: " + str(cmps.dataset['Casos Confirmados'].iloc[-1]) + " (+" + str(cmps.dataset["Novos Casos"].iloc[-1]) + ") " + "\n\nÓbitos confirmados: " + str(cmps.dataset.Obito.iloc[-1]) + " (+" + str(cmps.dataset["Novos Obitos Confirmados"].iloc[-1]) + ")" + "\n\nSíndrome Respiratória Aguda Grave: " + str(int(cmps.dataset['Sindrome Respiratoria Aguda Grave'].iloc[-1])) + " (+" + str(int(cmps.dataset['Sindrome Respiratoria Aguda Grave'].iloc[-1] - cmps.dataset['Sindrome Respiratoria Aguda Grave'].iloc[-2]))  + ")" + "\n\nSíndrome Gripal: " + str(int(cmps.dataset['Sindrome Gripal'].iloc[-1])) + " (+" + str(int(cmps.dataset['Sindrome Gripal'].iloc[-1] - cmps.dataset['Sindrome Gripal'].iloc[-2])) + ")" + "\n\nVacinados: " + str(int(cmps.dataset['Vacinados'].iloc[-1])) + " (+" + str(int(cmps.dataset['Vacinados'].iloc[-1] - cmps.dataset['Vacinados'].iloc[-2])) + ")" + "\n\nGráfico com número de casos por dia:\n(1/2)"        

    variacao_ocupacao_leitos = (cmps.dataset['UTI'].iloc[-1] - cmps.dataset['UTI'].iloc[-2])

    if tipo > 90:
        if variacao_ocupacao_leitos >= 0.0:
            msg[1] = "Ocupação de leitos de UTI: " + str(cmps.dataset['UTI'].iloc[-1]) + "%" + " (+" + str(round(variacao_ocupacao_leitos, 2)) + "%)" + "\n\nLetalidade: " + str(round(((cmps.dataset['Obitos Confirmados'].iloc[-1]/cmps.dataset["Casos Confirmados"].iloc[-1])*100), 2)) + "%" "\n\nEsse dia foi responsável por " + str(round(((cmps.dataset["Novos Casos"].iloc[-1]/cmps.dataset["Casos Confirmados"].iloc[-1])*100), 2)) + "% do total de casos\n\nCurva de Casos Confirmados e Óbitos:\n(2/2)"

        elif variacao_ocupacao_leitos < 0.0:
            msg[1] = "Ocupação de leitos de UTI: " + str(cmps.dataset['UTI'].iloc[-1]) + "%" + " (" + str(round(variacao_ocupacao_leitos, 2)) + "%)" + "\n\nLetalidade: " + str(round(((cmps.dataset['Obitos Confirmados'].iloc[-1]/cmps.dataset["Casos Confirmados"].iloc[-1])*100), 2)) + "%" "\n\nEsse dia foi responsável por " + str(round(((cmps.dataset["Novos Casos"].iloc[-1]/cmps.dataset["Casos Confirmados"].iloc[-1])*100), 2)) + "% do total de casos\n\nCurva de Casos Confirmados e Óbitos:\n(2/2)"

    else:
        if variacao_ocupacao_leitos >= 0.0:
            msg[1] = "Ocupação de leitos de UTI: " + str(cmps.dataset['UTI'].iloc[-1]) + "%" + " (+" + str(round(variacao_ocupacao_leitos, 2)) + "%)" + "\n\nOcupação de leitos clínicos: " + str(cmps.dataset['Clinica'].iloc[-1]) + "%" + "\n\nFila de espera para leitos: " + str(int(cmps.dataset['Fila de Espera'].iloc[-1])) + "\n\nLetalidade: " + str(round(((cmps.dataset['Obitos Confirmados'].iloc[-1]/cmps.dataset["Casos Confirmados"].iloc[-1])*100), 2)) + "%" "\n\nEsse dia foi responsável por " + str(round(((cmps.dataset["Novos Casos"].iloc[-1]/cmps.dataset["Casos Confirmados"].iloc[-1])*100), 2)) + "% do total de casos\n\nGráfico de Óbitos Confirmados por Dia:\n(2/2)"

        elif variacao_ocupacao_leitos < 0.0:
            msg[1] = "Ocupação de leitos de UTI: " + str(cmps.dataset['UTI'].iloc[-1]) + "%" + " (" + str(round(variacao_ocupacao_leitos, 2)) + "%)" + "\n\nOcupação de leitos clínicos: " + str(cmps.dataset['Clinica'].iloc[-1]) + "%" + "\n\nFila de espera para leitos: " + str(int(cmps.dataset['Fila de Espera'].iloc[-1])) + "\n\nLetalidade: " + str(round(((cmps.dataset['Obitos Confirmados'].iloc[-1]/cmps.dataset["Casos Confirmados"].iloc[-1])*100), 2)) + "%" "\n\nEsse dia foi responsável por " + str(round(((cmps.dataset["Novos Casos"].iloc[-1]/cmps.dataset["Casos Confirmados"].iloc[-1])*100), 2)) + "% do total de casos\n\nGráfico de Óbitos Confirmados por Dia:\n(2/2)"
    
    tweet = api.update_status_with_media(msg[0], img_path[0])

    tweetAntes = tweet.id_str

    for i in range(1,2):

        tweet = api.update_status(msg[i], in_reply_to_status_id = tweetAntes, media_ids = [img_path[i].media_id])
        tweetAntes = tweet.id_str

        
def __init__():
    print('initei')
    #Le a planilha do Excel
    #camposDataframe = pandas.read_excel(folder_path + '/Casos_Campos.xlsx')

    #Lê o site da prefeitura
    get = Covid_Data()

    #Pega a url do boletim mais novo
    url = get.get_url()
    #Pega p boeltim mais novo com base na url
    get.urlFinder(url)
    
    #Checa a data e a hora da ultima atualização lá
    dataHora = get.date_finder()
    print(dataHora)
    #Coloca o dataframe num objeto para ser trabalhado
    cmps = analiseCampos(pandas.read_excel(folder_path + '/Casos_Campos.xlsx', dtype={0:'object', 1:'object',2:'object', 3:'object', 4:'object', 5:'object', 6:'object', 7:'object', 8:'object', 9:'object', 10:'object', 11:'object', 12:'object'}))
    #Checa se a nova atualização veio depois da ultima informação do excel
    oldDate = datetime.strptime(cmps.dataset['Data'].iloc[-1], "%d/%m/%Y")
    newDate = datetime.strptime(dataHora, "%d/%m/%Y")
    
    #Se ontem teve dado novo:
    if (newDate - oldDate).days == 1:
        print("entrei")
        cmps.salvar_excel(get)
        del cmps
        analiseLoop(get)
        
    #Caso a prefeitura nao tenha postado algum dia - geralmente domingo
    #Aqui ele repete o ultimo dia antes do dia pulado para adicionar dado novo depois
    elif (newDate - oldDate).days > 1:
        print("Nao ha novos dados. Repetindo anterior")
        #Repete repetindo dados por quantos dias tiverem sido pulados
        for i in range(1, (newDate - oldDate).days):
            inserterDate = datetime.strftime(oldDate + timedelta(days=i), "%d/%m/%Y")
            cmps.dataset = cmps.dataset.append(cmps.dataset.iloc[-1])
            cmps.dataset['Data'].iloc[-1] = inserterDate

        #Entao continua normal
        cmps.salvar_excel(get)
        del cmps
        analiseLoop(get)
        
    else:
        None
        
__init__()
