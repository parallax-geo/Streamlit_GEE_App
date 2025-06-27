import ee
import streamlit as st

try:
    def get_population_image(selected_sub_basin):
        if selected_sub_basin == 'None':
            return None
        dataset = ee.FeatureCollection('projects/ee-mspkafg/assets/1-final_validated_data/SubBasins')
        sub_basin_feature = dataset.filter(ee.Filter.eq('Sub_Basin', selected_sub_basin))
        population_data = ee.ImageCollection("WorldPop/GP/100m/pop_age_sex_cons_unadj").select('population').filterBounds(sub_basin_feature).filterDate('2020-01-01','2023-12-31').mean().clip(sub_basin_feature)
        print(population_data.getInfo())

        minMax = population_data.reduceRegion(
            reducer=ee.Reducer.minMax(),
            geometry=sub_basin_feature,
            scale=30,
            bestEffort=True
        )

        area = sub_basin_feature.geometry(0.01).area().divide(1e6)

        try:
            # Access min and max values from the minMax dictionary
            min_image = minMax.get('population_min')
            max_image = minMax.get('population_max')

            st.session_state['min'] = min_image.getInfo()
            st.session_state['max'] = max_image.getInfo()
            st.session_state['area'] = area.getInfo()
        except:
            st.session_state['min'] = 0
            st.session_state['max'] = 100
            st.session_state['area'] = area.getInfo()

        return population_data
except Exception as e:
    st.write('Something Went Wrong!')