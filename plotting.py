import glob
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os.path
import re
from pathlib import Path

import matplotlib.ticker as tkr

plots_dir = "plots/"
size_val=20
marker_size=8

def numfmt(x, pos):
    return int(x / 1000.0)

def plot_states(csv_file_path,heur_iter_vals,xmode=None,ymode=None,lower=False,prmin=True,prmax=True,to_pdf=False,plot_exact=True):
    data = pd.read_csv(csv_file_path,delimiter=",")
    #data = data[data['timeout'].astype(str) != "True"]
    data = data[data['states'].astype(str) != "-"]
    data = data[data[data.columns[13]].astype(str) != "error"]
    data = data[data[data.columns[13]].astype(str) != "parse error"]
    #data = data[((data['heur_iter'].astype(str) == '-') | (data['heur_iter'].astype(str) in [str(x) for x in heur_iter_vals]))]
    data['states'] = pd.to_numeric(data['states'])


    all_modes=data['mode'].unique().tolist()

    fig = plt.figure(figsize=(7,6))
    ax1 = fig.add_subplot(111)
    if ymode == "x1000":
        ax1.set_ylabel("states (x 1000)",size=size_val)
    else:
        ax1.set_ylabel("states",size=size_val)
    ax1.set_xlabel("threshold λ",size=size_val)
    plt.xticks(size = size_val)
    plt.yticks(size = size_val)
    plt.grid(True)

    colors = dict([("y exact","green"),("z exact","purple"),("y form","orange"),("z form","blue"),("local","brown"),("global","black"),("prmax","orange"),("prmax exact", "green"),("prmin","blue"),("prmin exact","green"),("prmax minimal","purple")])
    markers = dict([("y exact","x"),("z exact","."),("y form","x"),("z form","."),("local","d"),("global","s"),("prmax","x"),("prmax exact", "+"),("prmin","v"),("prmin exact","x"),("prmax minimal","v")])
    legend_names = dict([("y form",r'$P^{max}$ QS'),("z form",r'$P^{min}$ QS'),("prmax", r'$P^{max}$ QS'),("prmin", r'$P^{min}$ QS'), ("prmax exact", "$P^{max}$ exact"), ("prmax minimal", "ltlsubsys exact"),("prmin exact","$P^{min}$ exact")])
    exact_modes = ["y exact", "z exact", "prmax exact", "prmin exact", "prmax minimal"]
    prmin_modes = ["z exact", "z form", "prmin", "prmin exact"]
    prmax_modes = ["y form", "y exact", "prmax exact", "prmax", "prmax minimal"]
    comics_modes = ["local","global"]

    modes = all_modes
    if not prmin:
        modes = [mode for mode in modes if (mode not in prmin_modes)]
    if not prmax:
        modes = [mode for mode in modes if (mode not in prmax_modes)]

    tables=[data[data['mode'] == mode] for mode in modes]

    for table in tables:
        mode = table['mode'].unique().tolist()[0]
        if not plot_exact and (mode == "y exact" or mode == "z exact"):
            continue
        if mode in legend_names:
            name = legend_names[mode]
        else:
            name = mode
        if lower and (mode in exact_modes):
            table = table.sort_values(by=['threshold'])
            lower_table = pd.to_numeric(table['lower_bound'])
            ax1.plot(table['threshold'],table['states'],marker=markers[mode],ms=marker_size,linestyle="dashed",linewidth=1.2,color=colors[mode],label=name)
            ax1.plot(table['threshold'],lower_table,marker=markers[mode],ms=marker_size,linestyle="dashed",linewidth=1.2,color=colors[mode],label='_nolegend_')
            ax1.fill_between(table['threshold'], table['states'], lower_table,color=colors[mode], alpha=0.1)
        elif mode in comics_modes:
            table = table.sort_values(by=['threshold'])
            ax1.plot(table['threshold'],table['states'],marker=markers[mode],ms=marker_size,linestyle="dashed",linewidth=1.2,color=colors[mode],label=name)
        else:
            colors_iter = ['orange','red','brown','blue','teal','black']
            index = 0
            for heur_val in heur_iter_vals:
                if index == 0:
                    color = colors[mode]
                else:
                    color = colors_iter[index]
                sub_tab = table[table['heur_iter'].astype(str) == str(heur_val)].sort_values(by=['threshold'])
                ax1.plot(sub_tab['threshold'],sub_tab['states'],marker=markers[mode],ms=marker_size,linestyle="dashed",linewidth=1.2,color=color,label=name+r'$_' + str(heur_val) + '$')
                index += 1

    plt.legend(prop={'size':size_val-5})
    ##fig.legend(loc='upper left', bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)

    if ymode == "x1000":
        yfmt = tkr.FuncFormatter(numfmt)
        plt.gca().yaxis.set_major_formatter(yfmt)

    if xmode == "e":
        xfmt = tkr.FormatStrFormatter('%1.1e')
        plt.gca().xaxis.set_major_formatter(xfmt)

    plt.tight_layout()
    if to_pdf:
        info_str = ""
        if (not prmax) and prmin:
            info_str = "_prmin"
        if prmax and (not prmin):
            info_str = "_prmax"
        plt.savefig(plots_dir + Path(csv_file_path).stem + info_str + '_states.pdf')

