import streamlit as st  #streamlit will host our app
import pandas as pd #for data manipulation
import numpy as np
import pydeck as pdk #pydeck is used to build interactive 3d charts
import plotly.express as px #for plotting graphs from any lib: matplotlib, seaborn


#"""Adding a path for our Dataset"""
data_path = (
'C:\\Users\\acer\\Desktop\\Project_Dir\\StreamLit Apps\\Motor_Vehicle_Collisions_-_Crashes.csv'
)

#st.title('string') = sets the main title for the app
#st.markdown('str') = works pretty much same as jupyter's markdown feature

st.title('Motor Vehicle Collisions in New York City')
st.markdown("## This application is a Streamlit dashboard that can be used"
" to analyze motor vehicle collisions in NYC 🗽 💥🚗 ")

#@st.cache(persist = bool) = helps in caching and quick rendering of a heavy task;
#HERE  we used the motor vehicle csv which had more than a million rows

@st.cache(persist = True)
def load_data(nrows):
    df = pd.read_csv(data_path, nrows=nrows, parse_dates=[['CRASH_DATE', 'CRASH_TIME']])
    df.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace = True)
    lower_col = lambda x: str(x).lower()
    df.rename(lower_col, axis = 'columns', inplace = True)
    df.rename(columns={'crash_date_crash_time': 'date/time'}, inplace = True)
    return df


df = load_data(nrows = 100000)
data = df.copy()

#Creating a Header for our app:

st.header("Where are the most people injured in NYC")

#calculating the injured persons --- 0 to 19 
injured_set = st.slider("Number of persons injured in vehicle collisions", 0, 19)


st.map(df.query(f"injured_persons >= {injured_set}")[['latitude', 'longitude']].dropna(how = 'any'))

st.header("How many collisions occur during a given time of day")
hourbox = st.slider("Hour to look at", 0, 23)
df = df[df['date/time'].dt.hour == hourbox]

st.markdown("Vehicle Collisions between %i:00 and %i:00" % (hourbox, (hourbox+1) % 24))
midpoint = [np.average(df['latitude']), np.average(df['longitude'])]
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
        "latitude": midpoint[0],
        "longitude": midpoint[1],
        "zoom": 11,
        "pitch": 50,
    },
    layers=[
        pdk.Layer(
        "HexagonLayer",
        data=data[['date/time', 'latitude', 'longitude']],
        get_position=["longitude", "latitude"],
        auto_highlight=True,
        radius=100,
        extruded=True,
        pickable=True,
        elevation_scale=4,
        elevation_range=[0, 1000],
        ),
    ],
))

st.subheader("Breakdown by  minute between %i:00 and %i:00" % (hourbox, (hourbox+1) % 24))
filtered = df[(df['date/time'].dt.hour >= hourbox)& (df['date/time'].dt.hour < (hourbox+1))]
hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range=(0,60))[0]
char_df = pd.DataFrame({'minute':range(60), 'crashes':hist})
fig = px.bar(char_df, x='minute', y='crashes', hover_data = ['minute', 'crashes'])
st.write(fig)

st.header("Top 5 Dangerous streets affected type")
selector = st.selectbox("Affected types of people", ['Pedestrians', 'Cyclists', 'Motorists'])

if selector == 'Pedestrians':
    st.write(data.query('injured_pedestrians >= 1')[['on_street_name', 'injured_pedestrians']].sort_values(by = ['injured_pedestrians'], ascending = False).dropna(how='any')[:5])
elif selector == 'Cyclists':
    st.write(data.query('injured_cyclists >= 1')[['on_street_name', 'injured_cyclists']].sort_values(by = ['injured_cyclists'], ascending = False).dropna(how='any')[:5])

elif selector == 'Motorists':
    st.write(data.query('injured_motorists >= 1')[['on_street_name', 'injured_motorists']].sort_values(by = ['injured_motorists'], ascending = False).dropna(how='any')[:5])


if st.checkbox("Show Raw data", False):
    st.subheader('Raw Data')
    st.write(df)




"""Pending tasks: Comment Code for better understanding"""