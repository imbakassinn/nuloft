import pandas as pd
import numpy as np
import tensorflow as tf
import xarray as xr
import matplotlib.pyplot as plt
import math
import pickle

#physical_devices = tf.config.list_physical_devices('GPU')
#tf.config.experimental.set_memory_growth(physical_devices[0], enable=True)

def opnaERA5Land(slod):
    ds = xr.open_dataset(slod) #ERA5Land gögn - nota líka bara 2019
    forecasts = ds.sel(latitude=64.1,longitude=-21.9).to_dataframe()
    forecasts['f10'] = (forecasts['u10']**2+forecasts['v10']**2)**0.5
    forecasts['d10'] = np.arctan2(forecasts['u10']/forecasts['f10'], forecasts['v10']/forecasts['f10'])+np.pi
    return forecasts
    
def opnaPM10maelingar(slod):
    measurements = pd.read_excel(slod) #Gögn um svifryk - Nota 2019 sem sýnidæmi
    measurements.index = pd.to_datetime(measurements['time']) 
    return measurements
def mergeMeasurementsForecasts(measurements,forecasts):
    """Sameina loftgæðamælingar og veðurspá
       Tekur inn annars vegar loftgæðamælingar sem df
       og hingsvegar veðurspá sem df"""
    measurements = measurements.loc[~measurements.index.duplicated(keep='first')]
    forecasts = forecasts.loc[~forecasts.index.duplicated(keep='first')]
    weatherdata = pd.concat([measurements, forecasts], axis=1)
    weatherdata = weatherdata.dropna()
    del weatherdata['time']
    del weatherdata['longitude']
    del weatherdata['latitude']
    return weatherdata
    
def extractMonth(data):
    """Skilar mánuði útfrá gefnum datetime"""
    return data.month
    
def extractHour(data):
    """Skilar klukkustund útfrá gefnum datetime"""
    return data.hour

def normalizeData(weatherdata):
    """Normalisera gögnin þannig öll gildi verða á bilinu -1 til 1
       Gert til að líkanið gefi ekki háum breytum s.s. loftþrýstingi aukið vægi"""
    data_mean = weatherdata.mean(axis=0)
    data_std = weatherdata.std(axis=0)
    with open('data_mean.pickle', 'wb') as handle:
        pickle.dump(data_mean, handle, protocol=pickle.HIGHEST_PROTOCOL)
    with open('data_std.pickle', 'wb') as handle:
        pickle.dump(data_std, handle, protocol=pickle.HIGHEST_PROTOCOL)
    normdata = (weatherdata-data_mean)/data_std
    return normdata

def prepareInputData(normdata,history,future):
    """Velur dálka og breytir gögnum þannig hægt sé að fóðra Tensorflow með þeim"""
    historicaldata = []
    forecastdata = []
    for i in range(0,len(normdata)+1-future-history):
        historicaldata.append(normdata.iloc[i:history+i][['pm10']].values)
        forecastdata.append(normdata.iloc[i+history:history+future+i][COLUMNS].values)
    return historicaldata, forecastdata

def prepareOutputData(weatherdata,history,future):
    """Undirbýr tilbúin úttaksgögn svo hægt sé að prófa líkanið"""
    truedata = []
    for i in range(0, len(weatherdata) + 1 - future - history):
        truedata.append(weatherdata.iloc[i + history:history + future + i]['pm10'].values)
    return truedata
    
def traintest(data,trainfrac):
    """Skiptir gögnunum í train og test búta"""
    train = data[0:int(len(forecastdata)*(1-trainfrac))]
    test = data[-int(len(forecastdata)*(trainfrac)):]
    return np.array(train),np.array(test)
    
def createModel(forecast_dataset_train,historical_dataset_train,forecast_dataset_test,historical_dataset_test):
    """Býr til líkanið, hér er breytt ef fikta á í líkaninu"""
    input1 = tf.keras.layers.Input(shape=historical_dataset_train[0].shape)
    lstm1 = tf.keras.layers.LSTM(16,return_sequences=True)(input1)
    lstm2 = tf.keras.layers.LSTM(8,activation='relu')(lstm1)

    input2 = tf.keras.layers.Input(shape=forecast_dataset_train[0].shape)
    lstm3 = tf.keras.layers.LSTM(16,return_sequences=True)(input2)
    lstm4 = tf.keras.layers.LSTM(8,activation='relu')(lstm3)

    concat = tf.keras.layers.Concatenate()([lstm2, lstm4])
    lstm5 = tf.keras.layers.Dense(8,activation='relu')(concat)
   

    output = tf.keras.layers.Dense(FUTURE)(lstm5)

    full_model = tf.keras.Model(inputs=[input1,input2], outputs=[output])
    full_model.compile(optimizer=tf.keras.optimizers.RMSprop(clipvalue=1.0), loss='mse')
    return full_model
    
TRAINFRAC = 0.1
HISTORY = 12
FUTURE = 48
BATCH_SIZE = 10
COLUMNS = ['f10','d10','t2m','tp','man','klst']

forecasts = opnaERA5Land('ollgogn.nc')
measurements = opnaPM10maelingar('grensas_pm10_2019.xlsx')

weatherdata = mergeMeasurementsForecasts(measurements,forecasts)
weatherdata['timi'] = weatherdata.index
weatherdata['man'] = weatherdata['timi'].apply(extractMonth)
weatherdata['klst'] = weatherdata['timi'].apply(extractHour)
del weatherdata['timi']
normdata = normalizeData(weatherdata)
historicaldata, forecastdata = prepareInputData(normdata,HISTORY,FUTURE)
truedata = prepareOutputData(weatherdata,HISTORY,FUTURE)

historicaldata_train,historicaldata_test = traintest(historicaldata,TRAINFRAC)
forecastdata_train,forecastdata_test = traintest(forecastdata,TRAINFRAC)
truedata_train,truedata_test = traintest(truedata,TRAINFRAC)

model = createModel(forecastdata_train,historicaldata_train,forecastdata_test,historicaldata_test)

history = model.fit([historicaldata_train,forecastdata_train], truedata_train,
                                          batch_size=BATCH_SIZE,
                                          epochs=10,
                                          validation_data=([historicaldata_test,forecastdata_test],truedata_test),
                                          validation_steps=10)

model.save('grensasvegur')


