import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
sns.set_theme()



st.title('Crunchbase startups: from 20th century to 2014')
st.image('https://about.crunchbase.com/wp-content/uploads/2020/09/crunchbase-case-studies.jpg')
st.markdown("""Crunchbase is the leading destination for company insights from early-stage startups to the Fortune 1000. The dataset from Kaggle describes information scrapped from Crunchbase API.  
Link to the dataset: https://www.kaggle.com/datasets/arindam235/startup-investments-crunchbase""")
df = pd.read_csv('cleaned_data.csv', index_col='Unnamed: 0')
st.title('Some statistics per feature')

with st.expander('View table'):
    st.dataframe(df.describe())

st.title('Overview')

top_spheres = df['market'].value_counts()[:10]
fig = px.pie(values=top_spheres, names=top_spheres.index, title='Top 10 most expensive markets');
st.plotly_chart(fig)

fig = px.histogram(df['status'], title='Startups status')
st.plotly_chart(fig)
st.write("Most startups are operational, and that's good!")

rounds = {}
for i in df.columns:
    if 'round_' in i:
        rounds[i] = df[i].mean()/10**6
fig = px.histogram(x=rounds.keys(), y=rounds.values(), labels={'y': 'Investment ($ million)', 'x': 'Rounds'}, title='Investment per round');
st.plotly_chart(fig)

fig = px.histogram(x=['angel', 'grant', 'venture'], y=[len(df[df['angel']!=0]),len(df[df['grant']!=0]), len(df[df['venture']!=0])], title='Startups investment sources');
st.plotly_chart(fig)
st.write('This makes sense, because venture capitals are provided by professional investors and give startups way more funding')


top_countries = df['country'].value_counts()[:10]
fig = px.pie(values=top_countries, names=top_countries.index, title='Top 10 most popular regions for a startup');
st.plotly_chart(fig)
st.write("*Hmmm*, will the funding be also biggest in the USA? Let's check!")

funds_by_country = {}
for c in set(df['country']):
    funds_by_country[c] = df[df['country']==c]['funding_total_usd'].sum()/10**9
funds_by_country = sorted(funds_by_country.items(), key=lambda x: x[1], reverse=True)
fig = px.histogram(
    y=[x[0] for x in funds_by_country][:10], 
    x=[x[1] for x in funds_by_country][:10],
    title='Top 10 countries by total funding');
st.plotly_chart(fig)
st.write("No surprise here! Go to the US if you want to raise more money. But **be aware** of the competitors:")

top_companies = df.sort_values(by=['funding_total_usd'], ascending=False)[:25]
fig = px.histogram(data_frame=top_companies, x='funding_total_usd', 
y='name', 
title='Top 25 most successfull companies by year',
labels={'x': 'Total funding', 'y': 'Company'}, 
color='founded_year');
st.plotly_chart(fig)
st.write("Seems like company's success doesn't really depend on the year it was founded")

st.title('Closer analysis')
st.subheader('Correlation')
fig = px.imshow(df.corr(), title='Correlation heatmap');
st.plotly_chart(fig)

st.markdown("""### Question: \nThe plot shows high positive correlation between **debt_financing** and **funding_total_usd**. Why so?""")
fig = px.scatter(df[(df['debt_financing']>0)&(df['funding_total_usd']/10**9 < 30)], 
x='funding_total_usd', 
y='debt_financing', 
trendline="ols",
title='Correlation between debt financing and startup funding')
st.plotly_chart(fig)
st.write("Now it's clear that the more money you need for the startup, the more debt_financing you'll need.")

st.markdown("""### Hypothesis: \nEvery year startups need more $$$ to raise. Is that true? 
Let's calculate total funding by year and make a line plot:""")
years = set(df['founded_year'])
fund_by_year = {}
for year in sorted(years):
    fund_by_year[year] = df[df['founded_year']==year]['funding_total_usd'].sum()/10**9
fig = px.line(x = fund_by_year.keys(), y=fund_by_year.values(), labels={'x': 'Year', 'y': 'Funding in $ billions'})
st.plotly_chart(fig)
st.write("""From this graph, economic recessions can clearly be seen. In the 1983, [Israel bank stock crisis](https://en.wikipedia.org/wiki/1983_Israel_bank_stock_crisis) 
hit the market and the banks no longer had the capital to buy back shares and to support the prices causing share prices to collapse. Then, from 1984 to 2007, startups raised more and more $$$ each year, untill the [Global Financial Crisis in 2007](https://en.wikipedia.org/wiki/Financial_crisis_of_2007–2008), the most serious in the 21st century. 
So, the **hypothesis is partly true**. Indeed, startups raise more and more capital each year, but it strongly depends on the global events like crises. """)


st.markdown("""### Hypothesis: \nYour startup will less likely close at less popular market.
Let's see that on a heatmap.""")
markets = pd.read_csv('markets.csv', index_col='Unnamed: 0')
fig = px.imshow(
    markets[['share']][:20],
    aspect='auto',
    title='Top 20 markets where startups close',
    labels=dict(x="Market share", y="", color="Market share (%)"),
)
st.plotly_chart(fig, use_container_width=True)
st.markdown("""The hypothesis turns out to be true! The closer market to the top, the more 'yellow' (bigger) its market share becomes. 
Thus, choose less popular markets to succeed!""")

st.markdown("""### Hypothesis: 
The **seed**(the first official investment round) you raise depends on the **founded quater**.\n
Are there any 'good' quaters to start your first fund raising?""")
fig = px.scatter(
    y=df.sort_values(by='quater')['seed'], 
    x=df.sort_values(by='quater')['quater'],
    title='Seed values for various quaters',
    labels={'x': 'Quater the startup was founded at', 
    'y': 'Seed capital'})
st.plotly_chart(fig)

df_by_q_sort = df.sort_values(by='quater')
num_seed = []
for q in df_by_q_sort['quater'].unique():
    num_seed.append(len(df_by_q_sort[(df_by_q_sort['quater']==q)&(df_by_q_sort['seed'] > 0)]))
fig = px.histogram(
    y=num_seed, 
    x=df_by_q_sort['quater'].unique(),
    title='Quater x Seed Number plot',
    labels={'x': 'Quater the startup was founded at', 
    'y': '  seeds raised'})
st.plotly_chart(fig)
st.markdown("""Unfortunately, no. Seed capital seems to depend on other factors. 
However, **the biggest number** of seeds raised was at the **1st Quater**! That's the most popular time startups raise their first money""")

