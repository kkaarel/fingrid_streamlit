import requests
import json
import pandas as pd
from datetime import datetime, date, timedelta
import streamlit as st

#Fingrid api instructions  https://data.fingrid.fi/en/pages/apis

#Get your own api key from https://data.fingrid.fi/open-data-forms/registration/
#Create a secret in .streamlit/secrets.toml
API_key = st.secrets["apikey"]

##Fingrid api testing

st.title("Fingrid Api")

#The variable number can be different, so check what data you want from the library 

MINIMUM_DAYS = 21

# Create a list of dates starting from today and going back 90 days - have some limitations
today = datetime.utcnow()
start_date = today - timedelta(days=90)
dates = []
while start_date <= today:
    dates.append(start_date)
    start_date += timedelta(days=1)

# Create a select box with the dates
start_date = st.selectbox("Select a start date", dates, format_func=lambda d: d.strftime('%Y-%m-%d'))
min_end_date = start_date + timedelta(days=MINIMUM_DAYS)
end_dates = [d for d in dates if d >= min_end_date]
end_date = st.selectbox("Select an end date", end_dates, format_func=lambda d: d.strftime('%Y-%m-%d'))

#Date convert
start_datestr = start_date.strftime("%Y-%m-%dT%H:%M:%SZ")


end_datestr = end_date.strftime("%Y-%m-%dT%H:%M:%SZ")

def get_f_data(start_datestr, end_datestr):
    # Source https://data.fingrid.fi/fi/dataset/updated-electricity-consumption-forecast-of-finland
    catalog = 166
    url = 'https://api.fingrid.fi/v1/variable/{}/events/json'.format(catalog)
    headers = {'x-api-key':API_key, 'Accept':'application/json'}
    payload = {"start_time": start_datestr, "end_time": end_datestr, "limit": 100}
    response = requests.get(url, headers=headers, params=payload)
    if response.ok:
        df = pd.json_normalize(response.json()) 
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df['start_time'] = df['start_time'].dt.strftime('%Y-%m-%d')
        df['end_time'] = df['end_time'].dt.strftime('%Y-%m-%d')
        return df #st.write(df)

def bar_chart():
    st.title("Kulutusennuste - sähkö")
    chart_data = get_f_data(start_datestr, end_datestr)

    return st.bar_chart(chart_data, y ="value", x="end_time")  

def sahkonhinta_now(start_datestr, end_datestr):
    # Source https://data.fingrid.fi/fi/dataset/electricity-consumption-in-finland
    catalog=124
    st.title("Sähkönkulutus Suomessa ")
    payload = {"start_time": start_datestr, "end_time": end_datestr, "limit": 100}
    url = 'https://api.fingrid.fi/v1/variable/{}/events/json'.format(catalog)
    headers = {'x-api-key':API_key, 'Accept':'application/json'}
    response = requests.get(url, headers=headers, params=payload)
    if response.ok:
        df = pd.json_normalize(response.json())
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        df['start_time'] = df['start_time'].dt.strftime('%Y-%m-%d %H:%M')
        df['end_time'] = df['end_time'].dt.strftime('%Y-%m-%d %H:%M')
        return st.line_chart(df, y ="value", x="end_time")   #st.write(df)

def line_chart():
    ss= sahkonhinta_now()
    return st.line_chart(ss, y ="value", x="start_time")  

#The button will start the query to the the data
if st.button("Get data from Fingrid"):
    if start_datestr is not None and end_datestr is not None and start_datestr.strip()!='' and end_datestr.strip()!='':
        try:
            get_f_data(start_datestr, end_datestr)
            bar_chart()
            sahkonhinta_now(start_datestr, end_datestr)
         
        except ValueError:
            st.error("Do better, you have a problem")
    else:
        st.error("There is only one right date format")    

#This is just a demo, don't use this in production



