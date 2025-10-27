
import pandas as pd
import streamlit as st
import plotly.express as px
#1) ANALYZING DATA 
df = pd.read_csv("Life Expectancy Data.csv")
#INSPECT
print(df.info())
print(df.columns)
print(df.describe)
#DELETING REDUNDANT COLUMNS
df.drop(columns=[' thinness  1-19 years', ' thinness 5-9 years', 'Income composition of resources', 'Schooling','Measles ','Polio','Diphtheria ',' HIV/AIDS','Hepatitis B'], inplace=True)
#RENAMING THE COLUMNS
df.columns = [i.strip().title() for i in df.columns]
df.rename(columns={'Gdp': 'GDP', 'Bmi': "BMI"}, inplace=True)
#HANDLING DUPLICATES
df.drop_duplicates(inplace=True)
df.reset_index().drop(columns='index', inplace=True)
#HANDLING NAN
df.dropna(inplace=True)
#SAVE CSV TO NEW FILE
df.to_csv("life_expectance_data_clean.csv")
print("data saved")
#VISUALIZATION USING STREAMLIT AND PLOTLY
df = pd.read_csv("life_expectance_data_clean.csv")
df.drop(columns='Unnamed: 0', inplace=True)
#SET TITLE
st.set_page_config(page_title="Global Life Expectancy Dashboard", layout="wide")
st.title("💊 Money, Medicine and Mortality")
st.write("An Analytical Dashboard on Global Life Expectancy")
#SET SIDE BAR
st.sidebar.header("Filter Your Data")
country = st.sidebar.multiselect(
    "Select Country(s)",
    options=df['Country'].unique(),
    default=df['Country'].unique()
)
status = st.sidebar.multiselect(
    "Select Status(s)",
    options=df['Status'].unique(),
    default=df['Status'].unique()
)
year = st.sidebar.multiselect(
    "Select year(s)",
    options=sorted(df['Year'].unique()),
    default=sorted(df['Year'].unique())
)
#FILTER DOWN DATA FRAME
filtered_df = df[
    (df["Country"].isin(country)) &
    (df["Status"].isin(status)) &
    (df["Year"].isin(year)) 
]
#ERROR HANDLING
if filtered_df.empty:
    st.warning("No data Selected. Please Adjust your Selections")
else:
    st.subheader("Filtered Dataframe")
    st.dataframe(filtered_df)
#KEY METRICS
total_pop = filtered_df['Population'].fillna(0).sum()
total_gdp = filtered_df['GDP'].fillna(0).sum()
total_exp = filtered_df['Total Expenditure'].fillna(0).sum()
st.metric("Total Population", f"{total_pop:,}")
st.metric("Total GDP", f"${total_gdp:,.2f}")
st.metric("Total Expenditure(in Million USD)", f"${total_exp}")
#BAR GRAPH- AVERGAGE LIFE EXPECTANCY BY COUNTRY
avg_life = filtered_df.groupby('Country')['Life Expectancy'].mean().reset_index()
fig_bar = px.bar(
    avg_life,
    x="Country",
    y='Life Expectancy',
    title="Average Life Expectancy(years) by Country",
    text="Life Expectancy"
)
st.plotly_chart(fig_bar, use_container_width=True)

#SCATTER PLOT - GDP vs LIFE EXPECTANCY
scatter_plt = px.scatter(
    filtered_df,
    x='GDP', y="Life Expectancy",
    color="Status",
    title="GDP vs Life Expectancy(years)"
)
st.plotly_chart(scatter_plt, use_container_width=True)

#BAR CHART - AVERAGE LIFE EXPECTANCY BY STATUS
avg_life_dev = filtered_df.groupby('Status')['Life Expectancy'].mean().reset_index()
fig_bar_status = px.bar(
    avg_life_dev,
    x="Status",
    y='Life Expectancy',
    title="Average Life Expectancy based on Status",
    text="Life Expectancy"
)
st.plotly_chart(fig_bar_status, use_container_width=True)

#STACKED BAR CHART - MORTALITY TYPES BY CATEGORY
bar_mortality = filtered_df.groupby('Country')[['Adult Mortality', 'Infant Deaths', 'Under-Five Deaths']].sum().reset_index()
fig = px.bar(
    bar_mortality,
    x="Country",
    y=['Adult Mortality', 'Infant Deaths', 'Under-Five Deaths'],
    barmode="stack",
    title="Mortality Types across Country (Summed)",
    
)
st.plotly_chart(fig, use_container_width=True)

#SIDE BY SIDE COMPARITIVE PIE CHART--> GLOBAL HEALTH EXPENDITURE BY COUNTRY AND STATUS (%)
status_weighed = (
    filtered_df.groupby("Status")
    .apply(lambda x: (x['Percentage Expenditure'] * x['GDP']).sum() / x["GDP"].sum())
    .reset_index(name="Weighted Expenditure")
)
country_weighed = (
    filtered_df.groupby("Country")
    .apply(lambda x: (x['Percentage Expenditure'] * x['GDP']).sum() / x["GDP"].sum())
    .reset_index(name="Weighted Expenditure")
    .nlargest(5, "Weighted Expenditure")
)

#Pie 1: By Status
pie_status = px.pie(
    status_weighed,
    names="Status",
    values="Weighted Expenditure",
    title="(GDP-weighted) % Expenditure(By Status)"
)
#Pie 2: By country
pie_country = px.pie(
    country_weighed,
    names="Country",
    values="Weighted Expenditure",
    title="(GDP-weighted) % Expenditure(By Country)"
)
#side by side comparitive charts
col1, col2 = st.columns(2)
col1.plotly_chart(pie_status, use_container_width=True)
col2.plotly_chart(pie_country, use_container_width=True)
#DOWNLOAD YOUR CSV
csv = filtered_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📩 Download CSV",
    data=csv,
    file_name="Life_expectancy_filtered.csv",
    mime="text/csv"
)