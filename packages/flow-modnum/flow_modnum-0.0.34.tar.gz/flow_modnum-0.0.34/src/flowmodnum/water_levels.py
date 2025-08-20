import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.ticker import ScalarFormatter
import matplotlib.dates as mdates
import os
import sys
from pathlib import Path
import shutil
import folium
import fiona
import plotly.express as px
import plotly.io as pio
from pyproj import Transformer
from tqdm import tqdm
import plotly.graph_objects as go
import geopandas as gpd
import fiona
from shapely.geometry import LineString, mapping, Polygon
from scipy.interpolate import griddata
from skimage import measure
import subprocess

def get_executable_path(executable):
    base_path = Path(__file__).parent
    exe_path = base_path /'exe'/executable
    return f'"{str(exe_path)}"'

def plot_hydrograms(obs_dir, model_dir, wells_dir, scale, date_ini, format_date='%d/%m/%Y', lang='EN'):
    """
    Function to plot water level hydrograms form MODFLOW-USG output files.
    
    Arguments:
    
    obs_dir: (str) Directory to observation data. Format as John Doherty's Groundwater Utilities.
    model_dir: (str) Directory to model files.
    wells_dir: (str) Directory to table containing wells. Columns must be: "Well_Name" "X_Coordinate" "Y_Coordinate" "Model_Layer"
    scale: (float/int) Vertical scale (+- from mean values)
    date_ini: (str) Initial date. Must be the same format as format_date.
    format_date: (str) (Optional) Date format to build DataFrames. Default is '%d/%m/%Y'
    lang: (str) (Optional) Language. Can choose between EN and SP. Default is EN.
    
    Outputs: Folder with hydrograms for each well.
    
    """
    # Current working directory
    cwd = os.getcwd()
    
    # Settings file
    with open('settings.fig', 'w', encoding='utf-8', newline='\n') as f:
        f.writelines('date={}\n'.format(format_date.replace('%d','dd').replace('%m','mm').replace('%Y','yyyy')))
        f.writelines('colrow=yes')
    f.close()
    
    # Directories for plots
    plot_dir = os.path.join(cwd, 'graphs')
    if not os.path.exists(plot_dir):
        os.makedirs(plot_dir)
    if os.path.exists(plot_dir):
        shutil.rmtree(plot_dir)
        os.makedirs(plot_dir)
    
    # Model files
    for file in os.listdir(model_dir):
        if file.endswith('.gsf'):
            gsf_file = file
        elif file.endswith('.dis'):
            dis_file = file
        elif (file.endswith('.hds')) and ('cln' not in file):
            hds_file = file
            
    ## run quadfac to obtain factors
    quadfac='usg_quadfac.in'
    with open(os.path.join(cwd,quadfac),'w') as g:
        g.writelines('{} \n'.format(os.path.join(model_dir, gsf_file)))
        g.writelines('n \n')
        g.writelines('0 \n')
        g.writelines('{} \n'.format(os.path.join(model_dir, dis_file)))
        g.writelines('{}'.format(wells_dir) +'\n')
        g.writelines('{}'.format(wells_dir) +'\n')
        g.writelines('factors.dat' +'\n')
        g.writelines('1')
    g.close()
    run_file='quadfac.bat'
    with open(os.path.join(cwd,run_file),'w') as g:
        g.writelines('"{}"<{} \n'.format(get_executable_path('usgquadfac.exe'), quadfac))
    g.close()
    os.system(run_file)
    #os.remove(os.path.join(cwd,run_file))
    
    # run mod2smp to obtain simulated values
    ins_file = 'mod2smp.in'
    with open(os.path.join(cwd,ins_file), 'w') as f:
        f.write('factors.dat' + '\n')
        f.write('{}'.format(wells_dir) + '\n')
        f.write('g' + '\n')
        f.write('y' + '\n')
        f.write('{}'.format(os.path.join(model_dir, hds_file)) + '\n')
        f.write(str(999999)+'\n')
        f.write(str(5000)+'\n')
        f.write("d" + '\n')
        f.write("{}".format(date_ini) + '\n')
        f.write("00:00:00" + '\n')
        f.write("niveles_simulados.smp" + '\n')
    run_file = 'mod2smp.bat'
    with open(os.path.join(cwd,run_file),'w') as g: 
        g.writelines('"{}"<{} \n'.format(get_executable_path('usgmod2smp.exe'), ins_file))
    g.close()
    os.system(run_file)
    #os.remove(os.path.join(cwd,run_file))
    
    # Dataframes are loaded
    df_sim = pd.read_csv('niveles_simulados.smp', sep=r'\s+', header=None)
    df_sim.columns=['well', 'date', 'time', 'water_level']
    df_sim['well'] = df_sim.well.str.upper()
    df_sim['date'] = pd.to_datetime(df_sim.date, format=format_date)

    df_obs = pd.read_csv(obs_dir, sep=r'\s+', header=None)
    df_obs.columns=['well', 'date', 'time', 'water_level']
    df_obs['well'] = df_obs.well.str.upper()
    df_obs['date'] = pd.to_datetime(df_obs.date, format=format_date)
    
    # Delete files
    os.remove(os.path.join(cwd, 'factors.dat'))
    os.remove(os.path.join(cwd, 'mod2smp.in'))
    os.remove(os.path.join(cwd, 'niveles_simulados.smp'))
    os.remove(os.path.join(cwd, 'settings.fig'))
    os.remove(os.path.join(cwd, 'usg_quadfac.in'))
    
    for well in df_obs.well.unique():
        # Hydrograms
        fig, axs = plt.subplots(1, figsize=(7,5))

        # Plot simulated and observed data
        if lang == 'EN':
            axs.scatter(df_obs.loc[df_obs.well == well]['date'], df_obs.loc[df_obs.well == well]['water_level'], label='Observed', color='black')
            axs.plot(df_sim.loc[df_sim.well == well]['date'], df_sim.loc[df_sim.well == well]['water_level'], label='Simulated')
            
            # Axis format
            axs.set_ylabel('Water Level (msnm)')
            axs.legend()
            axs.set_title(well)
            axs.xaxis.set_major_locator(mdates.YearLocator(1)) 
            axs.xaxis.set_tick_params(rotation=45)
            axs.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        elif lang=='SP':
            axs.scatter(df_obs.loc[df_obs.well == well]['date'], df_obs.loc[df_obs.well == well]['water_level'], label='Observado', color='black')
            axs.plot(df_sim.loc[df_sim.well == well]['date'], df_sim.loc[df_sim.well == well]['water_level'], label='Simulado')
            
            # Axis format
            axs.set_ylabel('Nivel (msnm)')
            axs.legend()
            axs.set_title(well)
            axs.xaxis.set_major_locator(mdates.YearLocator(1)) 
            axs.xaxis.set_tick_params(rotation=45)
            axs.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))

        # Vertical scale
        means = (df_obs.loc[df_obs.well == well]['water_level'].mean()+df_sim.loc[df_sim.well == well]['water_level'].mean())/2
        maxs = max(df_obs.loc[df_obs.well == well]['water_level'].max(), df_sim.loc[df_sim.well == well]['water_level'].max())
        mins = min(df_obs.loc[df_obs.well == well]['water_level'].min(), df_sim.loc[df_sim.well == well]['water_level'].min())
        maxs = means+maxs-mins
        mins = means-maxs+mins
        maxs = max(maxs, means+scale)
        mins = min(mins, means-scale)
        axs.set_ylim(mins, maxs)

        # Save plot
        plt.savefig(os.path.join(plot_dir, well+'.png'), dpi=300)
        plt.close()
        fig.clear()

