"""
Author: Joshua Wallington
Description: Creates a dashboard using Dash and Plotly to visualize all the Apple Health Data in one place.
Credits: Some of the below code was sourceed from the following -
        https://github.com/plotly/dash-oil-and-gas-demo/blob/master/app.py (CSS Code)
        https://github.com/mganjoo/apple-health-exporter (ZIP to XML)

"""
#Dash components:
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State, ClientsideFunction
from dash.exceptions import PreventUpdate

#Data and Graphing
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import dash_resumable_upload

#Files
from zipfile import ZipFile
import zipfile
import io
import base64
import os
from src.options import Get_Drop_Choices, Explination_Table
from src.upload import health_xml_to_feather
from flask_caching import Cache

#STL
import time
import warnings
import copy

#Reqs
from datetime import datetime
import json


#Variables:
warnings.filterwarnings("ignore")
TIMEOUT = 60
app = dash.Dash(__name__)
cache = Cache(app.server, config={
    "CACHE_TYPE": "filesystem",
    "CACHE_DIR": "cache-directory"
})
Order = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
Attribute_Color = "#2BFEBE"
Heart_High_Color = "#E93329"
Heart_Low_Color = "#2ab0fe"
No_Data_Header_Message = "No Apple Health Data Uploaded"
config = {"displayModeBar": False}
df = "None"

layout = {
    "margin" :  {"l" : 15, "r" : 15, "t" : 25, "b" : 5},
    "hovermode" : "x",
    "plot_bgcolor" : "#242e3f",
    "paper_bgcolor" : "#2e3444",   
    "font_color" : "#1EAEDB",
    "legend" : {"font" : {"size" : 10}}, #, "orientation" : "h"
    "title" : "Graph Title",
    "xaxis": {"showgrid": False, "showline" : True, "linewidth" : 2, "linecolor" : "white", "mirror" : True},
    "yaxis" : {"showgrid" : True, "title" : {"text" : ""}, "showline" : True, "linewidth" : 2, "linecolor" : "white", "mirror" : True}}

No_Data_Graph_Message = {
    "layout": {"xaxis": {"visible": False},
    "yaxis": {"visible": False},
    "annotations": [
            {"text": "No Apple Health Data Uploaded",
                "xref": "paper",
                "yref": "paper",
                "showarrow": False,
                "font": {"size": 28}}
            ]
        }
    }


