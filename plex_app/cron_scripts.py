from db_utils import get_connection
from app_configs import FTP_MOUNT, PLEX_MOUNT
import os
import pandas as pd
import datetime
import shutil
import sys

def update_available_dls():
    try:
        file_list = [(item, os.path.isfile(os.path.join(FTP_MOUNT,item))) for item in os.listdir(FTP_MOUNT)]
        df = pd.DataFrame(file_list,columns=['seedbox_name','is_file'])
        df['is_file'] = df['is_file'].astype(int)
        df['last_update_time'] = datetime.datetime.now()
        df['downloaded'] = 0
        conn = get_connection()
        df.to_sql('available_dls',conn,if_exists='replace',index=False)
        print("Data Saved: {}".format(df.shape[0]))
    except Exception as e:
        print("Error saving data: {}".format(e))

def download_files():
    conn = get_connection()
    files_df = pd.read_sql("select * from downloads where download_state = 'QUEUED'",conn)
    if files_df.shape[0]==0:
        print("No Files to download")
        return
    def dl_func(row,curs):
        curs.execute("UPDATE downloads set download_start = (datetime('now','localtime')) where seedbox_name = '{}'".format(row['seedbox_name']))
        conn.commit()
        movie = row['is_movie']
        is_file = row['is_file']
        if movie==1:
            dl_path1 = PLEX_MOUNT+'/movies'
        else:
            dl_path1 = PLEX_MOUNT+'/tvshows'

        if is_file==0:
            dl_path1 += row['seedbox_name']

        if is_file==1:
            shutil.copy2(os.path.join(FTP_MOUNT,row['seedbox_name']),dl_path1)
        else:
            os.chdir(FTP_MOUNT)
            shutil.copytree(row['seedbox_name'],dl_path1)

        curs.execute("UPDATE downloads set download_state='DONE', download_date=(datetime('now','localtime')), downloaded=1, download_path = '{}' where seedbox_name = '{}'".format(dl_path1,row['seedbox_name']))
        curs.execute("UPDATE available_dls set downloaded =1, last_update_date = (datetime('now','localtime')) where seebox_name = '{}'".format(row['seedbox_name']))
        conn.commit()
        print("File: {} has finished downloading to path: {}".format(row['seedbox_name'],row['download_path']))
    c = conn.cursor()
    files_df.apply(dl_func,curs=c,axis=1)

if __name__ == '__main__':
    script = 'update'
    if len(sys.argv)>1:
        script = sys.argv[1]
    if script == 'update':
        update_available_dls()
    elif script == 'download':
        download_files()
    else:
        sys.exit("Need to call download or update in order to run cron_scripts.")