def plot_fit(obs_dir, model_dir, wells_dir, date_ini, format_date='%d/%m/%Y', lang='EN'):
    """
    Function to plot simulated fit to observed data from MODFLOW-USG output files.
    
    Arguments:
    
    obs_dir: (str) Directory to observation data. Format as John Doherty's Groundwater Utilities.
    model_dir: (str) Directory to model files.
    wells_dir: (str) Directory to table containing wells. Columns must be: "Well_Name" "X_Coordinate" "Y_Coordinate" "Model_Layer"
    scale: (float/int) Vertical scale (+- from mean values)
    date_ini: (str) Initial date. Must be the same format as format_date.
    format_date:(str) (Optional) Date format to build DataFrames. Default is '%d/%m/%Y'
    lang: (str) (Optional) Language. Can choose between EN and SP. Default is EN.
    
    Output: Fit plot image.
    """
    # Current working directory
    cwd = os.getcwd()
    
    # Settings file
    with open('settings.fig', 'w') as f:
        f.writelines('date={}\n'.format(format_date.replace('%d','dd').replace('%m','mm').replace('%Y','yyyy')))
        f.writelines('colrow=yes')
    f.close()
    
    # Model files
    for file in os.listdir(model_dir):
        if file.endswith('.gsf'):
            gsf_file = file
        elif file.endswith('.dis'):
            dis_file = file
        elif (file.endswith('.hds')) and ('cln' not in file):
            hds_file = file
    
    ## run quadfac to obtain factors
    quadfac='usg_quadfac.in'
    with open(os.path.join(cwd,quadfac),'w') as g:
        g.writelines('{} \n'.format(os.path.join(model_dir, gsf_file)))
        g.writelines('n \n')
        g.writelines('0 \n')
        g.writelines('{} \n'.format(os.path.join(model_dir, dis_file)))
        g.writelines('{}'.format(wells_dir) +'\n')
        g.writelines('{}'.format(wells_dir) +'\n')
        g.writelines('factors.dat' +'\n')
        g.writelines('1')
    g.close()
    run_file='quadfac.bat'
    with open(os.path.join(cwd,run_file),'w') as g:
        g.writelines('{}<{} \n'.format(get_executable_path('usgquadfac.exe'), quadfac))
    g.close()
    os.system(run_file)
    os.remove(os.path.join(cwd,run_file))
    
    # run mod2obs to obtain simulated values interpolated to observed values
    ins_file = 'mod2obs.in'
    with open(os.path.join(cwd,ins_file), 'w') as f:
        f.write('factors.dat' + '\n')
        f.write('{}'.format(wells_dir) + '\n')
        f.write('g' + '\n')
        f.write('y' + '\n')
        f.write('{}'.format(obs_dir) + '\n')
        f.write('{}'.format(os.path.join(model_dir, hds_file)) + '\n')
        f.write(str(5000)+'\n')
        f.write("d" + '\n')
        f.write("{}".format(date_ini) + '\n')
        f.write("00:00:00" + '\n')
        f.write(str(15) + '\n')
        f.write("niveles_simulados.mod2obs" + '\n')
    run_file = 'mod2obs.bat'
    with open(os.path.join(cwd,run_file),'w') as g: 
        g.writelines('{}<{} \n'.format(get_executable_path('usgmod2obs.exe'), ins_file))
    g.close()
    os.system(run_file)
    os.remove(os.path.join(cwd,run_file))
    
    # Dataframes are generated
    df_mod2obs = pd.read_csv('niveles_simulados.mod2obs', sep=r'\s+', header=None)
    df_mod2obs.columns=['well', 'date', 'time', 'water_level']
    df_mod2obs['well'] = df_mod2obs.well.str.upper()
    df_mod2obs['date'] = pd.to_datetime(df_mod2obs.date, format=format_date)

    df_obs = pd.read_csv(obs_dir, sep=r'\s+', header=None)
    df_obs.columns=['well', 'date', 'time', 'water_level']
    df_obs['well'] = df_obs.well.str.upper()
    df_obs['date'] = pd.to_datetime(df_obs.date, format='%d/%m/%Y')
    
    # Remove files
    os.remove(os.path.join(cwd, 'factors.dat'))
    os.remove(os.path.join(cwd, 'mod2obs.in'))
    os.remove(os.path.join(cwd, 'niveles_simulados.mod2obs'))
    os.remove(os.path.join(cwd, 'settings.fig'))
    os.remove(os.path.join(cwd, 'usg_quadfac.in'))
    
    # Plot is generated
    fig, axs = plt.subplots(1, figsize=(7,7))

    # Plot 1:1 fit line
    maxs = max(df_obs['water_level'].max(), df_mod2obs['water_level'].max())
    mins = min(df_obs['water_level'].min(), df_mod2obs['water_level'].min())
    axs.plot([0,maxs], [0,maxs], color='red')

    # Plot model fit
    axs.scatter(df_obs['water_level'], df_mod2obs['water_level'], s=6)

    # Format axes and save figure
    if lang == 'EN':
        axs.set_xlabel('Observed (msnm)')
        axs.set_ylabel('Simulated (msnm)')
        axs.set_ylim(mins,maxs)
        axs.set_xlim(mins,maxs)

        plt.savefig(os.path.join(cwd, 'fit.png'), dpi=300)
    elif lang == 'SP':
        axs.set_xlabel('Nivel Observado (msnm)')
        axs.set_ylabel('Nivel Simulado (msnm)')
        axs.set_ylim(mins,maxs)
        axs.set_xlim(mins,maxs)

        plt.savefig(os.path.join(cwd, 'ajuste.png'), dpi=300)

