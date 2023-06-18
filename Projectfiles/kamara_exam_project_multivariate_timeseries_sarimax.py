# -*- coding: utf-8 -*-
"""KAMARA-Exam_Project_Multivariate-TimeSeries_SARIMAX.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/13s22Ler9L1YScv0o7PE4TcNyE41GnggJ

# **Multivariate timeseries with SARIMAX**

**Predicting the GDP using mulitple exogenous variables**: real-consumption,	real-investment, real-government-spending,	real-disposable-income,	consumer-prce-index,	m1,	tbilrate,	unemployment,	population,	inflation,	real-investment.

**Import the liabraries:**
"""

# import the packages
import pandas as pd
import numpy as np
from statsmodels.tsa.statespace.sarimax import SARIMAX
import matplotlib.pyplot as plt
import statsmodels.api as sm
from statsmodels.tsa.stattools import acf

"""**Import the dataset:**"""

# import built-in macro dataset from statsmodels.api 
mdata_org = sm.datasets.macrodata.load_pandas().data
# create a copy of the original dataset
macro_data = mdata_org.copy()

"""**Explore the dataset:**"""

# head
macro_data.head()

# tail
macro_data.tail()

# shape of the data
macro_data.shape

# datatypes
macro_data.dtypes

# missing values
macro_data.isna().sum()

# prepare the dates index
dates = macro_data[['year', 'quarter']].astype(int).astype(str)
quarterly = dates["year"] + "Q" + dates["quarter"]

# converting strings to date
from statsmodels.tsa.base.datetools import dates_from_str
quarterly = dates_from_str(quarterly)

# create a copy by slicing everything
macdata = macro_data[:]
# set quaterly variable to Index
macdata.index = pd.DatetimeIndex(quarterly)
# run the code below to export to csv for use in other application such as excel
macdata.to_csv('MacroData_datetimeIndex.csv', index = False, encoding='utf-8') # False: not include index

# view the top 10
macdata.head(10)

plt.plot(macdata.index,macdata['realgdp'])
plt.title('RealGDP from 1959 - 2009 [thousand USD]')
plt.show()

# plot the real gdp since i am only interested in it
# import plotly.express as px
# fig = px.line(macdata, x=macdata.index, y=macdata['realgdp'], title='RealGDP from 1959 - 2009 [thousand USD]')
# fig.show()

"""**Preprocess the data:**"""

# Preprocessing, log - diff transform
# df = pd.read_csv('MacroData_datetimeIndex.csv', header=0)
# since we are interested in the realgdp column we just grab it
GDP_df = macdata['realgdp'] # array of sales data
logdata = np.log(GDP_df) # log transform

logdiff = pd.Series(logdata).diff() # logdiff transform

# Preprocessing, train and test set
cutpoint = len(logdiff) - 12
train = GDP_df[:cutpoint]
test = GDP_df[cutpoint:]

"""**Decompose the RealGDP series: for seasonality and trends:**"""

# import statsmodels for decomposition
from statsmodels.tsa.seasonal import seasonal_decompose
# assign the variable
results = seasonal_decompose(GDP_df,model='multiplicative')
# output the result
results.plot();
plt.show()


"""You can also plot each and every item in the result:"""

# results.seasonal.plot(figsize=(12,8), title = "Seasonal");
# results.resid.plot(figsize=(12,8), title = "Resid");
# results.trend.plot(figsize=(12,8), title = "Trend");

"""**Fit the model:**"""

# create a copy of macdata
data = macdata.copy()
# drop the year and quarter column since they have been concatenated
data.drop(['year', 'quarter'], axis = 1, inplace = True) 
# show the first 10 rows
data.head()
# make a copy of the dataframe
GDP_df = data.copy()

# assing the y value
y = GDP_df['realgdp']
# drop realgdp value
GDP_df.drop(['realgdp'], axis = 1, inplace = True) 
x = GDP_df.iloc[:, :-1]

# output y
y.head()

# output x
x.head()

"""**Fit the model**"""

# Fit the model
model = SARIMAX(y, exog=x, order=(0,2,2), seasonal_order=(0,1,0,4))
sfit = model.fit(disp=False)
print(sfit.summary())

"""**Plot the prediction:**"""

#test

#ypred

# ***** Predictions in-sample: ********
ypred = sfit.predict(len(train),len(train)+11)
plt.plot(train.index, train, label="train")
plt.plot(test.index, test, label="actual")
plt.plot(test.index, ypred, label="forecast")
plt.xlabel('Date')
plt.ylabel('GDP')
plt.title("Real GDP [thousand dollars]")
plt.legend()
plt.show();

plt.plot(test, label="actual")
plt.plot(ypred, label="forecast")
plt.title("Actual vs Forecast values")
plt.xticks(rotation=45)
plt.legend()
plt.show();

"""**Accuracy metrics:**"""

######## ****************** Accuracy metrics ************************
def forecast_accuracy(forecast, actual):
    mape = np.mean(np.abs(forecast - actual)/np.abs(actual)) # MAPE
    me = np.mean(forecast - actual) # ME
    mae = np.mean(np.abs(forecast - actual)) # MAE
    mpe = np.mean((forecast - actual)/actual) # MPE
    rmse = np.mean((forecast - actual)**2)**.5 # RMSE
    corr = np.corrcoef(forecast, actual)[0,1] # correlation coeff
    mins = np.amin(np.hstack([forecast[:,None], actual[:,None]]), axis=1)
    maxs = np.amax(np.hstack([forecast[:,None], actual[:,None]]), axis=1)
    minmax = 1 - np.mean(mins/maxs) # minmax
    acf1 = acf(forecast-actual)[1] # ACF1
    return({'mape':mape, 'me':me, 'mae': mae, 'mpe': mpe, 'rmse':rmse,'acf1':acf1, 'corr':corr, 'minmax':minmax})

# instatiate the values to calculate the metric evaluation
forecast_values = np.array(ypred)
actual_vaues = np.array(test)

# output the accuracy
print("THE METRICS:",);
# assign to an object
metrics = forecast_accuracy(forecast_values, actual_vaues)
# iterate through the object and print out each metric
for i in metrics:
  print(i,":",metrics[i])