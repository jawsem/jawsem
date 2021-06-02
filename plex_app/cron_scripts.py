from db_utils import get_connection
from app_configs import FTP_MOUNT, PLEX_MOUNT,TRANS_MOUNT,TRANSFER_FILE,logging
import os
import pandas as pd
import datetime
import shutil
import sys
import subprocess

def update_available_dls():
    logging.info("CRON_JOB: Updating available DLs")
    try:
        file_list = [(item, os.path.isfile(os.path.join(FTP_MOUNT,item))) for item in os.listdir(FTP_MOUNT)]
        df = pd.DataFrame(file_list,columns=['seedbox_name','is_file'])
        conn = get_connection()
        df['is_file'] = df['is_file'].astype(int)
        current_list = pd.read_sql("select * from available_dls",conn)
        final_df = pd.concat([current_list,df[~df['seedbox_name'].isin(current_list['seedbox_name'])]])
        final_df['last_update_date'].fillna(datetime.datetime.now(),inplace=True)
        final_df['downloaded'].fillna(0,inplace=True) 
        final_df['hidden'].fillna(0,inplace=True) 
        final_df.to_sql('available_dls',conn,if_exists='replace',index=False)
        print("Data Saved: {}".format(df.shape[0]))
        logging.info("Data Saved: {}".format(df.shape[0]))
    except Exception as e:
        print("Error saving data: {}".format(e))
        logging.info("CRON_JOB: Error updating available DLS: {}".format(e))

def download_files():
    logging.info("CRON_JOB: Downloading Files")
    conn = get_connection()
    files_df = pd.read_sql("select * from downloads where download_state = 'QUEUED'",conn)
    logging.info("Files to download: {}".format(files_df.shape[0]))
    if files_df.shape[0]==0:
        print("No Files to download")
        logging.info("No files to download exitting")
        return
    files_df.sort_values(by='size',inplace=True)
    curs = conn.cursor()
    for row in files_df.iterrows():
        logging.info("Downloading file : {}".format(row[1]['seedbox_name']))
        curs.execute("UPDATE downloads set download_start = (datetime('now','localtime')) where seedbox_name = '{}'".format(row[1]['seedbox_name']))
        conn.commit()

        movie = row[1]['is_movie']
        is_file = row[1]['is_file']
        if movie==1:
            dl_path1 =os.path.join(PLEX_MOUNT,'movies')
        else:
            dl_path1 = os.path.join(PLEX_MOUNT,'tvshows')

        if is_file==0:
            dl_path1 = os.path.join(dl_path1,row[1]['seedbox_name'])
        logging.info("Download Started to path: {}".format(dl_path1))
        try:
            if is_file==1:
                shutil.copy2(os.path.join(FTP_MOUNT,row[1]['seedbox_name']),dl_path1)
            else:
                os.chdir(FTP_MOUNT)
                shutil.copytree(row[1]['seedbox_name'],dl_path1)
                
        except Exception as e:
            print("File already downloaded, we will update shit")
 
        curs.execute("UPDATE downloads set download_state='DONE', download_date=(datetime('now','localtime')), downloaded=1, download_path = '{}' where seedbox_name = '{}'".format(dl_path1,row[1]['seedbox_name']))
        curs.execute("UPDATE available_dls set downloaded =1, last_update_date = (datetime('now','localtime')),hidden=1 where seedbox_name = '{}'".format(row[1]['seedbox_name']))
        conn.commit()
        print("File: {} has finished downloading to path: {}".format(row[1]['seedbox_name'],row[1]['download_path']))

        logging.info("File: {} has finished downloading to path: {}".format(row[1]['seedbox_name'],dl_path1))
        logging.info("Trying to extract files")
        try:
            os.chdir('/home/pi/PlexApp/plex_app')
            output = subprocess.call("bash extract.sh {}".format(dl_path1),shell=True)
            if output==0:
                logging.info("Files Extracted")
            else:
                logging.info("Output = {}: Failed to extract".format(output))
        except Exception as e:
            logging.debug("Error extracting file {}".format(e))
        if TRANSFER_FILE:
            logging.info("Trying to transfer files")
            try:
                if movie==1:
                    add_path=os.path.join(TRANS_MOUNT,'movies')
                else:
                    add_path=os.path.join(TRANS_MOUNT,'tvshows')
                if is_file==1:
                    shutil.copy2(dl_path1,add_path)
                else:    
                    shutil.copytree(dl_path1,os.path.join(add_path,os.path.basename(dl_path1)))
                    logging.debug("File {} transferred to {}".format(dl_path1,add_path))
            except Exception as e:
                logging.debug("Error transfering file {}".format(e))
if __name__ == '__main__':
    script = 'update'
    if len(sys.argv)>1:
        script = sys.argv[1]
    if script == 'update':
        try:
            update_available_dls()
        except Exception as e:
            logging.debug("Failed to update available downloade files: Error: {}".format(e))
    elif script == 'download':
        try:
            download_files()
        except Exception as e:
            logging.debug("Failed to download files: Error: {}".format(e))
    else:
        sys.exit("Need to call download or update in order to run cron_scripts.")