def get_stats(obs_dir, model_dir, wells_dir, date_ini, format_date='%d/%m/%Y', lang='EN'):
    """
    Function to generate table with fit statistics from MODFLOW-USG output files.
    
    Arguments:
    
    obs_dir: (str) Directory to observation data. Format as John Doherty's Groundwater Utilities.
    model_dir: (str) Directory to model files.
    wells_dir: (str) Directory to table containing wells. Columns must be: "Well_Name" "X_Coordinate" "Y_Coordinate" "Model_Layer"
    scale: (float/int) Vertical scale (+- from mean values)
    date_ini: (str) Initial date. Must be the same format as format_date.
    format_date: (str) (Optional) Date format to build DataFrames. Default is '%d/%m/%Y'
    lang: (str) (Optional) Language. Can choose between EN and SP. Default is EN.
    
    Output: Fit stats on .csv file.
    """
    # Current working directory
    cwd = os.getcwd()
    
    # Settings file
    with open('settings.fig', 'w') as f:
        f.writelines('date={}\n'.format(format_date.replace('%d','dd').replace('%m','mm').replace('%Y','yyyy')))
        f.writelines('colrow=yes')
    f.close()
    
    # Model files
    for file in os.listdir(model_dir):
        if file.endswith('.gsf'):
            gsf_file = file
        elif file.endswith('.dis'):
            dis_file = file
        elif (file.endswith('.hds')) and ('cln' not in file):
            hds_file = file
    
    ## run quadfac to obtain factors
    quadfac='usg_quadfac.in'
    with open(os.path.join(cwd,quadfac),'w') as g:
        g.writelines('{} \n'.format(os.path.join(model_dir, gsf_file)))
        g.writelines('n \n')
        g.writelines('0 \n')
        g.writelines('{} \n'.format(os.path.join(model_dir, dis_file)))
        g.writelines('{}'.format(wells_dir) +'\n')
        g.writelines('{}'.format(wells_dir) +'\n')
        g.writelines('factors.dat' +'\n')
        g.writelines('1')
    g.close()
    run_file='quadfac.bat'
    with open(os.path.join(cwd,run_file),'w') as g:
        g.writelines('{}<{} \n'.format(get_executable_path('usgquadfac.exe'), quadfac))
    g.close()
    os.system(run_file)
    os.remove(os.path.join(cwd,run_file))
    
    # run mod2obs to obtain simulated values interpolated to observed values
    ins_file = 'mod2obs.in'
    with open(os.path.join(cwd,ins_file), 'w') as f:
        f.write('factors.dat' + '\n')
        f.write('{}'.format(wells_dir) + '\n')
        f.write('g' + '\n')
        f.write('y' + '\n')
        f.write('{}'.format(obs_dir) + '\n')
        f.write('{}'.format(os.path.join(model_dir, hds_file)) + '\n')
        f.write(str(5000)+'\n')
        f.write("d" + '\n')
        f.write("{}".format(date_ini) + '\n')
        f.write("00:00:00" + '\n')
        f.write(str(15) + '\n')
        f.write("niveles_simulados.mod2obs" + '\n')
    run_file = 'mod2obs.bat'
    with open(os.path.join(cwd,run_file),'w') as g: 
        g.writelines('{}<{} \n'.format(get_executable_path('usgmod2obs.exe'), ins_file))
    g.close()
    os.system(run_file)
    os.remove(os.path.join(cwd,run_file))
    
    # Dataframes are generated
    df_mod2obs = pd.read_csv('niveles_simulados.mod2obs', sep=r'\s+', header=None)
    df_mod2obs.columns=['well', 'date', 'time', 'water_level']
    df_mod2obs['well'] = df_mod2obs.well.str.upper()
    df_mod2obs['date'] = pd.to_datetime(df_mod2obs.date, format=format_date)

    df_obs = pd.read_csv(obs_dir, sep=r'\s+', header=None)
    df_obs.columns=['well', 'date', 'time', 'water_level']
    df_obs['well'] = df_obs.well.str.upper()
    df_obs['date'] = pd.to_datetime(df_obs.date, format='%d/%m/%Y')
    
    # Remove files
    os.remove(os.path.join(cwd, 'factors.dat'))
    os.remove(os.path.join(cwd, 'mod2obs.in'))
    os.remove(os.path.join(cwd, 'niveles_simulados.mod2obs'))
    os.remove(os.path.join(cwd, 'settings.fig'))
    os.remove(os.path.join(cwd, 'usg_quadfac.in'))
    
    # Absolute and squared errors are calculated
    df_fit = df_mod2obs.copy()
    df_fit.rename({'water_level':'simulated'}, axis=1, inplace=True)
    df_fit['observed'] = df_obs['water_level']
    df_fit['r'] = np.abs(df_fit.simulated - df_fit.observed)
    df_fit['r2'] = df_fit.r**2
    
    # MAE and RMS are calculated
    mae = df_fit.r.sum()/len(df_fit)
    rms = np.sqrt(df_fit.r2.sum()/len(df_fit))
    
    # Observed range
    min_obs = df_fit.observed.min()
    max_obs = df_fit.observed.max()
    range_obs = max_obs-min_obs
    
    # KGE is calculated
    mean_sim = df_fit.simulated.mean()
    mean_obs = df_fit.observed.mean()
    std_sim = df_fit.simulated.std()
    std_obs = df_fit.observed.std()
    correlation = df_fit[['simulated', 'observed']].corr().iloc[0, 1]
    beta = mean_sim / mean_obs
    gamma = (std_sim / mean_sim) / (std_obs / mean_obs)
    kge = 1 - np.sqrt((correlation - 1)**2 + (beta - 1)**2 + (gamma - 1)**2)

    # Stats are generated as csv
    if lang=='EN':
        df = pd.DataFrame({'Parameter':['Total wells', 'Total points', 'Minimum observed (msnm)', 'Maximum observed (msnm)', 'Observed range Max - Min (m)', 'MAE (m)', 'NMAE (%)', 'RMS (m)', 'NRMS (%)', 'KGE'],
                    'Transient calibration':[len(df_fit.well.unique()),len(df_fit),min_obs,max_obs,range_obs,mae,100*mae/range_obs,rms,100*rms/range_obs, kge]})
        df.to_csv(os.path.join(cwd, 'stats.csv'), encoding='latin-1', index=False)
    elif lang=='SP':
        df = pd.DataFrame({'Parámetro':['Total pozos', 'Total datos', 'Mínimo Observado (msnm)', 'Máximo observado (msnm)', 'Rango de Observaciones Máx - Min (m)', 'MAE (m)', 'NMAE (%)', 'RMS (m)', 'NRMS (%)', 'KGE'],
                    'Calibración Transiente':[len(df_fit.well.unique()),len(df_fit),min_obs,max_obs,range_obs,mae,100*mae/range_obs,rms,100*rms/range_obs, kge]})
        df.to_csv(os.path.join(cwd, 'estadisticos.csv'), encoding='latin-1', index=False)

