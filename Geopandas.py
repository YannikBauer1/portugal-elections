import geopandas as gpd
import pandas as pd
from bokeh.models import GeoJSONDataSource, HoverTool, TapTool, Slider
from bokeh.plotting import figure, output_file, show
from bokeh.palettes import Spectral10
from bokeh.transform import factor_cmap
from bokeh.io import curdoc, output_notebook
from bokeh.layouts import widgetbox, row, column
#-------------------------------Editar os dados------------------------------------------------------------------------
mapa_Portugal=gpd.read_file("distritos(2)")
dados=pd.read_csv("resultados-legislativas.csv")

dados=dados[["nome","data","partido","num_votos","mandatos"]]   #tirar as colunas código, tipo e perc_votos

dados["nome"].replace({"Corvo":"Açores","São Jorge":"Açores","São Miguel":"Açores"}, inplace=True)   #juntar Corvo,Sao Jorge e Sao Miguel para Acores
dados=dados.groupby(["nome","data","partido"])[["num_votos","mandatos"]].sum().reset_index()
dados=dados.sort_values(["data","nome"])

dados["data"]=dados["data"].apply(lambda x:int(x[:4]))

#for i in range(len(dados.values)):               #tirar Mocambique e Macau dos dados
#    if "Moçambique" in dados.values[len(dados.values)-1-i] or "Macau" in dados.values[len(dados.values)-1-i]:
#        dados.drop([len(dados.values)-1-i],axis=0,inplace=True)  ####################################################Ver se funciona####################

datas=dados.T.values[1]            #separar os dados em Dataframes para cada data
datas=[0]+[i for i in range(1,len(datas)) if datas[i]!=datas[i-1]]+[len(datas)-1]
dataframes=[dados[datas[i-1]:datas[i]] for i in range(1,len(datas))]

dataframes_editados=[i.sort_values(["num_votos"],ascending=False).drop_duplicates(["nome"]) for i in dataframes]  #os dataframes sorted e só com o partido mais votado

mais_votados=[i[["partido"]].T.values for i in dataframes_editados]
l=[]
for i in range(len(mais_votados)):
   for j in range(len(mais_votados[i][0])):
        l.append(mais_votados[i][0][j])
mais_votados=pd.DataFrame(l).drop_duplicates().T.values[0]
mais_votados=[i for i in mais_votados]

d=dados["data"]
print(d)
#farben für partei zeigen
#drehrad zum jahr auswählen
def only_winners(dataframe):
    return dataframe.sort_values(["num_votos"],ascending=False).drop_duplicates(["nome"])

def json_data(selectedYear):
    dados_selectedYear = dados[dados["data"] == selectedYear]
    dados_selectedYear = only_winners(dados_selectedYear)
    merged = mapa_Portugal.merge(dados_selectedYear, left_on="NAME_1", right_on="nome")
    json=merged.to_json()
    return json


pop_states = mapa_Portugal.merge(dataframes_editados[0],left_on="NAME_1",right_on="nome")
geosource = GeoJSONDataSource(geojson =pop_states.to_json())
#output_file("index.html")


p = figure(title = 'Portugal Map',
            toolbar_location = 'above',
            tools = "pan, wheel_zoom, box_zoom, reset",
            )
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
states = p.patches('xs','ys',
                   source = geosource,
                   line_color = "gray",
                   line_width = 1,
                   fill_alpha = 1,
                   fill_color = factor_cmap("partido", palette = Spectral10, factors=mais_votados),
                   )

p.add_tools(HoverTool(renderers = [states],
                      tooltips = [('nome','@nome'),
                                ('num_votos','@num_votos'),("partido","@partido")]))



p.add_tools(TapTool())
def update_plot(attr, old, new):
    yr=slider.value
    geosource.geojson=json_data(yr)
    print("asdfasdf")
    p.title.text="Eleicoes Portugal in %d" %yr

slider=Slider(title="Year", start=1975, end=2011, step=1, value=1975)
slider.on_change("value", update_plot)
layout=column(p, widgetbox(slider))


from bokeh.layouts import widgetbox
from bokeh.models import Slider
from bokeh.io import curdoc

slider_w=Slider(start=0, end=100, step=10, title="Slider")
slider_layout=widgetbox(slider_w)
curdoc().add_root(slider_layout)
#curdoc().add_root(layout)

#show(layout)