app.layout = html.Div(
    [
        html.Div(
            [
            html.Div(
                [
                html.H2("Apple Watch Data", id = "Dashboard-Title")], 
                className = "eleven columns"),
                dcc.Upload(
                    html.Button("Upload ZIP file", n_clicks = 0, id = "Upload-Button"),
                    className = "one column", accept = ".zip", id = "Upload-Component")],
                    id = "header", className = "row"),
        html.Div(
            [
                html.Div(
                    [
                    html.P(No_Data_Header_Message, className = "control_label", id = "Data-Information")
                    ],  
                    className = "pretty_container four columns", id = "Explination-Box"),
                html.Div(
                    [
                    html.P("Data Source Information", className = "control_label", id = "Source-Title"),
                    dbc.Select(
                            id = "Data-Dropdown",
                            options = Get_Drop_Choices(),
                            placeholder = "Select Data!",
                            value = "HKQuantityTypeIdentifierActiveEnergyBurned",
                            style = {"display": "inline-block"},
                            className = "dcc_control")
                        ],
                    className = "pretty_container four columns", id = "DataSource-Box"),
                
                html.Div(
                    [
                    html.P("Pick Date (Not Required)", className = "control_label", id = "Date-Title"),
                    dcc.DatePickerRange(
                        id = "DatePicker",
                        disabled = True,
                        calendar_orientation = "horizontal",
                        first_day_of_week = 1,
                        end_date_placeholder_text = "End Date",
                        min_date_allowed = None,
                        max_date_allowed = None,
                        start_date = None,
                        end_date = None,
                        display_format = "MMM Do, YYYY",
                        month_format = "MMMM, YYYY",
                        minimum_nights = 7, #Find way to make inactive until init
                        className = "dcc_control")], 
                        className = "pretty_container four columns", id = "Date-Box")
                    ],className="row"),

        html.Div(
            [
            html.Div(
                [
                dcc.Graph(id = "ActiveEnergyGraph", figure = No_Data_Graph_Message, config = config)
            ], 
            className = "pretty_container six columns"),
            html.Div(
                [
                dcc.Graph(id = "BasalEnergyGraph", figure = No_Data_Graph_Message, config = config)
            ], 
            className = "pretty_container six columns")
        ], className = "row"),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id = "ExerciseTimeGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className="pretty_container six columns",
                ),
                html.Div(
                    [
                        dcc.Graph(id = "StandTimeGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className="pretty_container six columns"),
            ],
            className = "row"),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id = "StepCountGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className = "pretty_container six columns",
                ),
                html.Div(
                    [
                        dcc.Graph(id = "FlightsClimbedGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className = "pretty_container six columns",
                ),
            ],
            className = "row"
        ),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id = "DistanceWalkingRunningGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className = "pretty_container six columns",
                ),
                html.Div(
                    [
                        dcc.Graph(id = "EnvironmentalAudioExposureGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className = "pretty_container six columns",
                ),
            ],
            className = "row"
        ),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id = "HeartRateGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className = "pretty_container six columns",
                ),
                html.Div(
                    [
                        dcc.Graph(id = "WalkingHeartRateAverageGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className = "pretty_container six columns",
                ),
            ],
            className = "row"
        ),

        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id = "RestingHeartRateAverageGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className = "pretty_container six columns",
                ),
                html.Div(
                    [
                        dcc.Graph(id = "HeartRateVariabilityGraph", figure = No_Data_Graph_Message, config = config)
                    ],
                    className="pretty_container six columns",
                ),
            ],
            className = "row"
        ),
    ], 
    id = "mainContainer",
    style={"display": "flex", "flex-direction": "column"}) # End of HTML Components




@cache.memoize(timeout=TIMEOUT)
def query_data():
    return "Data/data.feather"

def dataframe():
    return pd.read_feather(query_data())

@app.callback(Output("Explination-Box", "children"),
                [Input("Data-Dropdown", "value")])
def Expliantions(value):
    if value is not None:
        return Explination_Table[value]["Explination"]

@app.callback(Output("DatePicker", "disabled"),
             Output("DatePicker", "start_date"),
             Output("DatePicker", "end_date"),
             Output("DatePicker", "min_date_allowed"),
             Output("DatePicker", "max_date_allowed"),
            [Input("Upload-Button", "n_clicks")],
            [Input("Upload-Component", "contents")],
            [State("Upload-Component", "filename")])
def update_output(n_clicks, list_of_contents, list_of_names):
    if list_of_contents is None or list_of_names is None:
        raise PreventUpdate #Only fire when ready
    elif n_clicks > 0:
            content_type, content_string = list_of_contents.split(",")
            content_decoded = base64.b64decode(content_string)
            zip_str = io.BytesIO(content_decoded)
            zip_obj = ZipFile(zip_str, "r")
            df = health_xml_to_feather(zip_str, "data.feather", remove_zip=True)

            List = df["type"].unique().tolist()
            Dates = df["startDate"].dt.date.unique()
            First_Date = Dates.min()
            Last_Date = Dates.max()
            return False, First_Date, Last_Date, First_Date, Last_Date

