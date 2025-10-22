import streamlit as st
import pandas as pd
import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Анализ грузоперевозок", layout="wide")

st.title(":truck: Анализ транспортно - экспедиционных грузоперевозок по Российской Федерации")


df = pd.read_csv('data/perevozki_processing.csv')

with st.sidebar:
    rasstoyanie_km_peremennayay = st.slider('Расстояние', min_value=df['rasstoyanie_km'].min(
    ), max_value=df['rasstoyanie_km'].max(), value=5000.0, step=500.0)
    
    
    all_status = st.checkbox("Выбрать все статусы",
                             value=True, key='all_status')
    if all_status:
        selected_status = st.multiselect(
            'Выберите статус перевозки:',
            options=df['status_perevozki'].unique(),
            default=df['status_perevozki'].unique())
    else:
        selected_status = st.multiselect(
            'Выберите статус перевозки:', options=df['status_perevozki'].unique())


    all_cargo = st.checkbox(
        "Выбрать все города отправления",  value=True, key='all_cargo')
    if all_cargo:
        selected_cargo_type = st.multiselect(
            'Выберите город отправления:', options=df['gorod_zagruzki'].unique(), default=df['gorod_zagruzki'].unique())
    else:
        selected_cargo_type = st.multiselect(
            'Выберите город отправления:', options=df['gorod_zagruzki'].unique())


    all_cargop = st.checkbox(
        "Выбрать все города получения",  value=True, key='all_cargop')
    if all_cargop:
        selected_cargop_type = st.multiselect(
            'Выберите город получения:', options=df['gorod_razgruzki'].unique(), default=df['gorod_razgruzki'].unique())
    else:
        selected_cargop_type = st.multiselect(
            'Выберите город получения:', options=df['gorod_razgruzki'].unique())
    all_identificatin = st.checkbox('Выбрать все', value=True, key='all_identificatin')
    options = df['identification_otklonenie_ot_plana_dney'].unique()

    if all_identificatin:
        selected_identification_otlklonenie = st.multiselect(
            'Тип задержки',
            options=options,
            default=options  
        )
    else:
        selected_identification_otlklonenie = st.multiselect(
            'Тип задержки',
            options=options
    )



filtered_df = df[
    (df['status_perevozki'].isin(selected_status)) &
    (df['gorod_zagruzki'].isin(selected_cargo_type)) &
    (df['gorod_razgruzki'].isin(selected_cargop_type)) &
    (df['rasstoyanie_km'].le(rasstoyanie_km_peremennayay)) &
    (df['identification_otklonenie_ot_plana_dney'].isin(selected_identification_otlklonenie))]

st.dataframe(filtered_df)


st.write("---")
st.markdown("###  Ключевые метрики")
col1, col2, col3, col4 = st.columns(4)
with col1:
    avg_profit = filtered_df['pribyl'].mean()
    st.metric(label="Средняя прибыль", value=f"{avg_profit:,.2f} тыс.руб.")
with col2:
    total_distance = filtered_df['rasstoyanie_km'].sum()
    st.metric(label="Суммарное расстояние", value=f"{total_distance:,.0f} км")
with col3:
    avg_delivery_time = round(filtered_df['srok_dostavki'].mean(), 2)
    st.metric(label="Средний срок доставки",
              value=f"{avg_delivery_time:,.1f} дней")
with col4:
    mod_machine_type = filtered_df['marka_model_avto'].mode()
    if not mod_machine_type.empty:
        st.metric(label='Часто используемый вид транспорта',
                  value=mod_machine_type[0])
    else:
        st.metric(label='Часто используемый вид транспорта',
                  value='Нет данных')

st.write("---")
st.header('📦 Прибыль по характеру груза')
fig = px.bar(
    filtered_df.groupby('tip_gruza')['pribyl'].sum().reset_index(),
    x='tip_gruza',
    y='pribyl')
st.plotly_chart(fig, use_container_width=True)

fig.add_hline(
    y=filtered_df['sebestoimost_perevozki'].mean(),
    line_dash="dot",
    annotation_text=f"Средняя себестоимость: {filtered_df['sebestoimost_perevozki'].mean():,.2f}",
    annotation_position="bottom right"
)

st.write("---")
st.header(':material/attach_money: Прибыль от расстояния')
fig_scatter = px.scatter(filtered_df, x='rasstoyanie_km', y='pribyl',
                         color='status_perevozki')
st.plotly_chart(fig_scatter, use_container_width=True)

st.write("---")
st.header('⚖️ Доля грузов по суммарному весу груза по компаниям '
          '(отправитель vs получатель)')

df_shippers = filtered_df.groupby('gruzootpravitel')[
    'tonnazh_gruza_tonn'].sum().reset_index()
df_shippers.columns = ['Компания', 'Суммарный вес']
df_shippers['Роль'] = 'Грузоотправитель'


df_consignees = filtered_df.groupby('gruzopoluchatel')[
    'tonnazh_gruza_tonn'].sum().reset_index()
df_consignees.columns = ['Компания', 'Суммарный вес']
df_consignees['Роль'] = 'Грузополучатель'


df_combined = pd.concat([df_shippers, df_consignees])


fig = px.bar(
    df_combined,
    x='Компания',
    y='Суммарный вес',
    color='Роль',
    barmode='group',
    labels={
        'Компания': 'Компания',
        'Суммарный объем': 'Суммарный вес груза (тонн)',
        'Роль': 'Роль'
    }
)
fig.update_layout(
    xaxis_title_text='Компания',
    yaxis_title_text='Суммарный вес груза (тонн)',
    legend_title_text='Роль',
    xaxis={'categoryorder': 'total descending'}
)

fig.update_layout(
    width=800,
    height=600)
st.plotly_chart(fig)

st.write("---")
st.header(':material/local_shipping: Доля общего количества перевозок по типу кузова')
df_grouped = filtered_df.groupby(['tip_kuzova', 'marka_model_avto']).size(
).reset_index(name='Количество перевозок')
fig_pie_cargo = px.pie(
    df_grouped,
    values='Количество перевозок',
    names='tip_kuzova',
    hole=0.3)
fig_pie_cargo.update_traces(
    textposition='inside',
    textinfo='percent+label',
    textfont_size=20)
fig_pie_cargo.update_layout(
    width=800,
    height=600)
fig_pie_cargo.update_traces(marker=dict(
    line=dict(width=1, color='DarkSlateGrey')))
st.plotly_chart(fig_pie_cargo, use_container_width=True)
