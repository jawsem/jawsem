#!/usr/bin/env python3

from flask import Flask
from flask import render_template, redirect,url_for
import os
import datetime
from db_utils import get_connection, get_size
import pandas as pd
from app_configs import FTP_MOUNT, PLEX_MOUNT,logging
from cron_scripts import download_files, update_available_dls

app = Flask(__name__)
pd.set_option('display.max_colwidth', -1)
@app.route('/')
def base_app():
    conn = get_connection()
    df = pd.read_sql("select * from available_dls where hidden = 0",conn)
    df['download_file'] = df.apply(lambda x: """<a href="{}/{}">DOWNLOAD FILE</a>""".format(x['seedbox_name'],x['is_file']),axis=1)
    df['hide_file'] = df['seedbox_name'].apply(lambda x: """<a href="{}/hide">HIDE FILE</a>""".format(x))
    raw_html = df[['last_update_date','seedbox_name','download_file','hide_file']].sort_values(by='last_update_date',ascending=False).to_html(escape=False)
    return render_template('base.html',title = "AVAILABLE TO DOWNLOAD LIST",rawhtml=raw_html)
@app.route('/download')
def download():
    download_files()
    return redirect('/')
@app.route('/update')
def update():
    update_available_dls()
    return redirect('/')
@app.route('/hiddenfiles')
def hidden_files():
    conn = get_connection()
    df = pd.read_sql("select * from available_dls where hidden =1",conn)
    df['unhide_file'] = df['seedbox_name'].apply(lambda x: """<a href="{}/unhide">UNHIDE FILE</a>""".format(x))
    raw_html = df[['last_update_date','seedbox_name','unhide_file']].sort_values(by='last_update_date',ascending=False).to_html(escape=False)
    return render_template('base.html',title = "HIDDEN FILE LIST",rawhtml=raw_html)

@app.route("/<file>/<action>")
def hide_file(file,action):
    conn = get_connection()
    curs = conn.cursor()
    if action == 'hide':
        curs.execute("update available_dls set hidden=1 where seedbox_name = '{}'".format(file))
        conn.commit()
        return redirect('/')
    if action == 'unhide':
        curs.execute("update available_dls set hidden=0 where seedbox_name = '{}'".format(file))
        conn.commit()
        return redirect('/hiddenfiles')
@app.route("/<file>/<int:is_file>")
def show_dl(file,is_file):
    conn = get_connection()
    df = pd.read_sql("select * from downloads where seedbox_name='{}'".format(file),conn)
    if df.shape[0]>0:
        queued = df['download_state'].values[0]
    else:
        queued = "Never Downloaded"
    raw_html = """<table border="1" class="dataframe"><tr><td>DOWNLOAD_STATE={}</td></tr><tr><td><a href="movies/{}">DOWNLOAD FILE AS MOVIE</a></td></tr><tr><td><a href="tvshows/{}">DOWNLOAD FILE AS TVSHOW</a></td></tr></table>""".format(queued,is_file,is_file)
    return render_template('base.html',title = "INFO: {}".format(file),rawhtml=raw_html)

@app.route("/<file>/<filetype>/<int:is_file>")
def queue_for_dl(file,filetype,is_file):
    conn = get_connection()
    if filetype=='check_status':
        df = pd.read_sql("select * from downloads where seedbox_name='{}'".format(file),conn)
        size = df['size']
        if is_file==1:
            cur_size = os.path.getsize(os.path.join(PLEX_MOUNT,file))
        else:
            cur_size = get_size(os.path.join(PLEX_MOUNT,file))
        perc_done = cur_size/size
        return render_template('base.html',title = "CURRENT_STATUS FOR FILE: {}".format(file),raw_html="Percent Done: {0:.2%}".format(perc_done))
    else:

        c = conn.cursor()
        if filetype=='movies':
            is_movie=1
        else:
            is_movie=0
        logging.debug("Getting File Size")
        if is_file==1:
            size = os.path.getsize(os.path.join(FTP_MOUNT,file))
        else:
            size = get_size(os.path.join(FTP_MOUNT,file))

        c.execute("""insert into downloads (seedbox_name,size,is_file,is_movie) values ('{}',{},{},{})""".format(file,size,is_file,is_movie))
        conn.commit()
        df = pd.read_sql("select * from downloads where seedbox_name='{}'".format(file),conn)
        conn.close()
        return render_template('base.html',title = "FILE: {} QUEUED for download".format(file),raw_html=df.to_html())

if __name__ == '__main__':
    app.run(debug=True,host= '0.0.0.0')
