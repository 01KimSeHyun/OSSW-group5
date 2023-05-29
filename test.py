#!/usr/bin/env python
# coding: utf-8

# In[1]:


pip install python-vlc


# In[3]:


pip show python-vlc


# In[12]:


pip install youtube_dl


# In[1]:


import os
import sys
import queue
import platform
import youtube_dl
import platform

from PyQt5 import QtWidgets, QtGui, QtCore
import vlc
from network import Client


class MiniPlayer(QtWidgets.QMainWindow):
    """Stripped-down PyQt5-based media player class to sync with "master" video.
    """

    def __init__(self, data_queue, master=None):
        QtWidgets.QMainWindow.__init__(self, master)
        self.setWindowTitle("Mini Player")
        self.statusbar = self.statusBar()
        self.statusbar.showMessage("Ready")

        # Create a basic vlc instance
        self.instance = vlc.Instance()

        self.media = None

        # Create an empty vlc media player
        self.mediaplayer = self.instance.media_player_new()

        self.init_ui()
        self.open_file()

        self.timer = QtCore.QTimer(self)
        self.timer.setInterval(10)
        self.timer.timeout.connect(self.update_ui)

        self.data_queue = data_queue
        self.timer.start()
        
    def open_youtube_video(self):
        """Open a YouTube video in a MediaPlayer
        """
        ydl_opts = {
            'format': 'best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }
        video_url = "https://www.youtube.com/watch?v=pTpFKacxBa0&ab_channel=HanyangUniversity%ED%95%9C%EC%96%91%EB%8C%80%ED%95%99%EA%B5%90ERICA"
        video_id = video_url.split("=")[1].split("&")[0]

        ydl_opts = {
            'format': 'best',
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4',
            }],
        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_id, download=False)
            url = info_dict['formats'][0]['url']

        # Set the media URL
        self.media = self.instance.media_new(url)

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in its own window). This is platform-specific,
        # so we must give the ID of the QFrame (or similar object) to vlc.
        # Different platforms have different functions for this.
        if platform.system() == "Linux":  # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows":  # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))
        
    

    def init_ui(self):
        """Set up the user interface
        """
        self.widget = QtWidgets.QWidget(self)
        self.setCentralWidget(self.widget)

        # In this widget, the video will be drawn
        if platform.system() == "Darwin":  # for MacOS
            self.videoframe = QtWidgets.QMacCocoaViewContainer(0)
        else:
            self.videoframe = QtWidgets.QFrame()

        self.palette = self.videoframe.palette()
        self.palette.setColor(QtGui.QPalette.Window, QtGui.QColor(0, 0, 0))
        self.videoframe.setPalette(self.palette)
        self.videoframe.setAutoFillBackground(True)

        self.vboxlayout = QtWidgets.QVBoxLayout()
        self.vboxlayout.addWidget(self.videoframe)
        self.widget.setLayout(self.vboxlayout)

    def open_file(self):
        """Open a media file in a MediaPlayer
        """
        dialog_txt = "Choose Media File"
        filename = QtWidgets.QFileDialog.getOpenFileName(self, dialog_txt, os.path.expanduser('~'))
        if not filename[0]:
            return

        # getOpenFileName returns a tuple, so use only the actual file name
        self.media = self.instance.media_new(filename[0])

        # Put the media in the media player
        self.mediaplayer.set_media(self.media)

        # Parse the metadata of the file
        self.media.parse()

        # Set the title of the track as the window title
        self.setWindowTitle("{}".format(self.media.get_meta(0)))

        # The media player has to be 'connected' to the QFrame (otherwise the
        # video would be displayed in it's own window). This is platform
        # specific, so we must give the ID of the QFrame (or similar object) to
        # vlc. Different platforms have different functions for this
        if platform.system() == "Linux":  # for Linux using the X Server
            self.mediaplayer.set_xwindow(int(self.videoframe.winId()))
        elif platform.system() == "Windows":  # for Windows
            self.mediaplayer.set_hwnd(int(self.videoframe.winId()))
        elif platform.system() == "Darwin":  # for MacOS
            self.mediaplayer.set_nsobject(int(self.videoframe.winId()))

        # Start playing the video as soon as it loads
        self.mediaplayer.play()

    def update_ui(self):
        self.update_statusbar()

        try:
            val = self.data_queue.get(block=False)
        except queue.Empty:
            return

        if val == '<':
            self.mediaplayer.set_rate(self.mediaplayer.get_rate() * 0.5)
            return
        if val == '>':
            self.mediaplayer.set_rate(self.mediaplayer.get_rate() * 2)
            return
        if val == 'P':
            self.mediaplayer.play()
            return
        if val == 'p':
            self.mediaplayer.pause()
            return
        if val == 'S':
            self.mediaplayer.stop()
            return

        val = int(val)
        if val != self.mediaplayer.get_time():
            self.mediaplayer.set_time(val)

    def update_statusbar(self):
        mtime = QtCore.QTime(0, 0, 0, 0)
        time = mtime.addMSecs(self.mediaplayer.get_time())
        self.statusbar.showMessage(time.toString())


