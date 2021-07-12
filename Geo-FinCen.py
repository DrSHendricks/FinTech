# Geo analysis with FinCen data (suspicious transactions for money laundering compliance)
```
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import geopandas as gpd
import geoplot as gplt
import geoplot.crs as gcrs
import mapclassify as mc
world = gpd.read_file(gplt.datasets.get_path('world'))
world = world[world.id !='-99']
df=pd.read_csv(r"https://github.com/DrSHendricks/FinTech/blob/main/download_transactions_map.csv", index_col='id')
fmt = '${x:,.0f}'
tick = mtick.StrMethodFormatter(fmt)
ncols=2
df['begin_date']=pd.to_datetime(df['begin_date'])
df['end_date']=pd.to_datetime(df['end_date'])
df['year']=df['begin_date'].dt.year
world_points=world.copy()
world_points['centroid'] = world_points.centroid
world_points = world_points.set_geometry('centroid')
from shapely.geometry import MultiPoint
country_sum=(df.groupby(['originator_iso','beneficiary_iso'])['amount_transactions'].agg(sum)/100000).reset_index()
map_network = world_points.merge(country_sum, left_on="id", right_on="originator_iso")
map_network = world_points.merge(map_network, left_on="id", right_on="beneficiary_iso")
def mapST(df,dire):
    country_sum=df.groupby([dire+'_iso'])['amount_transactions'].agg(sum)/100000
    map_st = world.merge(country_sum, left_on="id", right_on=dire+'_iso')
    scheme = mc.UserDefined(map_st['amount_transactions'], bins=[2500, 5000, 10000, 50000])
    gplt.choropleth(
        map_st, hue='amount_transactions',
        edgecolor='lightgray', linewidth=1,
        cmap='rainbow', legend=True, legend_kwargs={'loc': 'lower left', 'fontsize':15},
        scheme=scheme, figsize=(15,15),
        legend_labels=['< $2,500 million','$2,500-5,000 million', '$5,000-10,000 million', '$10,000-50,000 million',
             '>$50,000 million'])
    plt.title("Sum of ST by Country between 2000 and 2017",fontsize=20)
    plt.show()
           
mapST(df,'beneficiary')
def CountrySTFlow(df, dire, country, top):
    ###ST flowing in or out from a Country###
    df2=df[df[dire+'_iso']==country]
    df2['multi'] = [MultiPoint([x, y]) for x, y in zip(df2.centroid_y, df2.centroid_x)]
    df2=df2.set_geometry('multi')
    df2=df2.nlargest(top, columns=['amount_transactions'])
    scheme = mc.JenksCaspall(df2['amount_transactions'])
    lc=[f'${x:,.0f} million' for x in df2['amount_transactions']] 
    ax = gplt.sankey(df2, projection=gcrs.WebMercator(),
                hue='amount_transactions', scheme=scheme, cmap='Dark2', 
                legend=True,legend_kwargs={'loc': 'lower left', 'fontsize':10},
                legend_labels=lc, figsize=(12,12), linestyles=':')
    gplt.polyplot(world, ax=ax, facecolor='lightgray', edgecolor='white')
    plt.title(f"Sum of top {top} ST of {country} {dire.title()} between 2000 and 2017",fontsize=15)
    plt.show()

CountrySTFlow(map_network, 'beneficiary', 'USA', 5)    
```