def plot_times(csv_file_path,heur_iter_vals,to_pdf=False,prmin=True,prmax=True,plot_exact=True,xmode=None):
    data = pd.read_csv(csv_file_path,delimiter=",")
    data = data[data['timeout'].astype(str) != "True"]
    data = data[data['states'].astype(str) != "-"]
    data = data[data[data.columns[13]].astype(str) != "error"]
    data = data[data[data.columns[13]].astype(str) != "parse error"]
    #data = data[((data['heur_iter'].astype(str) == str(heur_iter_val)) | (data['heur_iter'].astype(str) == '-'))]
    data['t_wall'] = pd.to_numeric(data['t_wall'])
    #data = data.sort_values(by=['threshold'])


    all_modes=data['mode'].unique().tolist()

    fig = plt.figure(figsize=(7,6))
    ax1 = fig.add_subplot(111)
    ax1.set_ylabel("time in seconds",size=size_val)
    ax1.set_yscale('log')
    ax1.set_xlabel("threshold λ",size=size_val)
    plt.xticks(size = size_val)
    plt.yticks(size = size_val)
    plt.grid(True)

    colors = dict([("y exact","purple"),("z exact","green"),("y form","orange"),("z form","blue"),("local","brown"),("global","black"),("prmax","orange"),("prmax exact", "purple"),("prmin","blue"),("prmin exact","green"),("prmax minimal","brown")])
    legend_names = dict([("y form",r'$P^{max}$ QS'),("z form",r'$P^{min}$ QS'),("prmax", r'$P^{max}$ QS'),("prmin", r'$P^{min}$ QS'), ("prmax exact", "$P^{max}$ exact"), ("prmax minimal", "ltlsubsys exact"),("prmin exact","$P^{min}$ exact")])
    markers = dict([("y exact","x"),("z exact","."),("y form","x"),("z form","."),("local","d"),("global","s"),("prmax","x"),("prmax exact", "+"),("prmin","v"),("prmin exact","x"),("prmax minimal","v")])
    exact_modes = ["y exact", "z exact", "prmax exact", "prmin exact", "prmax minimal"]
    prmin_modes = ["z exact", "z form", "prmin", "prmin exact"]
    prmax_modes = ["y form", "y exact", "prmax exact", "prmax", "prmax minimal"]
    comics_modes = ["local","global"]

    modes = all_modes
    if not prmin:
        modes = [mode for mode in modes if (mode not in prmin_modes)]
    if not prmax:
        modes = [mode for mode in modes if (mode not in prmax_modes)]

    tables=[data[data['mode'] == mode] for mode in modes]

    for table in tables:
        mode = table['mode'].unique().tolist()[0]
        if not plot_exact and (mode in exact_modes):
            continue
        if mode in legend_names:
            name = legend_names[mode]
        else:
            name = mode
        if mode in exact_modes:
            table = table.sort_values(by=['threshold'])
            ax1.plot(table['threshold'],table['t_wall'],marker=markers[mode],ms=marker_size,linestyle="dashed",linewidth=1.2,color=colors[mode],label=name)
        elif mode in comics_modes:
            table = table.sort_values(by=['threshold'])
            ax1.plot(table['threshold'],table['t_wall'],marker=markers[mode],ms=marker_size,linestyle="dashed",linewidth=1.2,color=colors[mode],label=name)
        else:
            for heur_val in heur_iter_vals:
                sub_tab = table[table['heur_iter'].astype(str) == str(heur_val)].sort_values(by=['threshold'])
                ax1.plot(sub_tab['threshold'],sub_tab['t_wall'],marker=markers[mode],ms=marker_size,linestyle="dashed",linewidth=1.2,color=colors[mode],label=name+r'$_' + str(heur_val) + '$')
    ##fig.legend(loc='upper left', bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)
    plt.legend(prop={'size':size_val-5})

    if xmode == "e":
        xfmt = tkr.FormatStrFormatter('%1.1e')
        plt.gca().xaxis.set_major_formatter(xfmt)

    plt.tight_layout()
    if to_pdf:
        info_str = ""
        if (not prmax) and prmin:
            info_str = "_prmin"
        if prmax and (not prmin):
            info_str = "_prmax"
        plt.savefig(plots_dir + Path(csv_file_path).stem + info_str + '_times.pdf')


