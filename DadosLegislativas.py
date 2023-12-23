########################################################################################################################
#---------------------------------------------DadosLegislativas--------------------------------------------------------#
########################################################################################################################

import geopandas as gpd
import pandas as pd
import math
from bokeh.models import GeoJSONDataSource, HoverTool, TapTool, Slider, ColumnDataSource
from bokeh.plotting import figure
from bokeh.transform import factor_cmap, cumsum
from bokeh.io import curdoc
from bokeh.layouts import column, row

#-------------------------------import os dados------------------------------------------------------------------------
portugal_map=gpd.read_file("distritos")
data=pd.read_csv("resultados-legislativas.csv")

#-------------------------editar os dados------------------------------------------------------------------------------
data=data[["nome","data","partido","num_votos","mandatos"]]   #tirar as colunas código, tipo e perc_votos

data["nome"].replace({"Corvo":"Açores","São Jorge":"Açores","São Miguel":"Açores"}, inplace=True)   #juntar os Acores
data=data.groupby(["nome","data","partido"])[["num_votos","mandatos"]].sum().reset_index()
data=data.sort_values(["data","nome"])

data["data"]=data["data"].apply(lambda x:int(x[:4]))  #no data fica só o ano

#------------------------------------lista importantes de dados---------------------------------------------------------
def only_winners(dataframe):   #funcao que recebe uma dataframe e return uma dataframe só com os vencedores dos eleicoes
    return dataframe.sort_values(["num_votos"],ascending=False).drop_duplicates(["nome"])
def only_date(dataframe, yr):   #funcao dá um dataframe só com os dados do ano
    return dataframe[dataframe["data"] == yr]

dates=data[["data"]].drop_duplicates(["data"]).T.values[0]  #os datas dos eleicoes

winner_dataframes=[only_date(data,yr) for yr in dates]    #lista de dataframes da eleicao de cada ano
winner_dataframes=[only_winners(i) for i in winner_dataframes]    #lista de dataframes de cada ano com os vencedores

winner_partys=[i[["partido"]].T.values[0] for i in winner_dataframes]  #lista dos partidos mais votados
winner_partys=[item for sublist in winner_partys for item in sublist]
winner_partys=pd.DataFrame(winner_partys).drop_duplicates().T.values[0]

partys=data[["partido"]].drop_duplicates().T.values[0]  #todos os partidos

cmap={"PS": "blue",
      "PPD":"blueviolet",
      "PCP":"brown",
      "ADIM":"burlywood",
      "CDS":"chartreuse",
      "AD":"coral",
      "APU":"cornflowerblue",
      "PSD":"crimson",
      "PPD/PSD":"darkgreen",
      "CDU":"red"}
color_dict={"PS": "blue","PPD":"blueviolet","PCP":"brown","ADIM":"burlywood","CDS":"chartreuse","AD":"coral","APU":"cornflowerblue","PSD":"crimson","PPD/PSD":"darkgreen",
      "CDU":"red","FEC":"aqua","MDP":" chocolate","MES":" darkblue","PUP":" darkgoldenrod","UDP":"darkseagreen","FSP":"darkslategray","PPM":"deeppink","LCI":"dodgerblue",
      "CDM":"gold","AOC":"goldenrod","MRPP":"hotpink","PDC":" indianred","PCP (M-L)":" indigo","PRT":"khaki","PCTP/MRPP":"lightseagreen",
      "PSR":"maroon","UEDS":"mediumorchid","OCMLP":"mediumpurple","POUS":"olive","FRS":"orange","PDC/MIRN-PDP/FN":"orangered","POUS/PST":"orchid","PT":"salmon",
      "UDA/PDA":"rosybrown","LST":"seagreen","PDA":"silver","UDP/PSR":"slateblue","PC(R)":" skyblue","PRD":"yellow","MDP/CDE":"yellowgreen",
      "FER":"turquoise","PSN":"tomato","CDS-PP":"thistle","PG":"teal","PPM/MPT":"tan","MPT":"springgreen","MUT":"slategray","BE":"sandybrown","PH":"saddlebrown",
      "PNR":"purple","PND":"powderblue","MEP":"plum","MMS":"pink","MPT-PH":"paleturquoise","PPV":" palevioletred","PTP":"magenta","PAN":" limegreen"
}

#--------------------------------------------sources para os plots-----------------------------------------------------
def json_data(selectedYear):             #funcao recebe um ano e devolve um json dos dados do ano merged com a mapa de Portugal
    dada_selectedYear = data[data["data"] == selectedYear]
    dada_selectedYear = only_winners(dada_selectedYear)
    merged = portugal_map.merge(dada_selectedYear, left_on="NAME_1", right_on="nome")
    return merged.to_json()
def empty_year():    #retorna um ano "vazio" sem eleicoes
    dada_selectedYear = only_date(data, 1975)                                                                       #melhor era usar winners_dataframes[0]
    dada_selectedYear = only_winners(dada_selectedYear)
    dada_selectedYear["partido"]="Nada"
    dada_selectedYear["num_votos"] = "Nada"
    merged = portugal_map.merge(dada_selectedYear, left_on="NAME_1", right_on="nome")
    return merged.to_json()
def district_data(selectedYear, district):  #retorna os dados de eileicoes de um distrito
    data_selected = data[data["data"] == selectedYear]
    data_selected = data_selected[data_selected["nome"]==district]
    data_selected['angle'] = data_selected['num_votos'] / data_selected['num_votos'].sum() * 2 * math.pi
    l=[]
    for i in data_selected[["partido"]].T.values[0]:                                                        #l=[color_dict[i] for i in data_selected[["partido"]].T.values[0]]
        l.append(color_dict[i])
    data_selected["color"]=l
    return data_selected
def empty_district_data():    #retorna um distrito "vazio" quando nao havia eleicoes
    data_selected = data[data["data"] == 0]                                                                       #tudo nao é nessecario, so podia ter feito um dataframe com colunas "nome",... "color"
    data_selected['angle'] = data_selected['num_votos'] / data_selected['num_votos'].sum() * 2 * math.pi
    data_selected['color'] = "white"
    return data_selected

data_merged = portugal_map.merge(winner_dataframes[0],left_on="NAME_1",right_on="nome")   #primeira eleicao
geosource = GeoJSONDataSource(geojson =data_merged.to_json())

indices_dic=dict(zip(data_merged[["nome"]].index, data_merged[["nome"]].T.values[0]))   #dic de indice e distrito

number=[0 for i in winner_partys]
legend_datasource=ColumnDataSource(data=dict(winner_partys=winner_partys, number=number))  #legenda

district_source=ColumnDataSource(empty_district_data())  #distrito

#------------------------------------plots-----------------------------------------------------------------------------
pTitle=figure(title="Resultados-legislativas em Portugal entre 1975 e 2011", plot_width=1045, plot_height=73)
pTitle.toolbar.logo=None
pTitle.toolbar_location = None
pTitle.title.text_font_size = '30pt'

slider=Slider(title="Year", start=1975, end=2011, step=1, value=1975)

p = figure(title = 'Partidos mais votados em cada distrito 1975', toolbar_location = 'above',  #mapa de portugal
            tools = "pan, wheel_zoom, reset",plot_width=500, plot_height=500)
states = p.patches('xs', 'ys', source = geosource, line_color = "black", line_width=0.5,
            fill_color = factor_cmap("partido", palette = list(cmap.values()), factors=list(cmap.keys())))
p.vbar(x="winner_partys", top="number", source=legend_datasource, legend_field="winner_partys",     #legenda
            fill_color=factor_cmap("winner_partys", palette = list(cmap.values()), factors=list(cmap.keys())))
p.add_tools(HoverTool(renderers = [states],
            tooltips = [('nome','@nome'),('num_votos','@num_votos'),("partido","@partido")]), TapTool())
p.legend.location = "bottom_left"
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.axis.axis_label=None
p.axis.visible=False
p.toolbar.logo = None

p2=figure(title=" ", toolbar_location = 'above', tools = "", plot_width=600, plot_height=500)    #diagrama do distrito
p2.wedge(x=0, y=0, radius=0.6, start_angle=cumsum("angle", include_zero=True),end_angle=cumsum('angle'),
            source=district_source, fill_color="color", legend_field="partido", line_color="white")
p2.add_tools(HoverTool(tooltips = [("partido", "@partido"),('num_votos','@num_votos'),('mandatos','@mandatos')]))
p2.axis.axis_label=None
p2.axis.visible=False
p2.xgrid.grid_line_color = None
p2.ygrid.grid_line_color = None
p2.toolbar.logo = None
p2.toolbar_location = None

def slider_change(attr, old, new):
    yr=slider.value
    district_source.data = empty_district_data()
    p2.title.text = " "
    if yr in dates:
        geosource.geojson=json_data(yr)
        p.title.text="Partidos mais votados em cada distrito %d" %yr
    else:
        geosource.geojson=empty_year()
        p.title.text = "Não havia eleições neste ano"
def selection_change(attr, old, new):
    yr=slider.value
    if geosource.selected.indices==[]:
        district_source.data=empty_district_data()
        p2.title.text=" "
    else:
        if yr in dates:
            ind=geosource.selected.indices[0]
            district=indices_dic[ind]
            district_source.data=district_data(yr, district)
            p2.title.text=district

geosource.selected.on_change('indices', selection_change)
slider.on_change("value", slider_change)

layout=column(pTitle,slider, row(p,p2))
curdoc().add_root(layout)