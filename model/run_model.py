import pandas as pd
import urllib.request, json 
import datetime
import requests
import pickle
import numpy as np
import tensorflow as tf

def getPM10data():
    #Sækir PM10 gögn í API Umhverfisstofnunar
    with urllib.request.urlopen("https://api.ust.is/aq/a/getLatest") as url:
        data = json.loads(url.read().decode())
        grensas = (data['STA-IS0005A']['parameters']['PM10'])
        pm10maelingar = []
        for i in range(24-HISTORY,24):
            pm10maelingar.append(float(grensas[str(i)]['value']))
    return pm10maelingar

def getWeatherdata(vi=True):
    #Sækir veðurspá annað hvort úr líkani Bliku eða Veðurstofunnar fyrir Reykjavík
    #vi = True fyrir Veðurstofuna
    #vi = False fyrir Bliku
    if vi:
        apislod = 'https://api.blika.is/GetIGBForecastDag'
    else:
        apislod = 'https://api.blika.is/GetBlikaForecastDag'
    
    nuna = datetime.datetime.now()
    morgun = nuna+datetime.timedelta(days=1)
    hinn = nuna+datetime.timedelta(days=2)

    headers = {'Accept': 'application/json'}
    
    nunaurl = f'{apislod}/4/{nuna.year}/{nuna.month}/{nuna.day}'
    nunar = requests.get(nunaurl, headers=headers)
    nunadf = pd.DataFrame(nunar.json())

    morgunurl = f'{apislod}/4/{morgun.year}/{morgun.month}/{morgun.day}'
    morgunr = requests.get(morgunurl, headers=headers)
    morgundf = pd.DataFrame(morgunr.json())

    hinnurl = f'{apislod}/4/{hinn.year}/{hinn.month}/{hinn.day}'
    hinnr = requests.get(hinnurl, headers=headers)
    hinndf = pd.DataFrame(hinnr.json())

    vedurspa = pd.concat([nunadf,morgundf,hinndf])
    dags = vedurspa['dags_spar']
    spadags = vedurspa['dags_keyrsla']
    #Endurnefni dálka svo þeir passi miðað við gögnin úr ERA5Land
    vedurspa.columns=(['dags_keyrsla','dags_spar','t2m','slp','f10','d10','tp','nl',
                        'nm','nh','rh2','upplausn','i','j','innsett_dags','dtexti',
                        'merki','stodid','nafn'])
                    
    #Breyti einingum til að samrýma við ERA5Land
    vedurspa['t2m'] = vedurspa['t2m']+273.15 #Breyti úr C í Kelvin
    vedurspa['d10'] = vedurspa['d10']*(np.pi/180) #Breyti úr gráðum í Radíana
    vedurspa['tp'] = vedurspa['tp']/1000 #Breyti úr mm í m
    vedurspa = vedurspa[COLUMNS].iloc[0:FUTURE]
    return vedurspa,dags,spadags
    
def keyraLikan():
    pm10maelingar = getPM10data()
    tensorspa, dags, spadags = getWeatherdata(False)

    #Sæki meðaltal og staðalfrávik svo hægt sé að "normalisera" gögnin
    with open('data_mean.pickle', 'rb') as handle:
        data_mean = pickle.load(handle)[COLUMNS]
        
    with open('data_std.pickle', 'rb') as handle:
        data_std = pickle.load(handle)[COLUMNS]


    tfinput1 = []
    tfinput2 = []

    #"normalisera" gögnin
    tfinput1.append(((tensorspa-data_mean)/data_std).values)
    tfinput2.append(pm10maelingar)

    tfinput1 = np.array(tfinput1)
    tfinput2 = np.array(tfinput2)


    model = tf.keras.models.load_model('grensas')

    prediction = model.predict([np.array(tfinput2),np.array(tfinput1)])
    forecast = pd.DataFrame(list(zip(list(spadags),list(dags),prediction[0])),columns=['forecast_time','valid_time','pm10'])
    return forecast
    
#Fastar fyrir líkanið
HISTORY = 12
FUTURE = 48
COLUMNS = ['f10','d10','t2m','tp']
