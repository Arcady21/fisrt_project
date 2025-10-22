import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Главная страница", layout='wide')

st.title('Обзор данных')


df = pd.read_csv('data/pervozki_with_regions.csv')
st.write("### Исходные данные:")
st.dataframe(df.head(10))

df = pd.read_csv('data/perevozki_processing.csv')
st.write("### Обработанные данные:")
st.dataframe(df.head(10))




