import ee
import geemap.foliumap as geemap
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
from folium import Map, plugins

def minMax_html(min_val, max_val, area, index_name):
    html = f"""
    <div style="background-color: #f2f2f2; padding: 10px; border-radius: 5px;">

        <h6> Min  {index_name} = {round(min_val, 2)} </h6>
        <h6> Mean {index_name} = {round((max_val+min_val)/2, 2)} </h6>
        <h6> Max {index_name} = {round(max_val, 2)} </h6>
        <h6> Area = {round(area, 2)} sq.km</h6>
    </div>
    """
    return html

def legend_static_html():
    html = f"""
    <div style="background-color: #f2f2f2; padding: 10px; border-radius: 5px;">

        <h6 style="color:purple"> Airports </h6>
        <h6 style="color:blue"> River Network </h6>
        <h6 style="color:cyan"> Streams </h6>
        <h6 style="color:brown"> Railway Line </h6>
        <h6 style="color:purple"> Airports </h6>
        <h6 style="color:green"> Climate Station </h6>
        <h6 style="color:red"> Hydrometric Station </h6>
    </div>
    """
    return html

def colorLegend_html():

    colors = ['#006400', '#ffbb22', '#ffff4c', '#f096ff', '#fa0000', '#b4b4b4', '#f0f0f0', '#0064c8', '#0096a0', '#00cf75', '#fae6a0']
    names = ['Tree cover', 'Shrubland', 'Grassland', 'Cropland', 'Built-up', 'Bare / sparse vegetation', 'Snow and ice', 'Permanent water bodies', 'Herbaceous wetland', 'Mangroves', 'Moss and lichen']

    if len(colors) != len(names):
        raise ValueError("Number of colors and names must be the same.")

    num_columns = 2
    items_per_column = (len(colors) + num_columns - 1) // num_columns

    legend_items = ""
    for i in range(0, len(colors), items_per_column):
        column_items = zip(colors[i:i + items_per_column], names[i:i + items_per_column])
        column_html = ""
        for color, name in column_items:
            column_html += f"""
                <div style="margin-bottom: 5px; display: flex; align-items: center;">
                    <div style="width: 20px; height: 20px; background-color: {color}; border: 1px solid #ccc;"></div>
                    <span style="margin-left: 5px; font-size: 14px; flex-grow: 1;">{name}</span>
                </div>
            """
        legend_items += f'<div style="flex: 1; margin-right: 20px;">{column_html}</div>'

    html = f"""
    <div style="background-color: #f2f2f2; padding: 10px; border-radius: 5px; display: flex;">
        {legend_items}
    </div>
    """
    return html




def get_basins():
    dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
    basins_list = dataset.aggregate_array("Basin").sort().distinct().getInfo()
    return basins_list