@app.callback(Output("ActiveEnergyGraph", "figure"),
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def ActiveEnergyGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierActiveEnergyBurned"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    By_Day = Specified_Dates.groupby(["startDate"])["value"].sum().reset_index(name = "value")
    By_Month = Specified_Dates.groupby(["month"])["value"].sum().reset_index(name = "value")
    By_DayofWeek = Specified_Dates.groupby(["DayofWeek"])["value"].sum().reindex(Order)
    Day_Range = By_Day.startDate.unique().tolist()
    Month_Range = By_Month.month.unique().tolist()
    New_Range = By_DayofWeek.index.unique().tolist()

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Active Energy Burned Per Day from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Calories"

    Day = go.Scatter(
        x = By_Day.startDate,
        y = By_Day.value,
        name = "Calories",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Attribute_Color,
        visible = True)

    Month = go.Bar(
        x = By_Month.month,
        y = By_Month.value,
        name = "Calories",
        marker_color = Attribute_Color,
        visible = False)

    Weekday = go.Bar(
        x = By_DayofWeek.index,
        y = By_DayofWeek.values,
        name = "Calories",
        marker_color = Attribute_Color,
        visible = False)

    Graphs = [Day, Month, Weekday]

    updatemenus = [
        {"active" : 0, 
        "direction" : "down", 
        "pad" : {"r" : 4, "t" : 0}, 
        "x" : 0.93,
        "y" : 1.2,  
        "showactive" : True,
        "buttons" : [ 
            {"label" : "Total Per Day", "method" : "update", "args" : [
                {"visible" : [True, False, False], "x" : [Day_Range]},
                {"title" : f"Active Energy Burned Per Day from {start_date} to {end_date}", "yaxis.title.text" : "Calories"}]
            },

            {"label" : "Total Per Month", "method" : "update", "args" : [
                {"visible" : [False, True, False], "x" : [Month_Range]},
                {"title" : f"Total Active Energy Burned Per Month from {start_date} to {end_date}", "yaxis.title.text" : "Calories"}]
            },
            
            {"label" : "Total Per Weekday", "method" : "update", "args" : [
                {"visible" : [False, False, True], "x" : [New_Range]},
                {"title" : f"Total Active Energy Burned Per Weekday from {start_date} to {end_date}", "yaxis.title.text" : "Calories", "xaxis.dtick" : "M1", "xaxis.showgrid" : True}
            ]}]
        }]


    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, updatemenus = updatemenus)
    
    return Figure

@app.callback(Output("BasalEnergyGraph", "figure"),
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def BasalEnergyGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierBasalEnergyBurned"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    By_Day = Specified_Dates.groupby(["startDate"])["value"].sum().reset_index(name= "value")
    By_Month = Specified_Dates.groupby(["month"])["value"].sum().reset_index(name= "value")
    By_DayofWeek = Specified_Dates.groupby(["DayofWeek"])["value"].sum().reindex(Order)
    Day_Range = By_Day.startDate.unique().tolist()
    Month_Range = By_Month.month.unique().tolist()
    New_Range = By_DayofWeek.index.unique().tolist()

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Total Basal Energy Burned Per Day from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Calories"

    Day = go.Scatter(
        x = By_Day.startDate,
        y = By_Day.value,
        name = "Calories",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Attribute_Color,
        visible = True)

    Month = go.Bar(
        x = By_Month.month,
        y = By_Month.value,
        name = "Calories",
        marker_color = Attribute_Color,
        visible = False)

    Weekday = go.Bar(
        x = By_DayofWeek.index,
        y = By_DayofWeek.values,
        name = "Calories",
        marker_color = Attribute_Color,
        visible = False)

    Graphs = [Day, Month, Weekday]

    updatemenus = [
        {"active" : 0, 
        "direction" : "down", 
        "pad" : {"r" : 4, "t" : 0}, 
        "x" : 0.93,
        "y" : 1.2,   
        "showactive" : True,
        "buttons" : [
            {"label" : "Total Per Day", "method" : "update", "args" : [
                {"visible" : [True, False, False], "x" : [Day_Range]},
                {"title" : f"Total Basal Energy Burned Per Day from {start_date} to {end_date}", "yaxis.title.text" : "Calories"}]
            },

            {"label" : "Total Per Month", "method" : "update", "args" : [
                {"visible" : [False, True, False], "x" : [Month_Range]},
                {"title" : f"Total Basal Energy Burned Per Month from {start_date} to {end_date}", "yaxis.title.text" : "Calories"}]
            },
            
            {"label" : "Total Per Weekday", "method" : "update", "args" : [
                {"visible" : [False, False, True], "x" : [New_Range]},
                {"title" : f"Total Basal Energy Burned Per Weekday from {start_date} to {end_date}", "yaxis.title.text" : "Calories", "xaxis.dtick" : "M1", "xaxis.showgrid" : True}
            ]}]
        }]


    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, updatemenus = updatemenus)
    
    return Figure