def plot_heur_val_comp(csv_file_path,xmode=None,to_pdf=False):
    data = pd.read_csv(csv_file_path,delimiter=",")
    data = data[data['timeout'].astype(str) != "True"]
    #data = data[data['info'].astype(str) != "error"]
    data = data[(data['heur_iter'].astype(str) != '-')]
    data['t_wall'] = pd.to_numeric(data['t_wall'])
    data['states'] = pd.to_numeric(data['states'])

    modes=data['mode'].unique().tolist()
    tables=[data[data['mode'] == mode] for mode in modes]
    heur_iter_vals = data['heur_iter'].unique().tolist()

    for table in tables:
        mode = table['mode'].unique().tolist()[0]
        print(str(mode) + ":")
        fig = plt.figure(figsize=(7,6))
        ax1 = fig.add_subplot(111)
        plt.xticks(size = size_val)
        plt.yticks(size = size_val)
        plt.grid(True)
        ax1.set_ylabel("states",size=size_val)
        ax1.set_xlabel("threshold λ",size=size_val)
        colors = ["blue","green","orange","pink","brown","grey","purple"]
        markers = ["+","s","v","d","x"]
        index = 0
        for heur_val in heur_iter_vals:
            sub_tab = table[table['heur_iter'].astype(str) == str(heur_val)]
            ax1.plot(sub_tab['threshold'],sub_tab['states'],marker=markers[index],ms=marker_size,linestyle="dashed",linewidth=1.2,color=colors[index],label=r'QS$_' + str(heur_val) + "$")
            index +=1
        #fig.legend(loc='upper left', bbox_to_anchor=(0,1), bbox_transform=ax1.transAxes)

        if xmode == "e":
            xfmt = tkr.FormatStrFormatter('%1.1e')
            plt.gca().xaxis.set_major_formatter(xfmt)

        plt.legend(prop={'size':size_val-5})
        plt.tight_layout()
        if to_pdf:
            plt.savefig(plots_dir + Path(csv_file_path).stem + '_heur_iter_' + mode.replace(" ","") + '.pdf')

def read_state_number(csv_file_path):
    state_num_regex = re.compile("total states:([0-9]+)")
    with open(csv_file_path) as csv_file:
        first_line = csv_file.readline()
        regex_res = state_num_regex.search(first_line)
        state_num = int(regex_res.group(1))
        return state_num

def eval_rounding_err_in_file(csv_file_path):
    i=0
    data = pd.read_csv(csv_file_path,delimiter=",")
    row_count = len(data.index)
    data = data[(data['t_wall'].astype(str) != "-")]
    data = data[(data['prob'].astype(str) != "-")]

    data['prob'] = pd.to_numeric(data['prob'])
    data['threshold'] = pd.to_numeric(data['threshold'])
    data = data[(data['prob'] < data['threshold'])]
    if not data.empty:
        print(csv_file_path)
        for index,row in data.iterrows():
            print(row['mode'], row['threshold'], row['prob'])
            i += 1
    print("violation percentage: " + str(i/row_count))

def eval_rounding_err(csv_dir_path):
    for csv_file_path in glob.glob(csv_dir_path + "*/*.csv"):
        eval_rounding_err_in_file(csv_file_path)

def run(csv_file_path,heur_val,prmin=True,prmax=True,to_pdf=False,xmode=None,ymode=None,plot_exact=True):
    lower = plot_exact
    print(csv_file_path)
    print("states:" + str(read_state_number(csv_file_path)))
    plot_states(csv_file_path,heur_val,lower=lower,prmin=prmin,prmax=prmax,to_pdf=to_pdf,xmode=xmode,ymode=ymode,plot_exact=plot_exact)
    plot_times(csv_file_path,heur_val,to_pdf=to_pdf,plot_exact=plot_exact,prmin=prmin,prmax=prmax,xmode=xmode)
    eval_rounding_err_in_file(csv_file_path)
