# -*- coding: utf-8 -*-
# make plots from csv data
import pandas as pd
import os, cv2
import numpy as np
import matplotlib.pyplot as plt
from glob import glob
from tqdm import tqdm
import itertools
import seaborn as sns
from matplotlib.patches import Patch
from matplotlib.lines import Line2D

# %% 
def scatter_plot(dataset, method, gan_name='', preprocess='', mode='b2a', dark=True):
    if dark == True:
        bg_color = '#181717'
        plt.style.use(['ggplot','dark_background'])
        plt.rcParams['axes.facecolor'] = '#212020'
        plt.rcParams['figure.facecolor'] = bg_color
        plt.rcParams['grid.color'] = bg_color
        plt.rcParams['axes.edgecolor'] = bg_color
        label_color = 'white'
    else:
        plt.style.use('ggplot')
        label_color = 'black'
    markers = itertools.cycle(('p', '*', 'P', 'X', '+', '.', 'x', 'h', 'H', '1')) 

    # dataset-specific variables
    assert dataset in ['Eliceiri', 'Balvan', 'Zurich'], "supervision must be in ['Eliceiri', 'Balvan', 'Zurich']"
    if dataset == 'Eliceiri':
        target_root = './Datasets/Eliceiri_patches'
        w = 834
    elif dataset == 'Balvan':
        target_root = './Datasets/Balvan_patches/fold1'
        w = 300
    elif dataset == 'Zurich':
        target_root = './Datasets/Zurich_patches/fold1'
        w = 300
    
    # read results
    dfs = [pd.read_csv(csv_path) for csv_path 
           in glob(f'{target_root}/patch_tlevel*/results/{method+gan_name}_{mode}_{preprocess}.csv')]
    whole_df = pd.concat(dfs)
    #whole_df.loc[:, ['Displacement', 'Error']]

    # make scatter plot
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 7), sharex='col', sharey='row')
    # set colour
    color_cycler = plt.style.library['tableau-colorblind10']['axes.prop_cycle']
    colors = color_cycler.by_key()['color']
    ax.set_prop_cycle(color_cycler)
    # plot
    ax.scatter(whole_df['Displacement'], whole_df['Error'], alpha=0.6)
    ax.set_yscale('log')
    if dataset == 'Eliceiri':
        ax.set_xlim(left=0, right=225)
    ax.set_ylim(bottom=1e-2, top=2000)
        
    # plot identity line
    x = np.linspace(ax.get_xlim()[0], ax.get_xlim()[1], 10000)
    y = x
    ab, = ax.plot(x, y, linestyle='dotted', color='grey', scalex=False, scaley=False, label='$\epsilon = d$')
    
    # plot threshold
    ac = ax.axhline(y=w*0.02, linestyle="--", color="#52854C", label='success threshold $\delta_0$')
    ax.legend(handles=[ac, ab], fontsize='large', framealpha=0.4, loc='lower right')
    
    ax.set_xlabel('Initial displacement $d$ [px]', fontsize=15, color =label_color)
    ax.set_ylabel('Absolute registration error $\epsilon$ [px]', fontsize=15, color =label_color)
    ax.tick_params(labelsize='large')
    
    # Secondary Axis
    def forward(x):
        return x / w
    def inverse(x):
        return x * w
    secaxy = ax.secondary_yaxis('right', functions=(forward, inverse))
    secaxy.set_ylabel('Relative registration error $\delta$', fontsize=15, color=label_color)
    secaxy.tick_params(labelsize='large')
    secaxx = ax.secondary_xaxis('top', functions=(forward, inverse))
    secaxx.set_xlabel('Relative initial displacement to image width', fontsize=15, color=label_color)
    secaxx.tick_params(labelsize='large')
    if dataset in ['Balvan', 'Zurich']:
        secaxx.set_xlim(left=0, right=0.27)
    