@app.callback(Output("ExerciseTimeGraph", "figure"),
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def BasalEnergyGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierAppleExerciseTime"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    By_Day = Specified_Dates.groupby(["startDate"])["value"].sum().reset_index(name= "value")
    By_Month = Specified_Dates.groupby(["month"])["value"].sum().reset_index(name= "value")
    By_DayofWeek = Specified_Dates.groupby(["DayofWeek"])["value"].sum().reindex(Order)
    Day_Range = By_Day.startDate.unique().tolist()
    Month_Range = By_Month.month.unique().tolist()
    New_Range = By_DayofWeek.index.unique().tolist()

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Apple Excersise Minutes Per Day from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Minutes"

    Day = go.Scatter(
        x = By_Day.startDate,
        y = By_Day.value,
        name = "Minutes",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Attribute_Color,
        visible = True)

    Month = go.Bar(
        x = By_Month.month,
        y = By_Month.value,
        name = "Minutes",
        marker_color = Attribute_Color,
        visible = False)

    Weekday = go.Bar(
        x = By_DayofWeek.index,
        y = By_DayofWeek.values,
        name = "Minutes",
        marker_color = Attribute_Color,
        visible = False)

    Graphs = [Day, Month, Weekday]

    updatemenus = [
        {"active" : 0, 
        "direction" : "down", 
        "pad" : {"r" : 4, "t" : 0}, 
        "x" : 0.93,
        "y" : 1.2,    
        "showactive" : True,
        "buttons" : [
            {"label" : "Total Per Day", "method" : "update", "args" : [
                {"visible" : [True, False, False], "x" : [Day_Range]},
                {"title" : f"Total Apple Excersise Minutes Per Day from {start_date} to {end_date}", "yaxis.title.text" : "Minutes"}]
            },

            {"label" : "Total Per Month", "method" : "update", "args" : [
                {"visible" : [False, True, False], "x" : [Month_Range]},
                {"title" : f"Total Apple Excersise Minutes Per Month from {start_date} to {end_date}", "yaxis.title.text" : "Minutes"}]
            },
            
            {"label" : "Total Per Weekday", "method" : "update", "args" : [
                {"visible" : [False, False, True], "x" : [New_Range]},
                {"title" : f"Total Apple Excersise Minutes Per Weekday from {start_date} to {end_date}", "yaxis.title.text" : "Minutes", "xaxis.dtick" : "M1", "xaxis.showgrid" : True}
            ]}]
        }]


    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, updatemenus = updatemenus)
    
    return Figure

@app.callback(Output("StandTimeGraph", "figure"),
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def StandTimeGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierAppleStandTime"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    By_Day = Specified_Dates.groupby(["startDate"])["value"].sum().reset_index(name= "value")
    By_Month = Specified_Dates.groupby(["month"])["value"].sum().reset_index(name= "value")
    By_DayofWeek = Specified_Dates.groupby(["DayofWeek"])["value"].sum().reindex(Order)
    Day_Range = By_Day.startDate.unique().tolist()
    Month_Range = By_Month.month.unique().tolist()
    New_Range = By_DayofWeek.index.unique().tolist()

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Total Stand Time Per Day from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Minutes"

    Day = go.Scatter(
        x = By_Day.startDate,
        y = By_Day.value,
        name = "Minutes",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Attribute_Color,
        visible = True)

    Month = go.Bar(
        x = By_Month.month,
        y = By_Month.value,
        name = "Minutes",
        marker_color = Attribute_Color,
        visible = False)

    Weekday = go.Bar(
        x = By_DayofWeek.index,
        y = By_DayofWeek.values,
        name = "Minutes",
        marker_color = Attribute_Color,
        visible = False)

    Graphs = [Day, Month, Weekday]

    updatemenus = [
        {"active" : 0, 
        "direction" : "down", 
        "pad" : {"r" : 4, "t" : 0}, 
        "x" : 0.93, 
        "y" : 1.2,  
        "showactive" : True,
        "buttons" : [
            {"label" : "Total Per Day", "method" : "update", "args" : [
                {"visible" : [True, False, False], "x" : [Day_Range]},
                {"title" : f"Total Stand Time Per Day from {start_date} to {end_date}", "yaxis.title.text" : "Minutes"}]
            },

            {"label" : "Total Per Month", "method" : "update", "args" : [
                {"visible" : [False, True, False], "x" : [Month_Range]},
                {"title" : f"Total Stand Time Per Month from {start_date} to {end_date}", "yaxis.title.text" : "Minutes"}]
            },
            
            {"label" : "Total Per Weekday", "method" : "update", "args" : [
                {"visible" : [False, False, True], "x" : [New_Range]},
                {"title" : f"Total Stand Time Per Weekday from {start_date} to {end_date}", "yaxis.title.text" : "Minutes", "xaxis.dtick" : "M1", "xaxis.showgrid" : True}
            ]}]
        }]


    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, updatemenus = updatemenus)
    
    return Figure

