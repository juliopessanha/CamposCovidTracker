import numpy as np
import pandas as pd
import tweepy
import matplotlib.pyplot as plt

path = 'your/folder/path'
#path = ''
img_path = path + "vacinometro.jpg"
file_path = path + 'Casos_Campos.xlsx'

df = pd.read_excel(file_path) #reading the excel file with covid data

total = 383173 #total amount of 18+ ppl in Campos. Got it from Rio de Janeiro's official site
primeira_dose = int(df['Vacinados'].iloc[-1])  #first dose
segunda_dose = int(df['Segunda Dose'].iloc[-1]) #second dose
dose_unica = int(df['Dose Única'].iloc[-1]) #unique dose
totalmente_imunizados = segunda_dose + dose_unica #totally imune (first + second dose)

pct_primeira_dose = round((primeira_dose/total)*100) #% of the population with first dose

pct_segunda_dose = round((segunda_dose/total)*100) #% of the population with second

pct_dose_unica = round((dose_unica/total)*100) #% of the unique dose

pct_totalmente_imunizados = round((totalmente_imunizados/total)*100) #% of the population totally imune

category_names = ['Vacinados', 'Não Vacinados', 'placeholder']
results = {
    '1ª Dose': [pct_totalmente_imunizados, (pct_primeira_dose - pct_totalmente_imunizados), (100 - pct_primeira_dose)]
}
#,
#    '2ª Dose': [pct_totalmente_imunizados, (100 - pct_totalmente_imunizados)]


#Função para transformar mês numeral em escrito
def month_checker(mes):

    if mes == '01':
        return('Janeiro')
    elif mes == '02':
        return('Fevereiro')
    elif mes == '03':
        return('Março')
    elif mes == '04':
        return('Abril')
    elif mes == '05':
        return('Maio')
    elif mes == '06':
        return('Junho')
    elif mes == '07':
        return('Julho')
    elif mes == '08':
        return('Agosto')
    elif mes == '09':
        return('Setembro')
    elif mes == '10':
        return('Outubro')
    elif mes == '11':
        return('Novembro')
    elif mes == '12':
        return('Dezembro')
    