#    plt.show()
    save_dir = f'{target_root}/result_imgs/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if dark == True:
        plt.savefig(save_dir + f'dark_scatter_{method+gan_name}_{mode}_{preprocess}.png', 
                    format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
        plt.savefig(save_dir + f'dark_scatter_{method+gan_name}_{mode}_{preprocess}.svg', 
                    format='svg', bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    else:
        plt.savefig(save_dir + f'scatter_{method+gan_name}_{mode}_{preprocess}.png', 
                    format='png', dpi=300, bbox_inches='tight')
        plt.savefig(save_dir + f'scatter_{method+gan_name}_{mode}_{preprocess}.pdf', 
                    format='pdf', bbox_inches='tight')
    
    return

# %% for local testing 
scatter_plot(
        dataset='Zurich', 
#        dataset='Balvan', 
#        dataset='Eliceiri', 
        method='MI', 
        gan_name='', 
        preprocess='nopre', 
        mode='b2a',
        dark=True)

# %%
DARK=True

for gan in tqdm(['p2p_A', 'p2p_B', 'cyc_A', 'cyc_B', 'drit_A', 'drit_B']):
    for pre in ['nopre', 'hiseq']:
        for method in ['SIFT', 'aAMD']:
            scatter_plot(
                    target_root='./Datasets/Eliceiri_patches', 
                    method=method, 
                    gan_name=gan, 
                    preprocess=pre, 
                    mode='b2a',
                    dark=DARK)

for mode in tqdm(['a2a', 'b2a', 'b2b']):
    for pre in ['nopre', 'hiseq']:
        scatter_plot(
                target_root='./Datasets/Eliceiri_patches', 
                method='aAMD', 
                gan_name='', 
                preprocess=pre, 
                mode=mode,
                dark=DARK)
    scatter_plot(
            target_root='./Datasets/Eliceiri_patches', 
            method='SIFT', 
            gan_name='', 
            preprocess='nopre', 
            mode=mode,
            dark=DARK)
        
for method in ['MI', 'CA']:
    scatter_plot(
            target_root='./Datasets/Eliceiri_patches', 
            method=method, 
            gan_name='', 
            preprocess='nopre', 
            mode='b2a',
            dark=DARK)

for pre in ['su', 'us']:
    scatter_plot(
            target_root='./Datasets/Eliceiri_patches', 
            method='VXM', 
            gan_name='', 
            preprocess=pre, 
            mode='b2a',
            dark=DARK)


# %% Success rate 
def plot_success_rate(dataset, plot_method, pre='nopre', fold=1, dark=True):
    if dark == True:
        bg_color = '#181717'
        plt.style.use(['ggplot','dark_background'])
        plt.rcParams['axes.facecolor'] = '#212020'
        plt.rcParams['figure.facecolor'] = bg_color
        plt.rcParams['grid.color'] = bg_color
        plt.rcParams['axes.edgecolor'] = bg_color
        label_color = 'white'
    else:
        plt.style.use('ggplot')
        label_color = 'black'    
    markers = itertools.cycle(('p', '*', 'P', 'X', '+', '.', 'x', 'h', 'H', '1')) 

    assert pre in ['', 'nopre', 'PCA', 'hiseq'], "pre must be in ['', 'nopre', 'PCA', 'hiseq']"
    
    # dataset-specific variables
    assert dataset in ['Eliceiri', 'Balvan', 'Zurich'], "dataset must be in ['Eliceiri', 'Balvan', 'Zurich']"
    if dataset == 'Eliceiri':
        root_dir = './Datasets/Eliceiri_patches'
        w = 834
        fold = 1
    elif dataset == 'Balvan':
        root_dir = f'./Datasets/Balvan_patches/fold{fold}'
        w = 300
    elif dataset == 'Zurich':
        root_dir = f'./Datasets/Zurich_patches/fold{fold}'
        w = 300
    if fold == 'all':
        root_dir = f'./Datasets/{dataset}_patches'
        
    
    def plot_single_curve(method, mode='b2a', preprocess='nopre'):
        # read results
        if fold == 'all':
            dfs = [pd.read_csv(csv_path) for csv_path 
                   in glob(f'{root_dir}/fold*/patch_tlevel*/results/{method}_{mode}_{preprocess}.csv')]
        else:
            dfs = [pd.read_csv(csv_path) for csv_path 
                   in glob(f'{root_dir}/patch_tlevel*/results/{method}_{mode}_{preprocess}.csv')]
        
        whole_df = pd.concat(dfs)
        
        # success rate
        whole_df['binning'], bin_edges = pd.qcut(whole_df['Displacement'], q=10, retbins=True)
        n_success = whole_df[whole_df['Error'] < w*0.02].groupby('binning').count()['Error']
        success_rates = n_success / whole_df['binning'].value_counts(sort=False)
        bin_centres = [0.5 * (bin_edges[i] + bin_edges[i+1]) for i in range(len(bin_edges) - 1)]
        
        z = None    # zorder
        m = None    # marker
        if method in ['MI', 'CA'] or 'MI' in method:
            linestyle = '--'
            z=4
        elif method != 'VXM' and '_' not in method and 'comir' not in method:
            linestyle = '-.'
            z=4.1
        else:
            linestyle = '-'
            m = next(markers)
            
        if method == 'VXM':
            ax.plot(bin_centres, success_rates, linestyle=linestyle, marker=m, label=f'{method}_{mode}_{preprocess}')
        else:
            ax.plot(bin_centres, success_rates, linestyle=linestyle, marker=m, zorder=z, label=f'{method}_{mode}')
    
        return bin_edges
        
    # %
    
#    plt.style.use('ggplot')
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 7), sharex='col', sharey='row')
    # set colour
    color_cycler = plt.style.library['tableau-colorblind10']['axes.prop_cycle']
    colors = color_cycler.by_key()['color']
    ax.set_prop_cycle(color_cycler)
    
    # read results
    if fold == 'all':
        results = [os.path.basename(res_path) for res_path in glob(f'{root_dir}/fold1/patch_tlevel2/results/*_*_*.csv')]
    else:
        results = [os.path.basename(res_path) for res_path in glob(f'{root_dir}/patch_tlevel2/results/*_*_*.csv')]
    
    # baselines
    bin_edges = plot_single_curve(method='MI', mode='b2a', preprocess='nopre')