@app.callback(Output("StepCountGraph", "figure"),
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def StepCountGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierStepCount"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    By_Day = Specified_Dates.groupby(["startDate"])["value"].sum().reset_index(name= "value")
    By_Month = Specified_Dates.groupby(["month"])["value"].sum().reset_index(name= "value")
    By_DayofWeek = Specified_Dates.groupby(["DayofWeek"])["value"].sum().reindex(Order)
    Day_Range = By_Day.startDate.unique().tolist()
    Month_Range = By_Month.month.unique().tolist()
    New_Range = By_DayofWeek.index.unique().tolist()

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Total Step Count Per Day from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Minutes"

    Day = go.Scatter(
        x = By_Day.startDate,
        y = By_Day.value,
        name = "Steps",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Attribute_Color,
        visible = True)

    Month = go.Bar(
        x = By_Month.month,
        y = By_Month.value,
        name = "Steps",
        marker_color = Attribute_Color,
        visible = False)

    Weekday = go.Bar(
        x = By_DayofWeek.index,
        y = By_DayofWeek.values,
        name = "Steps",
        marker_color = Attribute_Color,
        visible = False)

    Graphs = [Day, Month, Weekday]

    updatemenus = [
        {"active" : 0, 
        "direction" : "down", 
        "pad" : {"r" : 4, "t" : 0}, 
        "x" : 0.93, #"xanchor" : "left", 
        "y" : 1.2,  #"yanchor" : "top",  
        "showactive" : True,
        "buttons" : [
            {"label" : "Total Per Day", "method" : "update", "args" : [
                {"visible" : [True, False, False], "x" : [Day_Range]},
                {"title" : f"Total Step Count Per Day from {start_date} to {end_date}", "yaxis.title.text" : "Count"}]
            },

            {"label" : "Total Per Month", "method" : "update", "args" : [
                {"visible" : [False, True, False], "x" : [Month_Range]},
                {"title" : f"Total Step Count Per Month from {start_date} to {end_date}", "yaxis.title.text" : "Count"}]
            },
            
            {"label" : "Total Per Weekday", "method" : "update", "args" : [
                {"visible" : [False, False, True], "x" : [New_Range]},
                {"title" : f"Total Step Count Per Weekday from {start_date} to {end_date}", "yaxis.title.text" : "Count", "xaxis.dtick" : "M1", "xaxis.showgrid" : True}
            ]}]
        }]


    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, updatemenus = updatemenus)
    
    return Figure

