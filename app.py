import streamlit as st
import ee
import geemap.foliumap as geemap
from datetime import datetime
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import json
from streamlit_option_menu import option_menu
import base64


from src.sub_basins.ndvi import get_ndvi_image, create_ndvi_timeseries
from src.sub_basins.era_temp import get_era_temp_image, create_temp_timeseries
from src.sub_basins.evi import get_evi_image, create_evi_timeseries
from src.sub_basins.landcover import get_landcover_image
from src.sub_basins.lst import get_lst_image, create_lst_timeseries
from src.sub_basins.srtm import get_srtm_image
from src.sub_basins.population import get_population_image
from src.sub_basins.kbdi import get_kbdi_image, create_kbdi_timeseries
from src.sub_basins.et import get_et_image, create_et_timeseries
from src.sub_basins.lhf import get_lhf_image, create_lhf_timeseries
from src.sub_basins.pet import get_pet_image, create_pet_timeseries
from src.sub_basins.lai import get_LAI_image, create_LAI_timeseries
from src.sub_basins.precp import get_Precp_image, create_Precp_timeseries
from src.sub_basins.soil_moisture import get_soil_moisture_image, create_soil_moisture_timeseries
from src.sub_basins.soil_temperature import get_soil_temperature_image, create_soil_temperature_timeseries
from src.sub_basins.transpiration import get_transpiration_image, create_transpiration_timeseries
from src.sub_basins.windspeed import get_windspeed_image, create_windspeed_timeseries
from src.sub_basins.snow_cover import get_snow_cover_image, create_snow_cover_timeseries

from src.roi.ndvi_roi import get_ndvi_image_for_roi, create_ndvi_timeseries_roi
from src.roi.era_temp_roi import get_era_temp_image_roi, create_temp_timeseries_roi
from src.roi.et_roi import get_et_image_roi, create_et_timeseries_roi
from src.roi.evi_roi import get_evi_image_roi, create_evi_timeseries_roi
from src.roi.kbdi_roi import get_kbdi_image_roi, create_kbdi_timeseries_roi
from src.roi.lai_roi import get_LAI_image_roi, create_LAI_timeseries_roi
from src.roi.landcover_roi import get_landcover_image_roi
from src.roi.lhf_roi import get_lhf_image_roi, create_lhf_timeseries_roi
from src.roi.pet_roi import get_pet_image_roi, create_pet_timeseries_roi
from src.roi.population_roi import get_population_image_roi
from src.roi.precp_roi import get_Precp_image_roi, create_Precp_timeseries_roi
from src.roi.snow_cover_roi import get_snow_cover_image_roi, create_snow_cover_timeseries_roi
from src.roi.soil_moisture_roi import get_soil_moisture_image_roi, create_soil_moisture_timeseries_roi
from src.roi.soil_temperature_roi import get_soil_temperature_image_roi, create_soil_temperature_timeseries_roi
from src.roi.srtm_roi import get_srtm_image_roi
from src.roi.transpiration_roi import get_transpiration_image_roi, create_transpiration_timeseries_roi
from src.roi.windspeed_roi import get_windspeed_image_roi, create_windspeed_timeseries_roi
from src.roi.lst_roi import get_lst_image_roi, create_lst_timeseries_roi
from dotenv import load_dotenv
import webbrowser
from src.map import display_map
import os
from ee import data

from google.oauth2 import service_account

service_account = 'test-service@ee-mspkafg.iam.gserviceaccount.com'
credentials = ee.ServiceAccountCredentials(service_account, 'google-credentials.json')

ee.Initialize(credentials=credentials)

# External Redirection Function
def redirect(url):
    st.markdown(f'<meta http-equiv="refresh" content="0; url={url}">', unsafe_allow_html=True)


# Function to get basins and sub-basins.
def get_basins():
    dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
    basins_list = dataset.aggregate_array("Basin").sort().distinct().getInfo()
    return basins_list
