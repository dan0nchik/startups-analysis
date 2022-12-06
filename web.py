import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
sns.set_theme()
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)



st.title('Crunchbase startups: from 20th century to 2014')
st.image('https://about.crunchbase.com/wp-content/uploads/2020/09/crunchbase-case-studies.jpg')
st.markdown("""Crunchbase is the leading destination for company insights from early-stage startups to the Fortune 1000. The dataset from Kaggle describes information scrapped from Crunchbase API.  
Link to the dataset: https://www.kaggle.com/datasets/arindam235/startup-investments-crunchbase""")
df = pd.read_csv('cleaned_data.csv', index_col='Unnamed: 0')
st.title('Some statistics')

with st.expander('View table per feature'):
    st.dataframe(df.describe())
st.subheader(f"Mean year founded: {round(df['founded_year'].mean())}")
st.subheader(f"Mean total funding: {'{:,}'.format(int(df['funding_total_usd'].mean()))} $")
st.subheader(f"Companies dates range from {int(min(df['founded_year']))} to {int(max(df['founded_year']))}")
st.subheader(f"Standard deviation of seed (first official investment round): {'{:,}'.format(round(df['seed'].std(), 3))} $")

st.title('Overview')

top_spheres = df['market'].value_counts()[:10]
fig = px.pie(values=top_spheres, names=top_spheres.index, title='Top 10 most expensive markets');
st.plotly_chart(fig)

fig = px.histogram(df['status'], title='Startups status', color_discrete_sequence=["mediumpurple"])
fig.update_xaxes(categoryorder='total ascending')
st.plotly_chart(fig)
st.write("Most startups are operational, and that's good!")

rounds = {}
for i in df.columns:
    if 'round_' in i:
        rounds[i] = df[i].mean()/10**6
fig = px.histogram(x=rounds.keys(), y=rounds.values(), labels={'y': 'Investment ($ million)', 'x': 'Rounds'}, color_discrete_sequence=["limegreen"]);
st.plotly_chart(fig)

fig = px.histogram(x=['angel', 'grant', 'venture'], 
                   y=[len(df[df['angel']!=0]),len(df[df['grant']!=0]), len(df[df['venture']!=0])], 
                   title='Startups investment sources',
                  color_discrete_sequence=["tomato"]);
fig.update_xaxes(categoryorder='total ascending')
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
fig = px.histogram(data_frame=top_companies, y='funding_total_usd', 
x='name', 
title='Top 25 most successfull companies',
labels={'x': 'Total funding', 'y': 'Company'}, 
color='founded_year');
fig.update_layout(xaxis_categoryorder = 'total descending')
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
st.write("Now it's clear that the more money you need for the startup, the more debts you'll need.")

st.markdown("""### Hypothesis: \nEvery year startups need more $$$ to raise. Is that true? 
Let's calculate total funding by year and make a line plot:""")
years = set(df['founded_year'])
fund_by_year = {}
for year in sorted(years):
    fund_by_year[year] = df[df['founded_year']==year]['funding_total_usd'].sum()/10**9
fig = px.line(x = fund_by_year.keys(), y=fund_by_year.values(), labels={'x': 'Year', 'y': 'Funding in $ billions'}, color_discrete_sequence=["darkorange"])
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
fig = px.icicle(
    df,
    path=[px.Constant("all"), 'quater'],
    values='seed',
    title='Seed values for various quaters')
st.plotly_chart(fig)
st.markdown("As we can see, the quater with biggest seed raised is **Q1**! However, we shall check, is that a really popular option? Maybe there's just an outlier there.")

df_by_q_sort = df.sort_values(by='quater')
num_seed = []
for q in df_by_q_sort['quater'].unique():
    num_seed.append(len(df_by_q_sort[(df_by_q_sort['quater']==q)&(df_by_q_sort['seed'] > 0)]))
fig = px.histogram(
    y=num_seed, 
    x=df_by_q_sort['quater'].unique(),
    title='Quater x Seed Number plot',
    color_discrete_sequence=["teal"],
    labels={'x': 'Quater the startup was founded at', 
    'y': 'Number of seeds raised'})
st.plotly_chart(fig)
st.markdown("""Yes! Q1 is also the most popular option among investors. 
That's the most popular time startups raise their first money. Thus, the hypothesis is **true**. Make sure you submit an application for seed funding in the 1st Quater.""")