@app.callback(Output("FlightsClimbedGraph", "figure"),
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def FlightsClimbedGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierFlightsClimbed"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    By_Day = Specified_Dates.groupby(["startDate"])["value"].sum().reset_index(name= "value")
    By_Month = Specified_Dates.groupby(["month"])["value"].sum().reset_index(name= "value")
    By_DayofWeek = Specified_Dates.groupby(["DayofWeek"])["value"].sum().reindex(Order)
    Day_Range = By_Day.startDate.unique().tolist()
    Month_Range = By_Month.month.unique().tolist()
    New_Range = By_DayofWeek.index.unique().tolist()

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Total Flights Climbed Per Day from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Flights"

    Day = go.Scatter(
        x = By_Day.startDate,
        y = By_Day.value,
        name = "Flights",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Attribute_Color,
        visible = True)

    Month = go.Bar(
        x = By_Month.month,
        y = By_Month.value,
        name = "Flights",
        marker_color = Attribute_Color,
        visible = False)

    Weekday = go.Bar(
        x = By_DayofWeek.index,
        y = By_DayofWeek.values,
        name = "Flights",
        marker_color = Attribute_Color,
        visible = False)

    Graphs = [Day, Month, Weekday]

    updatemenus = [
        {"active" : 0, 
        "direction" : "down", 
        "pad" : {"r" : 4, "t" : 0}, 
        "x" : 0.93, 
        "y" : 1.2,  
        "showactive" : True,
        "buttons" : [
            {"label" : "Total Per Day", "method" : "update", "args" : [
                {"visible" : [True, False, False], "x" : [Day_Range]},
                {"title" : f"Total Flights Climbed Per Day from {start_date} to {end_date}", "yaxis.title.text" : "Flights"}]
            },

            {"label" : "Total Per Month", "method" : "update", "args" : [
                {"visible" : [False, True, False], "x" : [Month_Range]},
                {"title" : f"Total Flights Climbed Per Month from {start_date} to {end_date}", "yaxis.title.text" : "Flights"}]
            },
            
            {"label" : "Total Per Weekday", "method" : "update", "args" : [
                {"visible" : [False, False, True], "x" : [New_Range]},
                {"title" : f"Total Flights Climbed Per Weekday from {start_date} to {end_date}", "yaxis.title.text" : "Flights", "xaxis.dtick" : "M1", "xaxis.showgrid" : True}
            ]}]
        }]


    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, updatemenus = updatemenus)
    
    return Figure

@app.callback(Output("DistanceWalkingRunningGraph", "figure"), 
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])
def DistanceWalkingRunningGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierDistanceWalkingRunning"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    By_Day = Specified_Dates.groupby(["startDate"])["value"].sum().reset_index(name= "value")
    By_Month = Specified_Dates.groupby(["month"])["value"].sum().reset_index(name= "value")
    By_DayofWeek = Specified_Dates.groupby(["DayofWeek"])["value"].sum().reindex(Order)
    Day_Range = By_Day.startDate.unique().tolist()
    Month_Range = By_Month.month.unique().tolist()
    New_Range = By_DayofWeek.index.unique().tolist()

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Total Distance Moved Per Day from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Miles"

    Day = go.Scatter(
        x = By_Day.startDate,
        y = By_Day.value,
        name = "Miles",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Attribute_Color,
        visible = True)

    Month = go.Bar(
        x = By_Month.month,
        y = By_Month.value,
        name = "Miles",
        marker_color = Attribute_Color,
        visible = False)

    Weekday = go.Bar(
        x = By_DayofWeek.index,
        y = By_DayofWeek.values,
        name = "Miles",
        marker_color = Attribute_Color,
        visible = False)

    Graphs = [Day, Month, Weekday]

    updatemenus = [
        {"active" : 0, 
        "direction" : "down", 
        "pad" : {"r" : 4, "t" : 0}, 
        "x" : 0.93,
        "y" : 1.2,   
        "showactive" : True,
        "buttons" : [
            {"label" : "Total Per Day", "method" : "update", "args" : [
                {"visible" : [True, False, False], "x" : [Day_Range]},
                {"title" : f"Total Miles Moved Per Day from {start_date} to {end_date}", "yaxis.title.text" : "Miles"}]
            },

            {"label" : "Total Per Month", "method" : "update", "args" : [
                {"visible" : [False, True, False], "x" : [Month_Range]},
                {"title" : f"Total Distance Moved Per Month from {start_date} to {end_date}", "yaxis.title.text" : "Miles"}]
            },
            
            {"label" : "Total Per Weekday", "method" : "update", "args" : [
                {"visible" : [False, False, True], "x" : [New_Range]},
                {"title" : f"Total Distance Moved Per Weekday from {start_date} to {end_date}", "yaxis.title.text" : "Miles", "xaxis.dtick" : "M1", "xaxis.showgrid" : True}
            ]}]
        }]


    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, updatemenus = updatemenus)
    
    return Figure

