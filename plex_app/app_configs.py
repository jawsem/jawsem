import logging
import os
file_path = os.path.dirname(os.path.abspath(__file__))
log_file = os.path.join(file_path, 'base_app.log')
logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s %(levelname)s %(threadName)s %(name)s %(message)s",
                            filename=log_file)
FTP_MOUNT = '/mnt/seedbox/rtorrent'
PLEX_MOUNT = '/mnt/seagate/plex_pi'
TRANS_MOUNT = '/mnt/arch'
TRANSFER_FILE=True