#    bin_edges = plot_single_curve(method='MI3', mode='b2a', preprocess='nopre')
#    bin_edges = plot_single_curve(method='MI5', mode='b2a', preprocess='nopre')
    
    # other lines
    for result in results:
        parts = result.split('_')
        preprocess = parts[-1].split('.')[0]
        mode = parts[-2]
        i_ = [i for i, ltr in enumerate(result) if ltr == '_']
        method = result[:i_[-2]].replace('results_','')
        if plot_method == 'SIFT':
    #        if 'aAMD' not in method and preprocess=='nopre':
            if plot_method in method and preprocess==pre:
                bin_edges = plot_single_curve(method=method, mode=mode, preprocess=preprocess)
        elif plot_method == 'aAMD':
    #        if 'SIFT' not in method and preprocess=='nopre':
            if plot_method in method and preprocess==pre:
                bin_edges = plot_single_curve(method=method, mode=mode, preprocess=preprocess)
        elif plot_method == 'VXM':
    #        if 'SIFT' not in method and 'aAMD' not in method:
            if plot_method in method:
                bin_edges = plot_single_curve(method=method, mode=mode, preprocess=preprocess)
    if dataset == 'Eliceiri':
        bin_edges = plot_single_curve(method='CA', mode='b2a', preprocess='nopre')
    
    ax.legend(fontsize='large', loc='center left', bbox_to_anchor=(1, 0.5), framealpha=0.0)
    # bin edges
    for edge in bin_edges:
        ax.axvline(x=edge, linestyle='dotted', color='grey', zorder=1.5)
    if dataset == 'Eliceiri':
        ax.set_xlim(left=0, right=225)
    ax.set_ylim(bottom=-0.05, top=1.05)
    
    ax.set_xlabel('Initial displacement $d$ [px]', fontsize=15, color=label_color)
    ax.set_ylabel('Success rate $\lambda$', fontsize=15, color=label_color)
    ax.tick_params(labelsize='large')

    # Secondary Axis
    def forward(x):
        return x / w
    def inverse(x):
        return x * w
    secaxx = ax.secondary_xaxis('top', functions=(forward, inverse))
    secaxx.set_xlabel('Relative initial displacement to image width', fontsize=15, color=label_color)
    secaxx.tick_params(labelsize='large')
    if dataset in ['Balvan', 'Zurich']:
        ax.set_xlim(left=-1, right=81)
        secaxx.set_xlim(left=0, right=0.27)

    #plt.show()
    save_dir = f'{root_dir}/result_imgs/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if dark == True:
        plt.savefig(save_dir + f'dark_{dataset}_success_{plot_method}_{pre}.png', 
                    format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
        plt.savefig(save_dir + f'dark_{dataset}_success_{plot_method}_{pre}.svg', 
                    format='svg', bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    else:
        plt.savefig(save_dir + f'{dataset}_success_{plot_method}_{pre}.png', format='png', dpi=300, bbox_inches='tight')
        plt.savefig(save_dir + f'{dataset}_success_{plot_method}_{pre}.pdf', format='pdf', bbox_inches='tight')

    return

# %%
DARK=True
for method in ['SIFT', 'aAMD']:
    for dataset in ['Balvan', 'Zurich', 'Eliceiri']:
        plot_success_rate(dataset=dataset, plot_method=method, pre='nopre', fold=1, dark=DARK)

# %%
def adjust_lightness(color, amount=0.5):
    import matplotlib.colors as mc
    import colorsys
    try:
        c = mc.cnames[color]
    except:
        c = color
    c = colorsys.rgb_to_hls(*mc.to_rgb(c))
    c_out = colorsys.hls_to_rgb(c[0], max(0, min(1, amount * c[1])), c[2])
    if type(color) is str:
        c_out = mc.to_hex(c_out)
    return c_out

def fid_scatter(dataset, preprocess='nopre', dark=True):
#    dataset='Zurich'
#    preprocess='nopre'
#    dark=True
    if dark == True:
        bg_color = '#181717'
        plt.style.use(['ggplot','dark_background'])
        plt.rcParams['axes.facecolor'] = '#212020'
        plt.rcParams['figure.facecolor'] = bg_color
        plt.rcParams['grid.color'] = bg_color
        plt.rcParams['axes.edgecolor'] = bg_color
        label_color = 'white'
    else:
        plt.style.use('ggplot')
        label_color = 'black'    

    assert preprocess in ['', 'nopre', 'PCA', 'hiseq'], "preprocess must be in ['', 'nopre', 'PCA', 'hiseq']"
    
    # dataset-specific variables
    assert dataset in ['Eliceiri', 'Balvan', 'Zurich'], "dataset must be in ['Eliceiri', 'Balvan', 'Zurich']"

    root_dir = f'./Datasets/{dataset}_patches'
    result_dir = f'./Datasets/{dataset}_patches_fake'

    gan_names = ['A2A', 'B2B', 
                 'cyc_A', 'cyc_B', 'drit_A', 'drit_B', 'p2p_A', 'p2p_B', 'star_A', 'star_B', 'comir']


    # read results
    df = pd.read_csv(f'{result_dir}/FID_success_{preprocess}.csv', index_col='Method')


    # make scatter plot
    fig, ax = plt.subplots(nrows=1, ncols=1, figsize=(10, 7), sharex='col', sharey='row')
    # set colour
#    color_cycler = plt.style.library['tableau-colorblind10']['axes.prop_cycle']
#    ax.set_prop_cycle(color_cycler)
    colors = sns.color_palette("Paired").as_hex()
    colors = itertools.cycle(colors)
    
    # plot
    i_row = 0
    legend1_elements = []
    for method_row in df.itertuples():
        if method_row.Index in gan_names:
            c = next(colors)
            if dark != True:      # darken bright colors for bright mode
                c = adjust_lightness(c, amount=0.4) if i_row % 2 == 0 else adjust_lightness(c, amount=1.2)
            ax.scatter(method_row.FID_mean, method_row.Success_aAMD_mean, 
#                       label=method_row.Index, 
                       c=c, s=10**2, marker='o', alpha=0.6, zorder=2.5)
            ax.scatter(method_row.FID_mean, method_row.Success_SIFT_mean, 
#                       label=method_row.Index, 
                       c=c, s=10**2, marker='X', alpha=0.6, zorder=2.5)
            if dataset != 'Eliceiri':
                # Error bars
                ax.errorbar(method_row.FID_mean, method_row.Success_aAMD_mean, 
                            xerr=method_row.FID_STD, yerr=method_row.Success_aAMD_STD, 
                            c=c, capsize=2, alpha=0.3)
                ax.errorbar(method_row.FID_mean, method_row.Success_SIFT_mean, 
                            xerr=method_row.FID_STD, yerr=method_row.Success_SIFT_STD, 
                            c=c, capsize=2, alpha=0.3)
            legend1_elements.append(Patch(color=c, label=method_row.Index, alpha=0.6))
            i_row += 1
#    ax.scatter(df['FID_mean'], df['Success_aAMD_mean'], alpha=0.6)
#    ax.scatter(df['FID_mean'], df['Success_SIFT_mean'], alpha=0.6)
        
#    ax.legend(fontsize='large', framealpha=0.4, loc='lower right')
    legend1 = ax.legend(handles=legend1_elements, 
                        fontsize='large', loc='center left', bbox_to_anchor=(1, 0.5), framealpha=0.0)
    ax.add_artist(legend1)
    
    # FID baselines
    baselineA = ax.axvline(x=df.loc['train2testA', 'FID_mean'], 
                           linestyle="--", color=next(colors), alpha=0.5, label='train2test_A')
    baselineB = ax.axvline(x=df.loc['train2testB', 'FID_mean'], 
                           linestyle="--", color=next(colors), alpha=0.5, label='train2test_B')
    
    # 2nd legend
    legend2_elements = [Line2D([],[], linewidth=0, marker='o', markersize=10, c='grey', label='aAMD'),
                        Line2D([],[], linewidth=0, marker='X', markersize=10, c='grey', label='SIFT'),
                        baselineA, 
                        baselineB]
    ax.legend(handles=legend2_elements, fontsize='large', loc='center left', bbox_to_anchor=(1, 0.1), framealpha=0.0)
    
    ax.set_ylim(bottom=-0.05, top=1.05)
    ax.set_xlabel('Fréchet Inception Distance ($FID$)', fontsize=15, color=label_color)
    ax.set_ylabel('Registration success rate $\lambda$', fontsize=15, color=label_color)
    ax.tick_params(labelsize='large')
    
    #plt.show()
    save_dir = f'{root_dir}/result_imgs/'
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
    if dark == True:
        plt.savefig(save_dir + f'dark_{dataset}_fid_{preprocess}.png', 
                    format='png', dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
        plt.savefig(save_dir + f'dark_{dataset}_fid_{preprocess}.svg', 
                    format='svg', bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    else:
        plt.savefig(save_dir + f'{dataset}_fid_{preprocess}.png', format='png', dpi=300, bbox_inches='tight')
        plt.savefig(save_dir + f'{dataset}_fid_{preprocess}.pdf', format='pdf', bbox_inches='tight')

    return

# %%
DARK=True
for pre in ['nopre', 'hiseq']:
    for dataset in ['Balvan', 'Eliceiri', 'Zurich']:
        fid_scatter(dataset=dataset, preprocess=pre, dark=DARK)