#Taking the covid data to make the bar graph. Got it's base from matplotlib official site
def survey(results, category_names):
    """
    Parameters
    ----------
    results : dict
        A mapping from question labels to a list of answers per category.
        It is assumed all lists contain the same number of entries and that
        it matches the length of *category_names*.
    category_names : list of str
        The category labels.
    """
    labels = list(results.keys())
    data = np.array(list(results.values()))
    data_cum = data.cumsum(axis=1)

    fig, ax = plt.subplots(figsize=(8, 0.3))
    ax.invert_yaxis()
    ax.xaxis.set_visible(False)
    ax.set_xlim(0, np.sum(data, axis=1).max())
    lightblue = '#3AA6E2' #lightblue hex color code
    darkblue = '#3A66A8' #darkblue hex color code
    grey = '#AAA6A6' #grey hex color code
    colors = [darkblue, lightblue, 'lightgrey']
    for i, (colname, color) in enumerate(zip(category_names, colors)):

        widths = data[:, i]
        starts = data_cum[:, i] - widths
        
        rects = ax.barh(labels, widths, left=starts, height=0.5,
                        label=colname, color=color)

        text_color = 'black' #if r * g * b < 0.5 else 'darkgrey'
        ax.bar_label(rects, label_type='center', color=text_color, fontsize = 1)
    #ax.legend(ncol=len(category_names), bbox_to_anchor=(0, 1),
    #          loc='lower left', fontsize=11.5)
    
    plt.axis('off')
    #plt.yticks(fontsize = 0.1)
    ax.spines['right'].set_visible(False)
    ax.spines['top'].set_visible(False)
    ax.spines['bottom'].set_visible(False)
    ax.spines['left'].set_visible(False)
    
    #Defining line height of each row of text
    first_line_height = 10.3
    second_line_height = 8.4
    third_line_height = 6.5
    forth_line_height = 4.5

    #DOWN HERE I'M BASIALLY DRAWING EVERY SINGLE LINE OF TEXT BY HAND. CRAFTING THE FINAL FORM STEP BY STEP

    first_text = 'Em ' + df.Data.iloc[-1][0:2] + ' de ' + month_checker(df.Data.iloc[-1][3:5]) + ' de ' + df.Data.iloc[-1][6:] + ","

    #First line
    
    ax.text(0, first_line_height, first_text, horizontalalignment='left', 
            verticalalignment='top', transform=ax.transAxes, fontsize = '22', color = grey)
    
    #Second line
    ax.text(0, second_line_height, 'Campos registrou', horizontalalignment='left', 
            verticalalignment='top', transform=ax.transAxes, fontsize = '22', color = grey)
    ax.text(0.45, 0.315+second_line_height, str(pct_primeira_dose) + "%", horizontalalignment='left', verticalalignment='top',
            transform=ax.transAxes, fontsize = '28', color = lightblue, weight= '600')
    ax.text(0.61, second_line_height, 'da', horizontalalignment='left', verticalalignment='top', 
            transform=ax.transAxes, fontsize = '22', color = lightblue)
    
    #Third line
    ax.text(0, third_line_height, 'população com pelo menos 1 dose', horizontalalignment='left', 
            verticalalignment='top', transform=ax.transAxes, fontsize = '22', color = lightblue)

    #Forth line
    ax.text(0, forth_line_height, 'e', horizontalalignment='left', verticalalignment='top', 
            transform=ax.transAxes, fontsize = '22', color = grey)
    ax.text(0.05, 0.315+forth_line_height, str(pct_totalmente_imunizados) + "%", horizontalalignment='left', verticalalignment='top',
            transform=ax.transAxes, fontsize = '28', color = darkblue, weight= '600')
    ax.text(0.22, forth_line_height, 'totalmente imunizada.', horizontalalignment='left', verticalalignment='top', 
            transform=ax.transAxes, fontsize = '22', color = darkblue)

    #Bottom text
    bottom_line_height = -0.35
    ax.text(0.01, bottom_line_height, '*população maior de idade.', horizontalalignment='left', verticalalignment='top', 
            transform=ax.transAxes, fontsize = '8', color = grey)
    
    position = (pct_segunda_dose/100)-0.025
    
    
    ax.text(position, -0.2, str(pct_totalmente_imunizados) + "%", horizontalalignment='left', verticalalignment='top', 
            transform=ax.transAxes, fontsize = '16', color = darkblue)
    
    position = (pct_primeira_dose/100)-0.025
    
    ax.text(position, -0.5, str(pct_primeira_dose) + "%", horizontalalignment='left', verticalalignment='top', 
            transform=ax.transAxes, fontsize = '16', color = lightblue)
    
    
    #plt.show()
    plt.savefig("vacinometro.jpg", bbox_inches = 'tight',pad_inches=0.36)
    plt.close()
    #return(fig, ax) #I'm returning but not using, could be removed since I get the saved figure


def tweet():
    # Authenticate to Twitter
    auth = tweepy.OAuthHandler("ok guys not gonna happen", "yes I must stop hard coding this I know")
    auth.set_access_token("i'm going to study how to make it better", "for now you can just copy and paste yours")

    # Create API object
    api = tweepy.API(auth)
    
    #twitter text
    msg = 'Vacinômetro Campos dos Goytacazes\n\n' \
    'Quantidade total de doses aplicadas:\n' \
    '   -Primeira Dose: %s (%s%%)\n   -Segunda Dose: %s (%s%%)\n   -Dose Única: %s (%s%%)' % (primeira_dose, pct_primeira_dose, segunda_dose, pct_segunda_dose, dose_unica, pct_dose_unica)
    
    #twitter image
    img_path = "vacinometro.jpg"
    
    print(msg)
    
    #twitter post
    api.update_with_media(img_path, msg)


if __name__ == '__main__':
    survey(results, category_names) #get the xlsx file and create the image to post
    tweet() #post on twitter