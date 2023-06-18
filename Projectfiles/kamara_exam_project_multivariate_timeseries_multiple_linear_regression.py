# -*- coding: utf-8 -*-
"""KAMARA-Exam_Project_Multivariate-TimeSeries_Multiple-Linear-Regression.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1ySOZeddAs7UrnNgioCKwO1WfXlJ0wKPL

# **Multivariate timeseries with Multiple Linear Regression**

**Predicting the GDP using mulitple exogenous variables**: real-consumption,	real-investment, real-government-spending,	real-disposable-income,	consumer-prce-index,	m1,	tbilrate,	unemployment,	population,	inflation,	real-investment.

**Datasource:** statsmodel inbuilt
"""

import statsmodels.api as sm
sm.datasets.macrodata.load_pandas().data.head()

"""**Import the liabraries:**"""

# import the packages
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statsmodels.api as stats
from statsmodels.tsa.stattools import acf

"""**Import the dataset:**"""

# import built-in macro dataset from statsmodels.api 
mdata_org = sm.datasets.macrodata.load_pandas().data
# create a copy of the original dataset
macro_data = mdata_org.copy()

"""**Explore the dataset:**"""

# head
macro_data.head()

# columns of the macrodata
macro_data.columns


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

# create a copy of macdata
data = macdata.copy()
# drop the year and quarter column since they have been concatenated
data.drop(['year', 'quarter'], axis = 1, inplace = True) 
# show the first 10 rows
data.head()

"""**Decompose the RealGDP series: for seasonality and trends:**"""

# import statsmodels for decomposition
from statsmodels.tsa.seasonal import seasonal_decompose
# assign the variable
results = seasonal_decompose(data['realgdp'],model='multiplicative')
# output the result
results.plot();

"""You can also plot each and every item in the result:"""

# results.seasonal.plot(figsize=(12,8), title = "Seasonal");
# results.resid.plot(figsize=(12,8), title = "Resid");
# results.trend.plot(figsize=(12,8), title = "Trend");

"""**Preprocess the data train-test split:**"""

# create a copy of macdata
data = macdata.copy()
# drop the year and quarter column since they have been concatenated
data.drop(['year', 'quarter'], axis = 1, inplace = True) 
# show the first 10 rows
data.head()
# make a copy of the dataframe
GDP_df = data.copy()

# assing the y value
train_df=GDP_df.sample(frac=0.94, random_state=99) #random state is a seed value
test_df=GDP_df.drop(train_df.index)

train_df.shape

test_df.shape

"""### Correlation Plot:"""

GDP_df.select_dtypes(exclude='object').corr().style.background_gradient(cmap='coolwarm')

"""**Fitting the Linear Regression Model 1 - overview:**"""

Y_train = train_df.realgdp
X_train = stats.add_constant(train_df.drop(columns=['realgdp']))

model_GDP = stats.OLS(Y_train, X_train)
results_GDP = model_GDP.fit()

print(results_GDP.summary())

GDP_df2 = GDP_df.copy() #.drop(columns=['realgovt','realdpi', 'cpi', 'm1','pop','infl','tbilrate'])
GDP_df2.select_dtypes(exclude='object').corr().style.background_gradient(cmap='coolwarm')

"""### Multicolinearity:"""

GDP_df2.head()

"""### Test/Train Split"""

train_df=GDP_df2[:191] #random state is a seed value
test_df=GDP_df2[191:]

train_df.shape

test_df.shape

"""**Fitting the Linear Regression Model 2:**"""

y_train = train_df.realgdp
x_train = stats.add_constant(train_df.drop(columns=['realgdp']))

model_GDP = stats.OLS(y_train, x_train)
results_GDP = model_GDP.fit()

print(results_GDP.summary())

"""Our sum of square residuals is then:"""

print('The sum of square residuals is {:.1f}'.format(results_GDP.ssr))

"""We can also use our test set to compare our predictions with the observed values."""

ytest = test_df.realgdp
test_df = stats.add_constant(test_df)
xtest = test_df[x_train.columns]

ypred= results_GDP.predict(xtest)
ypred

ytest

# plot the chart
#plt.plot(y_train.index, y_train, label="train")
plt.plot(ytest.index, ytest, label="actual")
plt.plot(ytest.index, ypred, label="forecast")
plt.xlabel('Date')
plt.ylabel('GDP')
plt.title("Real GDP [thousand dollars]")
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
actual_vaues = np.array(ytest)

# output the accuracy
print("THE METRICS:",);
# assign to an object
metrics = forecast_accuracy(forecast_values, actual_vaues)
# iterate through the object and print out each metric
for i in metrics:
  print(i,":",metrics[i])