def get_sub_basins(selected_basin):
    sub_basins_list = ['None']
    if selected_basin and selected_basin != 'None':
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        selected_basin_feature = dataset.filter(ee.Filter.eq('Basin', selected_basin))
        sub_basins_list += selected_basin_feature.aggregate_array('Sub_Basin').sort().distinct().getInfo()
    return sub_basins_list

def get_sub_basins_download(selected_basin):
    sub_basins_list = ['None']
    if selected_basin and selected_basin != 'None':
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        selected_basin_feature = dataset.filter(ee.Filter.eq('Basin', selected_basin))

    return selected_basin_feature

###########################################
###########################################

# Set full width layout
st.set_page_config(layout="wide", page_title="Pak-Afghan Shared Water Boundaries")



# Main app layout
def main():
    st.write("#")
    # Initialize session state variables (dual charts here or replace below below set to ndvi_chart)
    if 'selected_basin' not in st.session_state:
        st.session_state['selected_basin'] = 'None'
    if 'selected_sub_basin' not in st.session_state:
        st.session_state['selected_sub_basin'] = 'None'
    if 'selected_index' not in st.session_state:  # Headache
        st.session_state['selected_index'] = 'None'
    if 'geojson_data' not in st.session_state:
        st.session_state['geojson_data'] = None

    # Images
    if 'area' not in st.session_state:
        st.session_state['area'] = None
    if 'min' not in st.session_state:
        st.session_state['min'] = None
    if 'max' not in st.session_state:
        st.session_state['max'] = None
    if 'ndvi_image' not in st.session_state:
        st.session_state['ndvi_image'] = None
    if 'et_image' not in st.session_state:
        st.session_state['et_image'] = None
    if 'windspeed_image' not in st.session_state:
        st.session_state['windspeed_image'] = None
    if 'snow_cover_image' not in st.session_state:
        st.session_state['snow_cover_image'] = None
    if 'transpiration_image' not in st.session_state:
        st.session_state['transpiration_image'] = None
    if 'soil_moisture_image' not in st.session_state:
        st.session_state['soil_moisture_image'] = None
    if 'soil_temperature_image' not in st.session_state:
        st.session_state['soil_temperature_image'] = None
    if 'Precp_image' not in st.session_state:
        st.session_state['Precp_image'] = None
    if 'LAI_image' not in st.session_state:
        st.session_state['LAI_image'] = None
    if 'pet_image' not in st.session_state:
        st.session_state['pet_image'] = None
    if 'lhf_image' not in st.session_state:
        st.session_state['lhf_image'] = None
    if 'lst_image' not in st.session_state:
        st.session_state['lst_image'] = None
    if 'temp_image' not in st.session_state:
        st.session_state['temp_image'] = None
    if 'evi_image' not in st.session_state:
        st.session_state['evi_image'] = None
    if 'kbdi_image' not in st.session_state:
        st.session_state['kbdi_image'] = None
    if 'srtm_image' not in st.session_state:
        st.session_state['srtm_image'] = None
    if 'population_image' not in st.session_state:
        st.session_state['population_image'] = None
    if 'landcover_image' not in st.session_state:
        st.session_state['landcover_image'] = None
    if 'filter_options_visible' not in st.session_state:
        st.session_state['filter_options_visible'] = False
    if 'upload_section_visible' not in st.session_state:
        st.session_state['upload_section_visible'] = False
    if 'executed' not in st.session_state:
        st.session_state['executed'] = False
    if 'uploaded_roi' not in st.session_state:
        st.session_state['uploaded_roi'] = False
    if 'chart' not in st.session_state:
        st.session_state['chart'] = None

    if 'subbasins_dl' not in st.session_state:
        st.session_state['subbasins_dl'] = None
    if 'soiltypes' not in st.session_state:
        st.session_state['soiltypes'] = None

    if 'airports' not in st.session_state:
        st.session_state['airports'] = None
    if 'streams' not in st.session_state:
        st.session_state['streams'] = None
    if 'rivers' not in st.session_state:
        st.session_state['rivers'] = None
    if 'railwayline' not in st.session_state:
        st.session_state['railwayline'] = None
    if 'climate_stations' not in st.session_state:
        st.session_state['climate_stations'] = None
    if 'hydrometric_stations' not in st.session_state:
        st.session_state['hydrometric_stations'] = None
    if 'boot' not in st.session_state:
        st.session_state['boot'] = True
    if 'get_all' not in st.session_state:
        st.session_state['get_all'] = False
    if 'show_checkboxes' not in st.session_state:
        st.session_state['show_checkboxes'] = None

    # Sidebar content
    with st.sidebar:
        st.image('logo_transparent_HQ.png', width=300)
        cols = st.columns(3)

        with cols[0]:
            if st.button("Filter Basin"):
                st.session_state['filter_options_visible'] = True
                st.session_state['upload_section_visible'] = False
                st.session_state['uploaded_roi'] = False
                st.session_state['chart'] = None
                st.session_state['min'] = None
                st.session_state['max'] = None
                st.session_state['get_all'] = True
                st.session_state['show_checkboxes'] = True
                st.session_state['geojson_data'] = False

        with cols[1]:
            # upload_roi = st.button("Upload ROI")
            if st.button("Upload ROI"):
                st.session_state['upload_section_visible'] = True

                # Hide the filter options when the upload section is shown
                st.session_state['filter_options_visible'] = False
                st.session_state['chart'] = None
                st.session_state['selected_index'] = None
                st.session_state['selected_basin'] = None
                st.session_state['selected_sub_basin'] = None
                st.session_state['get_all'] = None
                st.session_state['show_checkboxes'] = None

        # with cols[2]:
            # draw_aoi = st.button("Draw AOI")
         # Display the file uploader if the upload section is visible

        if st.session_state.get('upload_section_visible', False):
            uploaded_file = st.file_uploader("Upload GeoJSON file", type=['geojson'], accept_multiple_files=False, key="geojson_upload")
            if uploaded_file is not None and uploaded_file.size <= 200_000:  # Check for file size (200 kb max max)
                # Read the GeoJSON file
                geojson_data = json.load(uploaded_file)
                st.session_state['geojson_data'] = geojson_data
                st.session_state['uploaded_roi'] = True
            elif uploaded_file is not None:
                st.error("File too large. Please upload a file less than 2 MB.")

        if st.session_state.get('uploaded_roi', False):
            from_date_uploaded = st.date_input("From Date", key='from_date_uploaded')
            to_date_uploaded = st.date_input("To Date", key='to_date_uploaded')
            selected_index_uploaded = st.selectbox("Select Index", ['None', 'Air Temperature','Enhanced Vegetation Index (EVI)',"Evapotranspiration (ET)","Keetch-Byram Drought Index","Land Cover (2020)","Land Surface Temperature","Latent Heat Flux (LE)","Leaf Area Index","NDVI","Population","Potential Evapotranspiration (PET)","Precipitation","Snow Cover","Soil Moisture","Soil Temperature","SRTM","Transpiration (TP)","Wind Speed"], key='selected_index')

            execute_col, download_col = st.columns([1,1], gap="small")
            with execute_col:
                if st.button('Execute'):
                    if selected_index_uploaded == 'NDVI':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['ndvi_image'] = get_ndvi_image_for_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_ndvi_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['ndvi_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='ndvi_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Air Temperature':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['temp_image'] = get_era_temp_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_temp_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['temp_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='temp_timeseries_roi.csv',
                                mime='text/csv',
                                )

                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Land Surface Temperature':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['lst_image'] = get_lst_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_lst_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['lst_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='lst_timeseries_roi.csv',
                                mime='text/csv',
                                )

                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Latent Heat Flux (LE)':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['lhf_image'] = get_lhf_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_lhf_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['lhf_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='lhf_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Potential Evapotranspiration (PET)':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['pet_image'] = get_pet_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_pet_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['pet_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='pet_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Leaf Area Index':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['LAI_image'] = get_LAI_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_LAI_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['LAI_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='LAI_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Precipitation':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['Precp_image'] = get_Precp_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_Precp_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['Precp_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='precp_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Soil Moisture':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['soil_moisture_image'] = get_soil_moisture_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_soil_moisture_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['soil_moisture_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='soil_moisture_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Soil Temperature':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['soil_temperature_image'] = get_soil_temperature_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_soil_temperature_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['soil_temperature_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='soil_temperature_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Transpiration (TP)':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['transpiration_image'] = get_transpiration_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_transpiration_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)

                        csv = st.session_state['transpiration_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='transpiration_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Wind Speed':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['windspeed_image'] = get_windspeed_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_windspeed_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        csv = st.session_state['windspeed_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='windspeed_timeseries_roi.csv',
                                mime='text/csv',
                                )
                        # Indicate that the NDVI image should be displayed on the map
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == 'Snow Cover':
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        # Process the uploaded ROI
                        st.session_state['snow_cover_image'] = get_snow_cover_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_snow_cover_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        csv = st.session_state['snow_cover_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='snow_cover_timeseries_roi.csv',
                                mime='text/csv',
                                )

                        st.session_state['executed'] = True

                    elif selected_index_uploaded == "Keetch-Byram Drought Index":
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        st.session_state['kbdi_image'] = get_kbdi_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_kbdi_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        csv = st.session_state['kbdi_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='kbdi_timeseries_roi.csv',
                                mime='text/csv',
                                )

                        st.session_state['executed'] = True

                    elif selected_index_uploaded == "Evapotranspiration (ET)":
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        st.session_state['et_image'] = get_et_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_et_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        csv = st.session_state['et_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='et_timeseries_roi.csv',
                                mime='text/csv',
                                )

                        st.session_state['executed'] = True

                    elif selected_index_uploaded == "Enhanced Vegetation Index (EVI)":
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        st.session_state['evi_image'] = get_evi_image_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        st.session_state['chart'] = create_evi_timeseries_roi(st.session_state['geojson_data'], from_date_str, to_date_str)
                        csv = st.session_state['evi_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='evi_timeseries_roi.csv',
                                mime='text/csv',
                                )

                        st.session_state['executed'] = True

                    elif selected_index_uploaded == "SRTM":
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        st.session_state['srtm_image'] = get_srtm_image_roi(st.session_state['geojson_data'])
                        st.session_state['chart'] = None

                        st.session_state['executed'] = True

                    elif selected_index_uploaded == "Population":
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        st.session_state['population_image'] = get_population_image_roi(st.session_state['geojson_data'])
                        st.session_state['chart'] = None
                        st.session_state['executed'] = True

                    elif selected_index_uploaded == "Land Cover (2020)":
                        from_date_str = from_date_uploaded.strftime('%Y-%m-%d')
                        to_date_str = to_date_uploaded.strftime('%Y-%m-%d')

                        st.session_state['landcover_image'] = get_landcover_image_roi(st.session_state['geojson_data'])
                        st.session_state['chart'] = None

                        st.session_state['executed'] = True

            with download_col:
                    if st.session_state['executed']:
                        if st.button(f'Save GeoTIFF'): #if st.button(f'Save {selected_index}'):
                            # Code to download the image
                            try:
                                if selected_index_uploaded == 'SRTM':
                                    download_url = st.session_state['srtm_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)}) #'dimensions': [2000,2000]}
                                elif selected_index_uploaded == 'NDVI':
                                    download_url = st.session_state['ndvi_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Air Temperature':
                                    download_url = st.session_state['temp_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Enhanced Vegetation Index (EVI)':
                                    download_url = st.session_state['evi_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Evapotranspiration ET':
                                    download_url = st.session_state['et_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Keetch-Byram Drought Index':
                                    download_url = st.session_state['kbdi_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Land Cover (2020)':
                                    download_url = st.session_state['landcover_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Land Surface Temperature':
                                    download_url = st.session_state['lst_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Latent Heat Flux (LE)':
                                    download_url = st.session_state['lhf_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Leaf Area Index':
                                    download_url = st.session_state['LAI_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Population':
                                    download_url = st.session_state['population_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Potential Evapotranspiration (PET)':
                                    download_url = st.session_state['pet_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Precipitation':
                                    download_url = st.session_state['Precp_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Snow Cover':
                                    download_url = st.session_state['snowcover_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Soil Moisture':
                                    download_url = st.session_state['soil_moisture_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Soil Temperature':
                                    download_url = st.session_state['soil_temperature_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Transpiration (TP)':
                                    download_url = st.session_state['tp_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})
                                elif selected_index_uploaded == 'Wind Speed':
                                    download_url = st.session_state['windspeed_image'].getDownloadURL({'scale': 90, 'region': ee.FeatureCollection(st.session_state['geojson_data']).geometry(0.01).bounds(0.01)})


                                    # download_url = st.session_state['ndvi_image'].getDownloadURL({'scale': 20})
                                # elif selected_index == 'Air Temperature':
                                #     download_url = st.session_state['']


                                st.markdown(f"[Download {selected_index_uploaded}]({download_url})", unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"An error occurred: {e}")
        # Display filter options if the filter section is visible
        if st.session_state.get('filter_options_visible', False):
        # Sidebar filter options
            if st.session_state['filter_options_visible']:
                # with st.sidebar:
                selected_basin = st.selectbox("Select Basin", ['None'] + get_basins(), key='selected_basin')
                selected_sub_basin = st.selectbox("Select Sub-Basin", get_sub_basins(selected_basin), key='selected_sub_basin')
                from_date = st.date_input("From Date", datetime.today(), key='from_date')
                to_date = st.date_input("To Date", datetime.today(), key='to_date')
                selected_index = st.selectbox("Select Index", ['None', 'Air Temperature','Enhanced Vegetation Index (EVI)','Evapotranspiration (ET)',"Keetch-Byram Drought Index","Land Cover (2020)","Land Surface Temperature","Latent Heat Flux (LE)","Leaf Area Index","NDVI","Population","Potential Evapotranspiration (PET)","Precipitation","Snow Cover","Soil Moisture","Soil Temperature","SRTM","Transpiration (TP)","Wind Speed"], key='selected_index')

                execute_col, download_col = st.columns([1,1], gap="small")
            with execute_col:
                if st.button('Execute'):
                    # st.write(f"Selected Index before any operation: {st.session_state['selected_index']}")
                    st.session_state['chart'] = None
                    st.session_state['min'] = None
                    st.session_state['max'] = None
                    # Reset images in session state
                    st.session_state['ndvi_image'] = None
                    st.session_state['srtm_image'] = None
                    st.session_state['temp_image'] = None
                    st.session_state['lst_image'] = None
                    st.session_state['evi_image'] = None
                    st.session_state['kbdi_image'] = None
                    st.session_state['et_image'] = None
                    st.session_state['landcover_image'] = None
                    st.session_state['lhf_image'] = None
                    st.session_state['pet_image'] = None
                    st.session_state['LAI_image'] = None
                    st.session_state['Precp_image'] = None
                    st.session_state['transpiration_image'] = None
                    st.session_state['snow_cover_image'] = None
                    st.session_state['population_image'] = None
                    st.session_state['soil_moisture_image'] = None
                    st.session_state['soil_temperature_image'] = None
                    st.session_state['windspeed_image'] = None
                    # Get the appropriate image based on selected index
                    if selected_index == 'Air Temperature':
                        st.session_state['temp_image'] = get_era_temp_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_temp_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['temp_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='airtemp_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Land Surface Temperature':
                        st.session_state['lst_image'] = get_lst_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_lst_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['lst_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='lst_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Latent Heat Flux (LE)':
                        st.session_state['lhf_image'] = get_lhf_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_lhf_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['lhf_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='lhf_timeseries.csv',
                                mime='text/csv',
                                )
                    if selected_index == 'Potential Evapotranspiration (PET)':
                        st.session_state['pet_image'] = get_pet_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_pet_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['pet_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='pet_timeseries.csv',
                                mime='text/csv',
                                )
                    if selected_index == 'Leaf Area Index':
                        st.session_state['LAI_image'] = get_LAI_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_LAI_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['LAI_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='LAI_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Precipitation':
                        st.session_state['Precp_image'] = get_Precp_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_Precp_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['Precp_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='Precp_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Soil Moisture':
                        st.session_state['soil_moisture_image'] = get_soil_moisture_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_soil_moisture_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['soil_moisture_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='soil_moisture_timeseries.csv',
                                mime='text/csv',
                                )
                    if selected_index == 'Soil Temperature':
                        st.session_state['soil_temperature_image'] = get_soil_temperature_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_soil_temperature_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['soil_temperature_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='soil_temperature_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Transpiration (TP)':
                        st.session_state['transpiration_image'] = get_transpiration_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_transpiration_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['transpiration_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='transpiration_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Wind Speed':
                        st.session_state['windspeed_image'] = get_windspeed_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_windspeed_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['windspeed_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='windspeed_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Snow Cover':
                        st.session_state['snow_cover_image'] = get_snow_cover_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_snow_cover_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))

                        csv = st.session_state['snow_cover_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='snow_cover_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Keetch-Byram Drought Index':
                        st.session_state['kbdi_image'] = get_kbdi_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_kbdi_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        csv = st.session_state['kbdi_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='kbdi_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Evapotranspiration (ET)':
                        st.session_state['et_image'] = get_et_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_et_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        csv = st.session_state['et_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='et_timeseries.csv',
                                mime='text/csv',
                                )

                    if selected_index == 'Enhanced Vegetation Index (EVI)':
                        st.session_state['evi_image'] = get_evi_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_evi_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        csv = st.session_state['evi_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='evi_timeseries.csv',
                                mime='text/csv',
                                )
                    if selected_index == 'SRTM':
                        st.session_state['srtm_image'] = get_srtm_image(selected_sub_basin)
                    if selected_index == 'Population':
                        st.session_state['population_image'] = get_population_image(selected_sub_basin)
                    elif selected_index == 'Land Cover (2020)':
                        st.session_state['landcover_image'] = get_landcover_image(selected_sub_basin)
                        st.session_state['chart'] = None
                    if selected_index == 'NDVI':
                        st.session_state['ndvi_image'], st.session_state['ndvi_geometry'] = get_ndvi_image(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        st.session_state['chart'] = create_ndvi_timeseries(selected_sub_basin, st.session_state['from_date'].strftime('%Y-%m-%d'), st.session_state['to_date'].strftime('%Y-%m-%d'))
                        # st.pyplot(st.session_state['ndvi_chart']) #show chart in sidebar
                        # Convert chart data to CSV
                        csv = st.session_state['ndvi_chart_data'].to_csv(index=False)
                        st.download_button(
                                label="Download CSV",
                                data=csv,
                                file_name='ndvi_timeseries.csv',
                                mime='text/csv',
                                )

                    st.session_state['executed'] = True
                    # st.write("Execution complete, session state updated.")

            with download_col:
                if st.session_state['executed']:
                    if st.button(f'Save GeoTIFF'): #if st.button(f'Save {selected_index}'):
                        # Code to download the image
                        try:
                            if selected_index == 'SRTM':
                                try:
                                    download_url = st.session_state['srtm_image'].getDownloadURL({'scale': 90, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['srtm_image'].getDownloadURL({'scale': 90, 'dimensions': [2000,2000]})
                            elif selected_index == 'NDVI':
                                try:
                                    download_url = st.session_state['ndvi_image'].getDownloadURL({'scale': 250, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['ndvi_image'].getDownloadURL({'scale': 250, 'dimensions': [2000,2000]})
                            elif selected_index == 'Air Temperature':
                                try:
                                    download_url = st.session_state['temp_image'].getDownloadURL({'scale': 11132, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['temp_image'].getDownloadURL({'scale': 11132, 'dimensions': [2000,2000]})
                            elif selected_index == 'Enhanced Vegetation Index (EVI)':
                                try:
                                    download_url = st.session_state['evi_image'].getDownloadURL({'scale': 250, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['evi_image'].getDownloadURL({'scale': 250, 'dimensions': [2000,2000]})
                            elif selected_index == 'Evapotranspiration ET':
                                try:
                                    download_url = st.session_state['et_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['et_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Keetch-Byram Drought Index':
                                try:
                                    download_url = st.session_state['kbdi_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['kbdi_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Land Cover (2020)':
                                try:
                                    download_url = st.session_state['landcover_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['landcover_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Land Surface Temperature':
                                try:
                                    download_url = st.session_state['lst_image'].getDownloadURL({'scale': 1000, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['lst_image'].getDownloadURL({'scale': 1000, 'dimensions': [2000,2000]})
                            elif selected_index == 'Latent Heat Flux (LE)':
                                try:
                                    download_url = st.session_state['lhf_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['lhf_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Leaf Area Index':
                                try:
                                    download_url = st.session_state['LAI_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['LAI_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Population':
                                try:
                                    download_url = st.session_state['population_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['population_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Potential Evapotranspiration (PET)':
                                try:
                                    download_url = st.session_state['pet_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['pet_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Precipitation':
                                try:
                                    download_url = st.session_state['Precp_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['Precp_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Snow Cover':
                                try:
                                    download_url = st.session_state['snowcover_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['snowcover_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Soil Moisture':
                                try:
                                    download_url = st.session_state['soil_moisture_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['soil_moisture_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Soil Temperature':
                                try:
                                    download_url = st.session_state['soil_temperature_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['soil_temperature_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Transpiration (TP)':
                                try:
                                    download_url = st.session_state['tp_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['tp_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})
                            elif selected_index == 'Wind Speed':
                                try:
                                    download_url = st.session_state['windspeed_image'].getDownloadURL({'scale': 100, 'region': get_sub_basins_download(selected_basin).geometry(0.01).bounds(0.01)})
                                except:
                                    download_url = st.session_state['windspeed_image'].getDownloadURL({'scale': 100, 'dimensions': [2000,2000]})

                                # download_url = st.session_state['ndvi_image'].getDownloadURL({'scale': 20})
                            # elif selected_index == 'Air Temperature':
                            #     download_url = st.session_state['']


                            st.markdown(f"[Download {selected_index}]({download_url})", unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"An error occurred: {e}")

        if st.session_state['show_checkboxes']:
            cols1 = st.columns(2)
            cols2 = st.columns(2)
            cols3 = st.columns(2)
            with cols1[0]:
                st.session_state['airports'] = st.checkbox('Airports')
            with cols1[1]:
                st.session_state['rivers'] = st.checkbox('Rivers')

            with cols2[0]:
                st.session_state['streams'] = st.checkbox('Streams')
            with cols2[1]:
                st.session_state['railwayline'] = st.checkbox('Railway Lines')

            with cols3[0]:
                st.session_state['climate_stations'] = st.checkbox('Climate Stations')
            with cols3[1]:
                st.session_state['hydrometric_stations'] = st.checkbox('Hydrometric Stations')
            with cols3[0]:
                st.session_state['soiltypes'] = st.checkbox('Soil Types')
            with cols3[1]:
                st.session_state['subbasins_dl'] = st.checkbox('Sub Basins')

            
            zip_file_path = "shapefiles.rar"
            if st.button("Get Static Files"):
                st.download_button(label="Click to Download",
                                data=open(zip_file_path, 'rb').read(),
                                file_name="shapefiles.rar",
                                key="download_button")
            st.markdown("""
           <a href="https://www.freecounterstat.com" title="free website counter"><img src="https://counter11.optistats.ovh/private/freecounterstat.php?c=9exugmtzxfzsn1211myt1kqty11lfxmp" border="0" title="free website counter" alt="free website counter"></a>
            """, unsafe_allow_html=True)


    selected = option_menu(
        menu_title=None,
        options=["Home","Reload", "About & Disclaimer","Tutorial"],
        icons=["house","repeat", "book",'play'],
        menu_icon="Cast",
        orientation="horizontal"
    )

    if selected == "Home":
        # Display the map in the main area
        Map = display_map(
            selected_index=st.session_state['selected_index'],
            selected_basin=st.session_state['selected_basin'],
            selected_sub_basin=st.session_state['selected_sub_basin'],
            ndvi_image=st.session_state['ndvi_image'],
            temp_image=st.session_state['temp_image'],
            evi_image=st.session_state['evi_image'],
            srtm_image=st.session_state['srtm_image'],
            lst_image=st.session_state['lst_image'],
            lhf_image=st.session_state['lhf_image'],
            landcover_image=st.session_state['landcover_image'],
            et_image=st.session_state['et_image'],
            pet_image=st.session_state['pet_image'],
            kbdi_image=st.session_state['kbdi_image'],
            LAI_image=st.session_state['LAI_image'],
            Precp_image=st.session_state['Precp_image'],
            transpiration_image=st.session_state['transpiration_image'],
            soil_moisture_image=st.session_state['soil_moisture_image'],
            soil_temperature_image=st.session_state['soil_temperature_image'],
            snow_cover_image=st.session_state['snow_cover_image'],
            population_image=st.session_state['population_image'],
            windspeed_image=st.session_state['windspeed_image'],
            geojson_data=st.session_state.get('geojson_data'),
            min=st.session_state['min'],
            max=st.session_state['max'],
            area=st.session_state['area']

            # st.session_state.get('geojson_data')
        )

        Map.to_streamlit(height=600)

        if 'chart' in st.session_state and st.session_state['chart'] is not None:
            st.pyplot(st.session_state['chart'])
            # st.components.v1.html(st.session_state['chart'], height=1000) # for google charts API comment above unvomment this



    if selected == "About & Disclaimer":
        st.title("About")
        st.markdown("""<div style="text-align: justify;">The USAID funded Water Management for Enhanced Productivity (WMfEP) activity focuses on the productive and sustainable use of water for agricultural production in the Khyber Pakhtunkhwa province. WMfEP works on improving water governance and management to enable increased farm household income, improved livelihoods to contribute to social-economic development and political stability.The activity is structured into four components – Component 4 of the WMfEP is about increasing Afghanistan-Pakistan collaboration on water policy, practices, and water sector challenges in common and cross-border River Basins.
                This platform, developed under Comp-4, provides satellite-based time series analysis of topographic, physiographic, demographic, and climatic variables. Users can visualize spatial variation at the five transboundary basins to sub-basins between Afghanistan and Pakistan namely Kabul, Kurram, Gomal, Pishin Lora and Dori Kadanai. The platform even allows users to upload their desired study areas within five basins to visualize spatiotemporal variations. This platform also enables downloading the selected variables along with additional statistical layers.
                </div>""", unsafe_allow_html=True)
        st.title("Disclaimer")
        st.markdown("""<div style="text-align: justify;">This output was made possible through support provided by the U.S. Agency for International Development’s Mission to Pakistan (USAID/Pakistan) under the terms of Award No. 72039118IO00003. The information expressed in this output does not necessarily reflect the views of the U.S. Agency for International Development. The U.S. Agency for International Development does not take any responsibility for the accuracy or otherwise of any information presented in this output.</div>""" , unsafe_allow_html=True)

    if selected == "Reload":
        redirect("https://www.knowledge-platform.org/")

    if selected == "Tutorial":
        st.video('https://youtu.be/0JpEsW451Y8')

        user_manual_pdf = "user_manual.pdf"
        with open(user_manual_pdf, "rb") as file:
            pdf_bytes = file.read()
        
        base64_pdf = base64.b64encode(pdf_bytes).decode("utf-8")
        # pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="950" height="950" type="application/pdf"></iframe>'
        pdf_display = f'''<iframe src="data:application/pdf;base64,{base64_pdf}#toolbar=0&view=fitH" width="1000" height="950" style="border: none;"></iframe>'''
        st.markdown(pdf_display, unsafe_allow_html=True)

            
# Run the app
if __name__ == "__main__":
    main()