def mapped_hydrograms(obs_dir, model_dir, EPSG, wells_dir, date_ini, format_date='%d/%m/%Y', lang='EN', grid_dir=None):
    """
    Function to plot water level hydrograms on map from MODFLOW-USG output files.
    
    Arguments:
    
    obs_dir: (str) Directory to observation data. Format as John Doherty's Groundwater Utilities.
    model_dir: (str) Directory to model files.
    EPSG: (int) EPSG code to which all coordinated are referenced.
    wells_dir: (str) Directory to table containing wells. Columns must be: "Well_Name" "X_Coordinate" "Y_Coordinate" "Model_Layer"
    scale: (float) Vertical scale (+- from mean values)
    date_ini: (str) Initial date. Must be the same format as format_date.
    format_date: (str)(Optional) Date format to build DataFrames. Default is '%d/%m/%Y'
    lang: (str) (Optional) Language. Can choose between EN and SP. Default is EN.
    grid_dir: (str) (Optional) Directory to model grid to plot on map. Shapefile format. Must be referenced to EPSG.
    
    Outputs: .html file with interactive map with wells. Each wells shows hydrograms on click.
    """
    # Current working directory
    cwd = os.getcwd()
    
    # Settings file
    with open('settings.fig', 'w') as f:
        f.writelines('date={}\n'.format(format_date.replace('%d','dd').replace('%m','mm').replace('%Y','yyyy')))
        f.writelines('colrow=yes')
    f.close()
    
    # Model files
    for file in os.listdir(model_dir):
        if file.endswith('.gsf'):
            gsf_file = file
        elif file.endswith('.dis'):
            dis_file = file
        elif (file.endswith('.hds')) and ('cln' not in file):
            hds_file = file
            
    ## run quadfac to obtain factors
    quadfac='usg_quadfac.in'
    with open(os.path.join(cwd,quadfac),'w') as g:
        g.writelines('{} \n'.format(os.path.join(model_dir, gsf_file)))
        g.writelines('n \n')
        g.writelines('0 \n')
        g.writelines('{} \n'.format(os.path.join(model_dir, dis_file)))
        g.writelines('{}'.format(wells_dir) +'\n')
        g.writelines('{}'.format(wells_dir) +'\n')
        g.writelines('factors.dat' +'\n')
        g.writelines('1')
    g.close()
    run_file='quadfac.bat'
    with open(os.path.join(cwd,run_file),'w') as g:
        g.writelines('{}<{} \n'.format(get_executable_path('usgquadfac.exe'), quadfac))
    g.close()
    os.system(run_file)
    os.remove(os.path.join(cwd,run_file))
    
    # run mod2smp to obtain simulated values
    ins_file = 'mod2smp.in'
    with open(os.path.join(cwd,ins_file), 'w') as f:
        f.write('factors.dat' + '\n')
        f.write('{}'.format(wells_dir) + '\n')
        f.write('g' + '\n')
        f.write('y' + '\n')
        f.write('{}'.format(os.path.join(model_dir, hds_file)) + '\n')
        f.write(str(999999)+'\n')
        f.write(str(5000)+'\n')
        f.write("d" + '\n')
        f.write("{}".format(date_ini) + '\n')
        f.write("00:00:00" + '\n')
        f.write("niveles_simulados.smp" + '\n')
    run_file = 'mod2smp.bat'
    with open(os.path.join(cwd,run_file),'w') as g: 
        g.writelines('{}<{} \n'.format(get_executable_path('usgmod2smp.exe'), ins_file))
    g.close()
    os.system(run_file)
    os.remove(os.path.join(cwd,run_file))
    
    # Dataframes are loaded
    df_sim = pd.read_csv('niveles_simulados.smp', sep=r'\s+', header=None)
    df_sim.columns=['well', 'date', 'time', 'water_level']
    df_sim['well'] = df_sim.well.str.upper()
    df_sim['date'] = pd.to_datetime(df_sim.date, format=format_date)

    df_obs = pd.read_csv(obs_dir, sep=r'\s+', header=None)
    df_obs.columns=['well', 'date', 'time', 'water_level']
    df_obs['well'] = df_obs.well.str.upper()
    df_obs['date'] = pd.to_datetime(df_obs.date, format=format_date)

    # Delete files
    os.remove(os.path.join(cwd, 'factors.dat'))
    os.remove(os.path.join(cwd, 'mod2smp.in'))
    os.remove(os.path.join(cwd, 'niveles_simulados.smp'))
    os.remove(os.path.join(cwd, 'settings.fig'))
    os.remove(os.path.join(cwd, 'usg_quadfac.in'))
    
    # Read table with wells coordinates
    wells = pd.read_csv(wells_dir, sep='\t', header=None)
    wells.columns = ['well', 'x', 'y', 'model_layer']

    # Convert EPSG to WGS84
    transformer = Transformer.from_crs("EPSG:{}".format(EPSG), "EPSG:4326", always_xy=True)
    def convert_psad56_to_wgs84(easting, northing):
        lon, lat = transformer.transform(easting, northing)
        return lat, lon
    wells[['Lat', 'Lon']] = wells.apply(lambda row: convert_psad56_to_wgs84(row['x'], row['y']), axis=1, result_type='expand')

    # Create map centered con coordinates mean values
    m = folium.Map(location=[wells['Lat'].mean(), wells['Lon'].mean()], zoom_start=12, tiles=None)
    folium.TileLayer('Esri.WorldImagery').add_to(m)

    # Add grid map 
    if grid_dir:
        # Read grid file and convert to WGS84
        gdf = gpd.read_file(grid_dir)
        gdf.crs = EPSG
        gdf.to_crs(epsg=4326)
        
        # Add to map with folium
        folium.GeoJson(
            gdf.dissolve(),
            style_function=lambda x: {
                'color': 'black',       # Boundary color
                'weight': 2,            # Boundary thickness
                'fillColor': 'transparent'  # Transparent fill color
            }
        ).add_to(m)

    # Function to create hydrograms
    def hydrogram(df_sim, df_obs):
        # Scale: Default at 3. Can be modified on map
        means = (df_obs.water_level.mean()+df_sim.water_level.mean())/2
        maxs = max(df_obs.water_level.max(), df_sim.water_level.max())
        mins = min(df_obs.water_level.max(), df_sim.water_level.max())
        maxs = means+(maxs-mins)
        mins = means-(maxs-mins)
        maxs = max(maxs, means+3)
        mins = min(mins, means-3)
        
        fig = go.Figure()
        if lang == 'EN':
            fig.add_trace(go.Scatter(x=df_obs.date, y=df_obs.water_level, mode='markers', name='Observed'))
            fig.add_trace(go.Scatter(x=df_sim.date, y=df_sim.water_level, mode='lines', name='Simulated'))
            
            fig.update_layout(
                    title=f'Well {well}',
                    xaxis_title='Date',
                    yaxis_title='Water level (msnm)',
                    yaxis_range = [mins, maxs],
                )
            return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')
            
        elif lang =='SP':
            fig.add_trace(go.Scatter(x=df_obs.date, y=df_obs.water_level, mode='markers', name='Observado'))
            fig.add_trace(go.Scatter(x=df_sim.date, y=df_sim.water_level, mode='lines', name='Simulado'))
        
            fig.update_layout(
                    title=f'Pozo {well}',
                    xaxis_title='Fecha',
                    yaxis_title='Nivel (msnm)',
                    yaxis_range = [mins, maxs],
                )
            return pio.to_html(fig, full_html=False, include_plotlyjs='cdn')

    # Add each well to map with plot on popup
    for _, row in tqdm(wells.iterrows(), total=len(wells)):
        well = row.well
        df_temp_sim = df_sim.loc[df_sim.well == well]
        df_temp_obs = df_obs.loc[df_obs.well == well]
        html_plot = hydrogram(df_temp_sim, df_temp_obs)
        iframe = folium.IFrame(html=html_plot, width=500, height=300)
        popup = folium.Popup(iframe, max_width=500)
        
        if lang == 'EN':
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                popup=popup,
                tooltip=f"Well {row['well']}",
                radius=3,               # Tamaño del punto
                color='black',          # Color del borde del punto
                fill=True,              # Relleno del punto
                fill_color='black',     # Color de relleno
                fill_opacity=1          # Opacidad del punto
            ).add_to(m)
            
        elif lang == 'SP':
            folium.CircleMarker(
                location=[row['Lat'], row['Lon']],
                popup=popup,
                tooltip=f"Pozo {row['well']}",
                radius=3,               # Tamaño del punto
                color='black',          # Color del borde del punto
                fill=True,              # Relleno del punto
                fill_color='black',     # Color de relleno
                fill_opacity=1          # Opacidad del punto
            ).add_to(m)
    if lang == 'EN':
        m.save('Mapped_Hydrograms.html')
    elif lang == 'SP':
        m.save('Mapa_Hidrogramas.html')

