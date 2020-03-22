## Application that connects to seedbox and creates a web ui to easily download files

### Directions:

1. Install plex media server on raspberry pi
2. Add a mount for the FTP server you wish to use
3. Optional add a mount for the external hard drive you need to save your files.
4. Run main.py in the plex_app directory

This will create a simple web application that will list the files and directories available for download.  You can click the files and specify if you want to download the as a Movie and a TV shows.

Cron jobs run hourly to check if there are updated movies and daily to download files (downloading occurs at night as not to interfere with normal activities).

You can specify your mounted directories in app_configs.py.  It will route the files based on whether you choose a movie or directory.