def main():
    """Entry point for our simple vlc player
    """
    app = QtWidgets.QApplication(sys.argv)

    data_queue = queue.Queue()

    player = MiniPlayer(data_queue)
    player.show()
    player.resize(480, 480)

    _ = Client("localhost", 8888, data_queue)
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

    
    


# In[1]:


{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 1,
   "id": "a148f62e",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "Collecting https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz\n",
      "  Using cached https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz (2.4 MB)\n",
      "  Installing build dependencies: started\n",
      "  Installing build dependencies: finished with status 'done'\n",
      "  Getting requirements to build wheel: started\n",
      "  Getting requirements to build wheel: finished with status 'done'\n",
      "  Installing backend dependencies: started\n",
      "  Installing backend dependencies: finished with status 'done'\n",
      "  Preparing metadata (pyproject.toml): started\n",
      "  Preparing metadata (pyproject.toml): finished with status 'done'\n",
      "Collecting pycryptodomex\n",
      "  Using cached pycryptodomex-3.18.0-cp35-abi3-win_amd64.whl (1.7 MB)\n",
      "Collecting brotli\n",
      "  Using cached Brotli-1.0.9-cp39-cp39-win_amd64.whl (383 kB)\n",
      "Collecting certifi\n",
      "  Using cached certifi-2023.5.7-py3-none-any.whl (156 kB)\n",
      "Collecting mutagen\n",
      "  Using cached mutagen-1.46.0-py3-none-any.whl (193 kB)\n",
      "Collecting websockets\n",
      "  Using cached websockets-11.0.3-cp39-cp39-win_amd64.whl (124 kB)\n",
      "Building wheels for collected packages: yt-dlp\n",
      "  Building wheel for yt-dlp (pyproject.toml): started\n",
      "  Building wheel for yt-dlp (pyproject.toml): finished with status 'done'\n",
      "  Created wheel for yt-dlp: filename=yt_dlp-2023.3.4-py2.py3-none-any.whl size=2703539 sha256=d3565d553282c01c2785ef4cae898567fd219e5463ba1734fe55936e2c7baac1\n",
      "  Stored in directory: C:\\Users\\Jeong\\AppData\\Local\\Temp\\pip-ephem-wheel-cache-m_1hws8x\\wheels\\17\\62\\6f\\3db33a84feab4a3387d47a6ce0d53bd24fc437809b48b1c5e5\n",
      "Successfully built yt-dlp\n",
      "Installing collected packages: brotli, websockets, pycryptodomex, mutagen, certifi, yt-dlp\n",
      "  Attempting uninstall: brotli\n",
      "    Found existing installation: Brotli 1.0.9\n",
      "    Uninstalling Brotli-1.0.9:\n",
      "      Successfully uninstalled Brotli-1.0.9\n",
      "  Attempting uninstall: websockets\n",
      "    Found existing installation: websockets 11.0.3\n",
      "    Uninstalling websockets-11.0.3:\n",
      "      Successfully uninstalled websockets-11.0.3\n",
      "  Attempting uninstall: pycryptodomex\n",
      "    Found existing installation: pycryptodomex 3.18.0\n",
      "    Uninstalling pycryptodomex-3.18.0:\n",
      "      Successfully uninstalled pycryptodomex-3.18.0\n",
      "  Attempting uninstall: mutagen\n",
      "    Found existing installation: mutagen 1.46.0\n",
      "    Uninstalling mutagen-1.46.0:\n",
      "      Successfully uninstalled mutagen-1.46.0\n",
      "  Attempting uninstall: certifi\n",
      "    Found existing installation: certifi 2023.5.7\n",
      "    Uninstalling certifi-2023.5.7:\n",
      "      Successfully uninstalled certifi-2023.5.7\n",
      "  Attempting uninstall: yt-dlp\n",
      "    Found existing installation: yt-dlp 2023.3.4\n",
      "    Uninstalling yt-dlp-2023.3.4:\n",
      "      Successfully uninstalled yt-dlp-2023.3.4\n",
      "Successfully installed brotli-1.0.9 certifi-2023.5.7 mutagen-1.46.0 pycryptodomex-3.18.0 websockets-11.0.3 yt-dlp-2023.3.4\n",
      "Note: you may need to restart the kernel to use updated packages.\n"
     ]
    },
    {
     "name": "stderr",
     "output_type": "stream",
     "text": [
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "    WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "    WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "    WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "    WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "    WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "    WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.\n",
      "anaconda-project 0.11.1 requires ruamel-yaml, which is not installed.\n",
      "conda-repo-cli 1.0.20 requires clyent==1.2.1, but you have clyent 1.2.2 which is incompatible.\n",
      "conda-repo-cli 1.0.20 requires nbformat==5.4.0, but you have nbformat 5.5.0 which is incompatible.\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n",
      "WARNING: Ignoring invalid distribution -ycryptodomex (c:\\users\\jeong\\anaconda3\\lib\\site-packages)\n"
     ]
    }
   ],
   "source": [
    "pip install --force-reinstall https://github.com/yt-dlp/yt-dlp/archive/master.tar.gz"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "2d42bebd",
   "metadata": {},
   "outputs": [
    {
     "name": "stdout",
     "output_type": "stream",
     "text": [
      "[youtube] Extracting URL: http://www.youtube.com/watch?v=Lr9xbHtpAfU\n",
      "[youtube] Lr9xbHtpAfU: Downloading webpage\n",
      "[youtube] Lr9xbHtpAfU: Downloading android player API JSON\n",
      "[youtube] Lr9xbHtpAfU: Downloading MPD manifest\n",
      "[info] Lr9xbHtpAfU: Downloading 1 format(s): 248+251\n",
      "[dashsegments] Total fragments: 54\n",
      "[download] Destination: 저장 경로 템플릿.f248.webm\n",
      "[download] 100% of   55.26MiB in 00:00:22 at 2.42MiB/s                   Done downloading, now converting ...\n",
      "\n",
      "[download] Destination: 저장 경로 템플릿.f251.webm\n",
      "[download] 100% of    4.63MiB in 00:00:00 at 8.62MiB/s   Done downloading, now converting ...\n",
      "\n",
      "[Merger] Merging formats into \"저장 경로 템플릿.webm\"\n",
      "Deleting original file 저장 경로 템플릿.f248.webm (pass -k to keep)\n",
      "Deleting original file 저장 경로 템플릿.f251.webm (pass -k to keep)\n"
     ]
    }
   ],
   "source": [
    "from __future__ import unicode_literals\n",
    "import yt_dlp as youtube_dl\n",
    "\n",
    "def my_hook(d):\n",
    "    if d['status'] == 'finished':\n",
    "        print('Done downloading, now converting ...')\n",
    "\n",
    "ydl_opts = {\n",
    "    'download_archive': 'archive.txt',\n",
    "    'ignoreerrors': True,\n",
    "    'nooverwrites': True,\n",
    "    'format': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]/best',       \n",
    "    'outtmpl': '저장 경로 템플릿',        \n",
    "    'noplaylist' : False,       \n",
    "    'progress_hooks': [my_hook],  \n",
    "}\n",
    "\n",
    "with youtube_dl.YoutubeDL(ydl_opts) as ydl:\n",
    "    ydl.download(['http://www.youtube.com/watch?v=Lr9xbHtpAfU'])\n",
    "\n",
    "\n"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3 (ipykernel)",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.9.7"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}


# In[ ]:




