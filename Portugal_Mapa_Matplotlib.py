import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

#-------------------------------Editar os dados------------------------------------------------------------------------
mapa_Portugal=gpd.read_file("distritos(2)/distritos.shp")
dados=pd.read_csv("resultados-legislativas.csv")

dados=dados[["nome","data","partido","num_votos","mandatos"]]   #tirar as colunas código, tipo e perc_votos

MaxMin=dados[["data"]].T.values
max_=max(MaxMin[0])[:4]
min_=min(MaxMin[0])[:4]

dados["nome"].replace({"Corvo":"Açores","São Jorge":"Açores","São Miguel":"Açores"}, inplace=True)   #juntar Corvo,Sao Jorge e Sao Miguel para Acores
dados=dados.groupby(["nome","data","partido"])[["num_votos","mandatos"]].sum().reset_index()
dados=dados.sort_values(["data","nome"])

#for i in range(len(dados.values)):               #tirar Mocambique e Macau dos dados
#    if "Moçambique" in dados.values[len(dados.values)-1-i] or "Macau" in dados.values[len(dados.values)-1-i]:
#        dados.drop([len(dados.values)-1-i],axis=0,inplace=True)  ####################################################Ver se funciona####################

datas=dados.T.values[1]            #separar os dados em Dataframes para cada data
datas=[0]+[i for i in range(1,len(datas)) if datas[i]!=datas[i-1]]+[len(datas)-1]
dataframes=[dados[datas[i-1]:datas[i]] for i in range(1,len(datas))]

dataframes_editados=[i.sort_values(["num_votos"],ascending=False).drop_duplicates(["nome"]) for i in dataframes]  #os dataframes sorted e só com o partido mais votado

mais_votados=[i[["partido"]].T.values for i in dataframes_editados]     #lista dos partidos mais votados
l=[]
for i in range(len(mais_votados)):
    for j in range(len(mais_votados[i][0])):
        l.append(mais_votados[i][0][j])
mais_votados=pd.DataFrame(l).drop_duplicates().T.values[0]
mais_votados=[i for i in mais_votados]

#map0= mapa_Portugal.merge(dataframes_editados[0],left_on="NAME_1",right_on="nome")
#map1= mapa_Portugal.merge(dataframes_editados[1], left_on="NAME_1", right_on="nome")
#mas=map0.plot(column="partido", cmap="tab10", legend=True, linewidth=2)
map=mapa_Portugal.plot(cmap="hsv")
#plt.set_color("red")
axSlider1=plt.axes([0.2,0.2,0.6,0.02])
silder1=Slider(axSlider1, "Ano:", valmin=int(min_), valmax=int(max_), valstep=1)
def slider_Chance(value):
    print(value)
    mas=map1.plot(column="partido", cmap="tab10", legend=True, linewidth=2)
    map0.cmap="tab10"
    m1=map1.plot(column="partido", cmap="tab10", legend=True, linewidth=2)
    plt.draw()
silder1.on_changed(slider_Chance)
map.get_cmap(cmap="tab10")
plt.show()
