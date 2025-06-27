import ee
import streamlit as st
try:
    def get_srtm_image(selected_sub_basin):
        if selected_sub_basin == 'None':
            return None
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        sub_basin_feature = dataset.filter(ee.Filter.eq('Sub_Basin', selected_sub_basin))
        srtm_data = ee.Image("CGIAR/SRTM90_V4").clip(sub_basin_feature)

        minMax = srtm_data.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=sub_basin_feature,
            scale=30,
            bestEffort=True
        )

        area = sub_basin_feature.geometry(0.01).area().divide(1e6)

        try:
            # Access min and max values from the minMax dictionary
            min_image = minMax.get('elevation_min')
            max_image = minMax.get('elevation_max')

            st.session_state['min'] = min_image.getInfo()
            st.session_state['max'] = max_image.getInfo()
            st.session_state['area'] = area.getInfo()
        except:
            st.session_state['min'] = 0
            st.session_state['max'] = 3000
            st.session_state['area'] = area.getInfo()
            
        return srtm_data

    def resize(image, new_width, new_height):
        # Get the projection information of the original image
        original_projection = image.projection()

        # Reproject the image to a new resolution
        srtm_data = image.reproject(crs=original_projection, scale=new_width)

        # Resample the image to the specified dimensions
        srtm_data = srtm_data.resample('bilinear').reproject(crs=original_projection, scale=new_height)
except Exception as e:
    st.write('Something Went Wrong!')