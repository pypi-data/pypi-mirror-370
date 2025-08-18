DOWNLOAD_LINKS_DROPBOX = {
    'route_model': "https://www.dropbox.com/scl/fi/1kjivr13kyf6gn7wlhbzt/routing.zip?rlkey=zq8j501amqyirfprcgb9dquec&dl=1",
    'params': "https://www.dropbox.com/scl/fi/zvluibsnhz36k4smzcavv/params.zip?rlkey=uqbxdi4ulr9dv4u4imktf605m&st=r0qrt2gd&dl=1",
    'global_data': "https://www.dropbox.com/scl/fi/dhy3y3e9dw6tg89vt6x66/global_data.zip?rlkey=uvy6772cj5bpdfvtvqa4u8enj&st=4sti44e7&dl=1",
    'global_vic_params': "https://www.dropbox.com/s/jsg2wu62qi2ltwz/global_vic_params.zip?dl=1",
}

## For google drive link, https://drive.google.com/file/d/<ID>/view?usp=sharing, use https://drive.google.com/uc?id=<ID>
DOWNLOAD_LINKS_GOOGLE = {
    'route_model': "https://drive.google.com/uc?id=1zr3VH0wy-XN-yF2_n0xic89_PiT_V_Mb",
    'params': "https://drive.google.com/uc?id=1o5TH8GBmP4rjvFFROQmbid-ILMJw7xiS",
    'global_data': "https://drive.google.com/uc?id=1Obm_cKPFoumJKhcNTvFxIZNkSU3OmgT_",
    'global_vic_params': "https://drive.google.com/uc?id=16P95eu2yG0i77ac_NrmTSVutNtVXWNeA",
}

SUFFIXES_GLOBAL = {
    'GLOBAL': {
        'basin_shpfile': 'global_basin_data/shapefiles/mrb_basins.json',
        'elevation_tif_file': 'global_elevation_data/World_e-Atlas-UCSD_SRTM30-plus_v8.tif',
        'grwl': 'global_river_data/GRWL_summaryStats.shp'
    },

    'VIC': {
        'vic_global_param_dir': 'global_vic_params'
    },

    'ROUTING': {
        'global_flow_dir_tif_file': 'global_drt_flow_file/global_drt_flow_16th.tif',
        'stations_vector_file': 'global_dam_data/GRanD_dams_v1_3_filtered.shp'
    },

    'GEE': {
        'reservoir_vector_file': 'global_reservoir_data/GRanD_reservoirs_v1_3.shp'
    },

    'ALTIMETER': {
        'altimeter_tracks': 'global_altimetry/j3_tracks.geojson',
        'geoid_grid': 'global_altimetry/geoidegm2008grid.mat'
    },
}

SUFFIXES_NOTGLOBAL = {
    'GLOBAL': {
        'project_dir': '',
        'data_dir': 'data',
        'basins_metadata': 'params/basins_metadata.csv'
    },

    'METSIM':{
        'metsim_env': 'models/metsim',
        'metsim_param_file': 'params/metsim/params.yaml'
    },

    'VIC': {
        'vic_env': 'models/vic',
        'vic_param_file': 'params/vic/vic_params.txt',
    },

    'ROUTING': {
        'route_model': 'models/routing/rout',
        'route_param_file': 'params/routing/route_param.txt',
    },

    'ROUTING PARAMETERS':{
        'uh': 'params/routing/uh.txt'
    }
}