# Function to display map
def display_map(selected_index,selected_basin=None, selected_sub_basin=None, ndvi_image=None, srtm_image=None,transpiration_image=None,windspeed_image=None, temp_image=None,soil_temperature_image=None,soil_moisture_image=None,population_image=None, snow_cover_image=None, Precp_image=None, LAI_image=None, landcover_image=None, evi_image=None, et_image=None,pet_image=None, lhf_image=None, kbdi_image=None,lst_image=None, geojson_data=None, min=None, max=None, area=None):
    
    if min and max:
        html = minMax_html(min, max, area, selected_index)

    Map = geemap.Map(add_google_map=False)

    basin_feature_collection = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
    basins = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins').select('Basin')
    

    # When Main Page is loaded add the map
    # Map.addLayer(basin_feature_collection.style(color='purple',fillColor='#00000030'), {}, 'Pak-Afghan Shared Water Basins')
    Map.addLayer(basins.style(color='yellow',fillColor='#00000030'), {}, 'Pak-Afghan Shared Water Basins')
    durand_line = ee.FeatureCollection('projects/ee-mspkafg/assets/durand')
    centroid_durand_line = geemap.vector_centroids(durand_line)
    Map.addLayer(durand_line,{'color':'red'},'Durand Line')
    # df_durand_line = geemap.ee_to_df(centroid_durand_line)
    # Map.add_labels(df_durand_line,"Name",font_size="10pt",
    # font_color="red",
    # font_family="arial",
    # font_weight="bold",)

    centroids = geemap.vector_centroids(basin_feature_collection)
    centroids2 = geemap.vector_centroids(basin_feature_collection.distinct('Basin'))
    df = geemap.ee_to_df(centroids2)
    # st.write(df)
    Map.add_labels(
    df,
    "Basin",
    font_size="10pt",
    font_color="black",
    font_family="arial",
    font_weight="bold",
    )
    


    if st.session_state['get_all']:
        # Map.addLayer(basin_feature_collection.style(color='purple',fillColor='#00000030'), {}, 'Pak-Afghan Shared Water Basins')
        # Map.addLayer(basins.style(color='yellow',fillColor='#00000030'), {}, 'Pak-Afghan Shared Water Basins')

        # centroids = geemap.vector_centroids(basin_feature_collection)
        # centroids2 = geemap.vector_centroids(basin_feature_collection.distinct('Basin'))

        # # df2 = geemap.ee_to_df(centroids2)
        # df = geemap.ee_to_df(centroids)

        # Map.add_labels(
        # df,
        # "Sub_Basin",
        # font_size="10pt",
        # font_color="black",
        # font_family="arial",
        # font_weight="bold",
        # )

        # Map.add_labels(
        # df2,
        # "Basin",
        # font_size="20pt",
        # font_color="Red",
        # font_family="arial",
        # font_weight="bold",
        # )

        # Map.addLayer(durand_line,{"color":'red'},'Durand Line')

        if st.session_state['airports']:
            airport = ee.FeatureCollection('projects/ee-mspkafg/assets/2-airport/Airport')
            airport_style = {'color': 'a455ff', 'pointSize': 5, 'pointShape': 'diamond'}
            Map.addLayer(airport, airport_style)
            centroids = geemap.vector_centroids(airport)
            df = geemap.ee_to_df(centroids)
            Map.add_labels(
            df,
            "Airport",
            font_size="12pt",
            font_color="red",
            font_family="arial",
            font_weight="light",
            )
            Map.add_html(legend_static_html(), position='bottomright')
            # legend_static_html
        
        if st.session_state['subbasins_dl']:
            subbasins = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
            subbasins_style = {'color': 'blue','fillColor':'#FFFFFF00'}
            Map.addLayer(subbasins, subbasins_style)
            centroids = geemap.vector_centroids(subbasins)
            df = geemap.ee_to_df(centroids)
            Map.add_labels(
            df,
            "Sub_Basin",
            font_size="12pt",
            font_color="red",
            font_family="arial",
            font_weight="light",
            )
            Map.add_html(legend_static_html(), position='bottomright')

        # Uncomment for soil types
        if st.session_state['soiltypes']:
            # st.write('No Soil Types Collection Found')
            soil = ee.Image('projects/ee-mspkafg/assets/soil_types_raster_500')
            Map.addLayer(soil.randomVisualizer(),{},'Soil Types')
            # subbasins = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
            # subbasins_style = {'color': 'blue','fillColor':'#FFFFFF00'}
            # Map.addLayer(subbasins, subbasins_style)
            # centroids = geemap.vector_centroids(subbasins)
            # df = geemap.ee_to_df(centroids)
            # Map.add_labels(
            # df,
            # "Name",
            # font_size="12pt",
            # font_color="red",
            # font_family="arial",
            # font_weight="light",
            # )
            Map.add_html(legend_static_html(), position='bottomright')

        if st.session_state['rivers']:
            rivers = st.session_state['rivers']
            rivers = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/River_Network')
            rivers_style = {'color': 'blue', 'width': 2}
            Map.addLayer(rivers, rivers_style)
            centroids = geemap.vector_centroids(rivers)
            df = geemap.ee_to_df(centroids)
            Map.add_labels(
            df,
            "Name",
            font_size="12pt",
            font_color="blue",
            font_family="arial",
            font_weight="light",
            )
            Map.add_html(legend_static_html(), position='bottomright')

        if st.session_state['railwayline']:
            railwayline = ee.FeatureCollection('projects/ee-mspkafg/assets/railway_line_within_basin/Railway_Line')
            railwayline_style = {'color': 'brown', 'width': 2}
            Map.addLayer(railwayline, railwayline_style)
            Map.add_html(legend_static_html(), position='bottomright')

        if st.session_state['climate_stations']:
            climatic_stations = ee.FeatureCollection('projects/ee-mspkafg/assets/3-climate_station/Climate_Station')
            climatic_stations_style = {'color': 'green', 'pointSize': 5}
            Map.addLayer(climatic_stations, climatic_stations_style)
            Map.add_html(legend_static_html(), position='bottomright')
            

        if st.session_state['hydrometric_stations']:
            hydrometric_stations = ee.FeatureCollection('projects/ee-mspkafg/assets/4-hydrometric_station/Hydrometric_Station')
            hydrometric_stations_style = {'color': 'red', 'pointSize': 5}
            Map.addLayer(hydrometric_stations, hydrometric_stations_style)
            centroids = geemap.vector_centroids(hydrometric_stations)
            df = geemap.ee_to_df(centroids)
            Map.add_labels(
            df,
            "Name",
            font_size="12pt",
            font_color="green",
            font_family="arial",
            font_weight="light",
            )
            Map.add_html(legend_static_html(), position='bottomright')

        if st.session_state['streams']:
            streams = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/Stream_Network')
            streams_style = {'color': 'cyan', 'width': 2}
            Map.addLayer(streams, streams_style)
            Map.add_html(legend_static_html(), position='bottomright')
    

    # Set the map center to a default location first
    Map.setCenter(70, 33, 6)

    # Clear all layers before adding new ones
    Map.layers = []

    # Add GeoJSON data to the map if available
    if geojson_data:
        Map = geemap.Map(add_google_map=False)
        geojson_layer = ee.FeatureCollection(geojson_data)
        Map.centerObject(geojson_layer)
        Map.addLayer(geojson_layer.style(color='red',fillColor='#FFFFFF00'), {'min': min, 'max': max, 'pallete': ['yellow','orange','red']}, "AOI")

    # below is select basin - sub basin
    if selected_basin and selected_basin != 'None':
        basin_feature = basin_feature_collection.filter(ee.Filter.eq('Basin', selected_basin))
        Map.addLayer(basin_feature, {}, 'Basin')
        Map.centerObject(basin_feature, 7)

    if selected_sub_basin and selected_sub_basin != 'None':
        sub_basin_feature = basin_feature_collection.filter(ee.Filter.eq('Sub_Basin', selected_sub_basin))
        Map.addLayer(sub_basin_feature.style(**{'color': 'red'}), {}, 'Sub-Basin')
        Map.centerObject(sub_basin_feature)

    if selected_index == 'NDVI' and ndvi_image:
        ndvi_vis_params = {'min': min, 'max': max, 'palette': ['0000FF', '00FF00', 'FF0000']}
        Map.addLayer(ndvi_image, ndvi_vis_params, 'NDVI')
        if min and max:
            Map.add_html(html, position='topright')
        Map.add_colormap(label="NDVI Colorbar", position=(35,5), vmin=ndvi_vis_params['min'], vmax=ndvi_vis_params['max'], vis_params=ndvi_vis_params)
        # Map.add_widget(st.session_state['ndvi_chart'])
    
    if selected_index == 'Land Surface Temperature' and lst_image:
        lst_vis_params = {'min': min, 'max': max, 'palette': ['blue','cyan','green','yellow','orange','red']}
        Map.addLayer(lst_image, lst_vis_params, 'LST')
        if min and max:
            Map.add_html(html, position='topright')
        Map.add_colormap(label="Land Surface Temp. (C)", position=(35,5), vmin=lst_vis_params['min'], vmax=lst_vis_params['max'], vis_params=lst_vis_params)
        # Map.add_widget(st.session_state['ndvi_chart'])
    
    if selected_index=="SRTM" and srtm_image:
        srtm_vis_params = {'min': min, 'max': max, 'palette': ['0000FF', 'FF0000']}
        Map.addLayer(srtm_image, srtm_vis_params, 'SRTM')
        if min and max:
            Map.add_html(html, position='topright')
        Map.add_colormap(label="Elevation (mASL)", position=(35,5), vmin=srtm_vis_params['min'], vmax=srtm_vis_params['max'], vis_params=srtm_vis_params)
    
    if selected_index=="Population" and population_image:
        population_vis_params = {'min': min, 'max': max, 'palette': ['0000FF', 'FF0000']}
        Map.addLayer(population_image, population_vis_params, 'Population Density')
        if min and max:
            Map.add_html(html, position='topright')
        Map.add_colormap(label="Population Density (2019)", position=(35,5), vmin=population_vis_params['min'], vmax=population_vis_params['max'], vis_params=population_vis_params)
    
    if selected_index=="Land Cover (2020)" and landcover_image:
        landcover_image = landcover_image.remap([10,20,30,40,50,60,70,80,90,95,100],[0,10,20,30,40,50,60,70,80,90,100])
        lc_vis_params = {'min': min, 'max': max, 'palette': ['006400', 'ffbb22','ffff4c','f096ff','fa0000','b4b4b4','f0f0f0','0064c8','0096a0','00cf75','fae6a0']}
        Map.addLayer(landcover_image, lc_vis_params, 'Land Cover 2020')
        #Adding Color-Bar Discrete
        # num_classes = 11
        # colors = ['#006400', '#ffbb22', '#ffff4c', '#f096ff', '#fa0000', '#b4b4b4',
        #         '#f0f0f0', '#0064c8', '#0096a0', '#00cf75', '#fae6a0']
        # fig, ax = plt.subplots(figsize=(3, 1))
        # fig.subplots_adjust(bottom=0.5)
        # cmap = plt.matplotlib.colors.ListedColormap(colors)
        # bounds = np.linspace(0, num_classes, num_classes + 1)
        # norm = plt.matplotlib.colors.BoundaryNorm(bounds, cmap.N)
        # cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap),
        #                 cax=ax, orientation='horizontal', ticks=bounds + 0.5)
        # cb.set_ticklabels([str(i) for i in range(num_classes + 1)])
        # ax.set_xlabel('Land Cover Classes')
        # Map.add_widget(fig,position="bottomright")
        Map.add_html(colorLegend_html(), position='bottomright')
        # Map.add_colormap(tick_size=8, discrete=True,label="LC 2020 Colorbar", position=(35,5), vmin=lc_vis_params['min'], vmax=lc_vis_params['max'], vis_params=lc_vis_params)
    #elif was here
    if selected_index == 'Air Temperature' and temp_image:
        temp_vis_params = {'min': min, 'max': max, 'palette': ['blue', 'cyan', 'green','yellow','orange','red']}
        Map.addLayer(temp_image, temp_vis_params, 'Air Temperature')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="Air Temperature (C)", position=(35,5), vmin=temp_vis_params['min'], vmax=temp_vis_params['max'], vis_params=temp_vis_params)
    if selected_index == 'Soil Moisture' and soil_moisture_image:
        soil_moisture_vis_params = {'min': min, 'max': max, 'palette': ['0300ff', '418504', 'efff07', 'efff07', 'ff0303']}
        Map.addLayer(ee.Image(soil_moisture_image), soil_moisture_vis_params, 'Soil Moisture')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="Soil Moisture (mm) Mean", position=(35,5), vmin=soil_moisture_vis_params['min'], vmax=soil_moisture_vis_params['max'], vis_params=soil_moisture_vis_params)
    
    if selected_index == 'Soil Temperature' and soil_temperature_image:
        soil_temperature_vis_params = {'min': min, 'max': max, 'palette': ['000080', '0000d9', '4000ff', '8000ff', '0080ff', '00ffff','00ff80', '80ff00', 'daff00', 'ffff00', 'fff500', 'ffda00','ffb000', 'ffa400', 'ff4f00', 'ff2500', 'ff0a00', 'ff00ff']}
        Map.addLayer(soil_temperature_image, soil_temperature_vis_params, 'Soil Temperature')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="Soil Temp. (C) Mean", position=(35,5), vmin=soil_temperature_vis_params['min'], vmax=soil_temperature_vis_params['max'], vis_params=soil_temperature_vis_params)

    if selected_index == 'Transpiration (TP)' and transpiration_image:
        transpiration_vis_params = {'min': min, 'max': max, 'palette': ['000080', '0000d9', '4000ff', '8000ff', '0080ff', '00ffff','00ff80', '80ff00', 'daff00', 'ffff00', 'fff500', 'ffda00','ffb000', 'ffa400', 'ff4f00', 'ff2500', 'ff0a00', 'ff00ff']}
        Map.addLayer(transpiration_image, transpiration_vis_params, 'Transpiration')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="Transpiration (m) Mean", position=(35,5), vmin=transpiration_vis_params['min'], vmax=transpiration_vis_params['max'], vis_params=transpiration_vis_params)

    if selected_index == 'Wind Speed' and windspeed_image:
        windspeed_vis_params = {'min': min, 'max': max, 'palette': ['000080', '0000d9', '4000ff', '8000ff', '0080ff', '00ffff','00ff80', '80ff00', 'daff00', 'ffff00', 'fff500', 'ffda00','ffb000', 'ffa400', 'ff4f00', 'ff2500', 'ff0a00', 'ff00ff']}
        Map.addLayer(windspeed_image, windspeed_vis_params, 'windspeed')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="windspeed (m) Mean", position=(35,5), vmin=windspeed_vis_params['min'], vmax=windspeed_vis_params['max'], vis_params=windspeed_vis_params)

    if selected_index == 'Evapotranspiration (ET)' and et_image:
        # st.write(et_image)
        et_vis_params = {'min': min, 'max': max, 'palette': ['ffffff', 'fcd163', '99b718', '66a000', '3e8601', '207401', '056201','004c00', '011301']}
        Map.addLayer(ee.Image(et_image), et_vis_params, 'ET')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="ET (kg/m^2)", position=(35,5), vmin=et_vis_params['min'], vmax=et_vis_params['max'], vis_params=et_vis_params)
    
    if selected_index == 'Latent Heat Flux (LE)' and lhf_image:
        lhf_vis_params = {'min': min, 'max': max, 'palette': ['ffffff', 'fcd163', '99b718', '66a000', '3e8601', '207401', '056201','004c00', '011301']}
        Map.addLayer(lhf_image, lhf_vis_params, 'Latent Heat Flux')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="LE (J/m^2/day)", position=(35,5), vmin=lhf_vis_params['min'], vmax=lhf_vis_params['max'], vis_params=lhf_vis_params)
    
    if selected_index == 'Potential Evapotranspiration (PET)' and pet_image:
        pet_vis_params = {'min': min, 'max': max, 'palette': ['ffffff', 'fcd163', '99b718', '66a000', '3e8601', '207401', '056201','004c00', '011301']}
        Map.addLayer(pet_image, pet_vis_params, 'Potential ET')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="PET (kg/m^2)", position=(35,5), vmin=pet_vis_params['min'], vmax=pet_vis_params['max'], vis_params=pet_vis_params)
    
    if selected_index == 'Leaf Area Index' and LAI_image:
        LAI_vis_params = {'min': min, 'max': max, 'palette': ['ffffff', 'ce7e45', 'df923d', 'f1b555', 'fcd163', '99b718', '74a901', '66a000', '529400', '3e8601', '207401', '056201', '004c00', '023b01',  '012e01', '011d01', '011301']}
        Map.addLayer(LAI_image, LAI_vis_params, 'LAI')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="LAI", position=(35,5), vmin=LAI_vis_params['min'], vmax=LAI_vis_params['max'], vis_params=LAI_vis_params)

    if selected_index == 'Precipitation' and Precp_image:
        Precp_vis_params = {'min': min, 'max': max, 'palette': ['001137', '0aab1e', 'e7eb05', 'ff4a2d', 'e90000']}
        Map.addLayer(Precp_image, Precp_vis_params, 'Precipitation mm/day')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="Mean Precipitation", position=(35,5), vmin=Precp_vis_params['min'], vmax=Precp_vis_params['max'], vis_params=Precp_vis_params)

    if selected_index == 'Snow Cover' and snow_cover_image:
        snow_cover_vis_params = {'min': min, 'max': max, 'palette': ['black', '0dffff', '0524ff']}
        Map.addLayer(snow_cover_image, snow_cover_vis_params, 'NDSI')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="NDSI (Snow Cover) Mean", position=(35,5), vmin=snow_cover_vis_params['min'], vmax=snow_cover_vis_params['max'], vis_params=snow_cover_vis_params)


    if selected_index == 'Keetch-Byram Drought Index' and kbdi_image:
        kbdi_vis_params = {'min': min, 'max': max, 'palette': ['001a4d', '003cb3', '80aaff', '336600', 'cccc00', 'cc9900', 'cc6600','660033']}
        Map.addLayer(kbdi_image, kbdi_vis_params, 'KBDI')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="KBDI Colorbar", position=(35,5), vmin=kbdi_vis_params['min'], vmax=kbdi_vis_params['max'], vis_params=kbdi_vis_params)

    if selected_index == 'Enhanced Vegetation Index (EVI)' and evi_image:
        evi_vis_params = {'min': min, 'max': max, 'palette': ['ffffff', 'ce7e45', 'df923d', 'f1b555', 'fcd163', '99b718', '74a901','66a000', '529400', '3e8601', '207401', '056201', '004c00', '023b01', '012e01', '011d01', '011301']}
        Map.addLayer(evi_image, evi_vis_params, 'EVI')
        if min and max:
            Map.add_html(html=html, position='topright')
        Map.add_colormap(label="EVI Colorbar", position=(35,5), vmin=evi_vis_params['min'], vmax=evi_vis_params['max'], vis_params=evi_vis_params)
        
    return Map
