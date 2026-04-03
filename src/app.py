import dash
from dash import dcc, html, Input, Output
import plotly.express as px
import pandas as pd

# Load mental health data
mh = pd.read_csv('../csv/Mental health Depression disorder Data.csv')

# Load World Bank mobile data (skip first 4 rows which are metadata)
mobile = pd.read_csv('../csv/API_IT.CEL.SETS.P2_DS2_en_csv_v2_1834.csv', skiprows=4)

print(mh.columns.tolist())
print(mobile.columns.tolist())