@app.callback(Output("EnvironmentalAudioExposureGraph", "figure"), 
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def EnvironmentalAudioExposureGraph(start_date, end_date):

    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierEnvironmentalAudioExposure"]
    if df.empty:
        Message = copy.deepcopy(No_Data_Graph_Message)
        Message["layout"]["annotations"][0]["text"] = "Watch does not record Enviornmental Audio Exposure"
        return go.Figure(data = Message)
    else:
        df["startDate"] = df["startDate"].dt.date

        Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
        Specified_Dates = df.loc[Date_Range]

        By_Day = Specified_Dates.groupby(["startDate"])["value"].mean().reset_index(name= "value")
        By_Month = Specified_Dates.groupby(["month"])["value"].mean().reset_index(name= "value")
        By_DayofWeek = Specified_Dates.groupby(["DayofWeek"])["value"].mean().reindex(Order)
        Day_Range = By_Day.startDate.unique().tolist()
        Month_Range = By_Month.month.unique().tolist()
        New_Range = By_DayofWeek.index.unique().tolist()

        Graph_Layout = copy.deepcopy(layout)

        Graph_Layout["title"] = f"Average Decible Exposure Per Day from {start_date} to {end_date}"
        Graph_Layout["yaxis"]["title"]["text"] = "Decibles"

        Day = go.Scatter(
            x = By_Day.startDate,
            y = By_Day.value,
            name = "Decibles",
            fill = "tonexty",
            mode = "lines+markers",
            marker_color = Attribute_Color,
            visible = True)

        Month = go.Bar(
            x = By_Month.month,
            y = By_Month.value,
            name = "Decibles",
            marker_color = Attribute_Color,
            visible = False)

        Weekday = go.Bar(
            x = By_DayofWeek.index,
            y = By_DayofWeek.values,
            name = "Decibles",
            marker_color = Attribute_Color,
            visible = False)

        Graphs = [Day, Month, Weekday]

        updatemenus = [
            {"active" : 0, 
            "direction" : "down", 
            "pad" : {"r" : 4, "t" : 0}, 
            "x" : 0.93,
            "y" : 1.2,
            "showactive" : True,
            "buttons" : [
                {"label" : "Average Per Day", "method" : "update", "args" : [
                    {"visible" : [True, False, False], "x" : [Day_Range]},
                    {"title" : f"Average Decibles Exposure Per Day from {start_date} to {end_date}", "yaxis.title.text" : "Decibles"}]
                },

                {"label" : "Average Per Month", "method" : "update", "args" : [
                    {"visible" : [False, True, False], "x" : [Month_Range]},
                    {"title" : f"Average Decible Exposure Per Month from {start_date} to {end_date}", "yaxis.title.text" : "Decibles"}]
                },
                
                {"label" : "Average Per Weekday", "method" : "update", "args" : [
                    {"visible" : [False, False, True], "x" : [New_Range]},
                    {"title" : f"Average Decible Exposure Per Weekday from {start_date} to {end_date}", "yaxis.title.text" : "Decibles", "xaxis.dtick" : "M1", "xaxis.showgrid" : True}
                ]}]
            }]


        Figure = go.Figure(data = Graphs)
        Figure.update_layout(Graph_Layout, updatemenus = updatemenus)
        
        return Figure

@app.callback(Output("HeartRateGraph", "figure"), 
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def HeartRateGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierHeartRate"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    By_Day_High = Specified_Dates.groupby(["startDate"])["value"].max().reset_index(name = "value")
    By_Day_Low = Specified_Dates.groupby(["startDate"])["value"].min().reset_index(name = "value")

    # By_Month = df.groupby(["month"])["value"].reset_index(name= "value")
    By_DayofWeek = df.groupby(["DayofWeek"])["value"].sum().reindex(Order)
    Day_Range = By_Day_High.startDate.unique().tolist()
    Month_Range = df["month"].unique().tolist()
    New_Range = By_DayofWeek.index.unique().tolist()

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Highest and Lowest Heart Rate from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Count/Min"
    #[By_Day_High.value, By_Day_Low.value],
    Day_High = go.Scatter(
        x = By_Day_High.startDate,
        y = By_Day_High.value,
        name = "CPM",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Heart_High_Color,
        visible = True)

    Day_Low = go.Scatter(
        x = By_Day_Low.startDate,
        y = By_Day_Low.value,
        name = "CPM",
        fill = "tozeroy",
        mode = "lines+markers",
        marker_color = Heart_Low_Color,
        visible = True)

    Month = go.Scattergl(
        x = Specified_Dates.month,
        y = Specified_Dates.values,
        name = "Miles",
        marker_color = Attribute_Color,
        visible = False)

    Weekday = go.Bar(
        x = By_DayofWeek.index,
        y = By_DayofWeek.values,
        name = "Miles",
        marker_color = Attribute_Color,
        visible = False)

    Graphs = [Day_High,Day_Low]

    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, showlegend = False)
    
    return Figure

@app.callback(Output("WalkingHeartRateAverageGraph", "figure"), 
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def WalkingHeartRateAverageGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierWalkingHeartRateAverage"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Walking Heart Rate Average from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Count/Min"

    Data = go.Scatter(
        x = Specified_Dates.startDate,
        y = Specified_Dates.value,
        name = "CPM",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Heart_High_Color,
        visible = True)

    Graphs = [Data]

    Figure = go.Figure(data = Graphs)
    Figure.update_layout(Graph_Layout, showlegend = False)
    
    return Figure

@app.callback(Output("RestingHeartRateAverageGraph", "figure"), 
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def RestingHeartRateAverageGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierRestingHeartRate"]
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Resting Heart Rate from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "Count/Min"

    Data = go.Scatter(
        x = Specified_Dates.startDate,
        y = Specified_Dates.value,
        name = "Count/Min",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Heart_High_Color)


    Figure = go.Figure(data = Data)
    Figure.update_layout(Graph_Layout)
    
    return Figure

@app.callback(Output("HeartRateVariabilityGraph", "figure"), 
              [Input("DatePicker", "start_date"),
              Input("DatePicker", "end_date")])  
def HeartRateVariabilityGraph(start_date, end_date):
    start_date = datetime.strptime(start_date, "%Y-%m-%d").strftime("%b %d, %Y")
    end_date = datetime.strptime(end_date, "%Y-%m-%d").strftime("%b %d, %Y")

    df = dataframe()
    df = df[df["type"] == "HKQuantityTypeIdentifierHeartRateVariabilitySDNN"] 
    df["startDate"] = df["startDate"].dt.date

    Date_Range = (df["startDate"] > pd.to_datetime(start_date)) & (df["startDate"] <= pd.to_datetime(end_date))
    Specified_Dates = df.loc[Date_Range]

    Average_Per_Day = Specified_Dates.groupby(["startDate"])["value"].mean().reset_index(name = "value")

    Graph_Layout = copy.deepcopy(layout)

    Graph_Layout["title"] = f"Heart Rate Variability from {start_date} to {end_date}"
    Graph_Layout["yaxis"]["title"]["text"] = "ms"
    Data = go.Scatter(
        x = Average_Per_Day.startDate,
        y = Average_Per_Day.value,
        name = "Miliseconds",
        fill = "tonexty",
        mode = "lines+markers",
        marker_color = Heart_High_Color)

    Figure = go.Figure(data = Data)
    Figure.update_layout(Graph_Layout)
    
    return Figure

if __name__ == "__main__":
    app.scripts.config.serve_locally = True
    app.css.config.serve_locally = True
    app.run_server(debug = True)
    dash_resumable_upload(app.server)
    