def generate_contours(model_dir, date_ini, layers, sps, EPSG, levels, dry_cells = -999.99):
    """
    Function to generate water level contours (shapefiles) from MODFLOW-USG output file. 
    
    Arguments:
    
    model_dir: (str) Directory to MODFLOW-USG model files.
    gsf_dir: (str) Directory to MODFLOW-USG .gsf file.
    date_ini: (str) Initial date of model. Format dd/mm/YYYY.
    layers: (list) Layers to extract contours of water levels.
    sps: (list) Stress periods to extract contours of water levels.
    EPSG: (int) EPSG code to which all coordinated are referenced.
    levels: (list) Contours levels
    dry_cells: (float) (Optional) Value assigned to dry cells by model.
    
    Outputs: Folder with shapefiles for desired contours.
    """
    
    # Current working directory
    cwd = os.getcwd()
    
    # Directories for piezometry
    piezo_dir = os.path.join(cwd, 'piezo')
    if not os.path.exists(piezo_dir):
        os.makedirs(piezo_dir)
    if os.path.exists(piezo_dir):
        shutil.rmtree(piezo_dir)
        os.makedirs(piezo_dir)
    
    # Model files
    for file in os.listdir(model_dir):
        if file.endswith('.gsf'):
            gsf_file = file
        elif (file.endswith('.hds')) and ('cln' not in file):
            hds_file = file
            
    # usgarrdet to extract times of results
    with open(os.path.join(cwd, 'usgarrdet.in'), 'w') as g:
        g.writelines(os.path.join(model_dir, hds_file)+'\n')
        g.writelines('h\n')
        g.writelines('g\n')
        g.writelines('times_heads.dat\n')
    g.close()
    run_file='usgarrdet.bat'
    with open(os.path.join(cwd,run_file),'w') as g:
        g.writelines('{}<{} \n'.format(get_executable_path('usgarrdet.exe'),'usgarrdet.in'))
    g.close()
    os.system(run_file)

    # Read times for which there are heads
    times_heads = pd.read_csv(os.path.join(cwd,'times_heads.dat'), sep=r"\s+")
    totim_list_heads = times_heads.TOTIM.unique().astype(float)

    # Remove usgarrdet files
    os.remove(os.path.join(cwd, 'usgarrdet.bat'))
    os.remove(os.path.join(cwd, 'usgarrdet.in'))
    os.remove(os.path.join(cwd, 'times_heads.dat'))
    
    # usgbin2tab for each TOTIM to extract heads results for specific stress periods
    for idx, totim in enumerate(totim_list_heads):  
        if idx+1 in sps:
            with open(os.path.join(cwd,'usgbin2tab.in'),'w') as g:
                g.writelines(os.path.join(model_dir, hds_file)+'\n')
                g.writelines(str(totim)+'\n')
                g.writelines(piezo_dir+'\\'+'HEADS_'+str(idx+1)+'.dat\n')
            g.close()  
            run_file='usgbin2tab.bat'
            with open(os.path.join(cwd,run_file),'w') as g:
                g.writelines('{}<{} \n'.format(get_executable_path('usgbin2tab_h.exe'), 'usgbin2tab.in'))
            g.close()
            os.system(run_file)
    
    # Remove usgbin2tab files
    os.remove(os.path.join(cwd, 'usgbin2tab.in'))
    os.remove(os.path.join(cwd, 'usgbin2tab.bat'))
    
    ## Shapefiles are constructed
    # Date
    date_ini = pd.to_datetime(date_ini, format='%d/%m/%Y')
    date_ini = pd.Timestamp(date_ini)

    for layer in layers:
        # Extract x, y, z with usggridlay for specific layer
        with open(os.path.join(cwd,'usggridlay.in'),'w') as g:
            g.writelines(os.path.join(model_dir, gsf_file)+'\n')
            g.writelines(str(layer)+'\n')
            g.writelines('\n')
            g.writelines('\n')
            g.writelines(str('xyz_base.dat')+'\n')
            g.writelines('n'+'\n')
        g.close()  
        run_file='usggridlay.bat'
        with open(os.path.join(cwd,run_file),'w') as g:
            g.writelines('{}<{} \n'.format(get_executable_path('usggridlay.exe'), 'usggridlay.in'))
        g.close()
        os.system(run_file)

        xyz_data = pd.read_csv(os.path.join(cwd, 'xyz_base.dat'), sep=r'\s+')
        
        # Remove usggridlay files
        os.remove(os.path.join(cwd, 'usggridlay.in'))
        os.remove(os.path.join(cwd, 'usggridlay.bat'))
        os.remove(os.path.join(cwd, 'xyz_base.dat'))
  
        for sp in sps:
            # Date for files
            date = date_ini+pd.DateOffset(months=sp)-pd.DateOffset(days=1)
            date_str = date.strftime('%Y-%m-%d')
            
            # Extract results for given stress period
            head = pd.read_csv(os.path.join(piezo_dir, 'HEADS_{}.dat'.format(sp)), sep=r'\s+')
            
            # Merge coordinates with head results
            df = pd.merge(left=xyz_data, right=head, left_on='NODE_NUMBER', right_on='NODE_NUMBER', how='left')
            
            # Replace dry cells
            df.loc[df.HEADU==dry_cells, 'HEADU'] = np.nan

            # X, Y coordinates and head results
            x = df['X'].values
            y = df['Y'].values
            head = df['HEADU'].values
            
            # Create regular grid
            grid_x, grid_y = np.meshgrid(np.linspace(x.min(), x.max(), 100),
                                        np.linspace(y.min(), y.max(), 100))

            # Interpolate HEAD values to new grid
            grid_z = griddata((x, y), head, (grid_x, grid_y), method='cubic')

            # Extract contours with skimage
            contour_lines = []
            contour_levels = []

            for level in levels:
                contours = measure.find_contours(grid_z, level)
                for contour in contours:
                    # Convert matrix index to real coordinates
                    line_coords = np.column_stack([
                        np.interp(contour[:, 1], np.arange(grid_x.shape[1]), grid_x[0]),
                        np.interp(contour[:, 0], np.arange(grid_y.shape[0]), grid_y[:, 0])
                    ])
                    contour_lines.append(LineString(line_coords))
                    contour_levels.append(level)

            # Crear esquema para shapefile
            schema = {
                'geometry': 'LineString',
                'properties': {'level': 'float'}
            }

            # Guardar como shapefile usando Fiona
            with fiona.open(os.path.join(piezo_dir, "Heads_{}_{}.shp".format(layer, date_str)), "w", 
                            driver="ESRI Shapefile", schema=schema, crs="EPSG:{}".format(EPSG)) as shp:
                for i in range(len(contour_lines)):
                    shp.write({
                        'geometry': mapping(contour_lines[i]),
                        'properties': {'level': contour_levels[i]}
                    })
            
            shp.close()
            
    for sp in sps:
        # Remove head file
        os.remove(os.path.join(piezo_dir, 'HEADS_{}.dat'.format(sp)))