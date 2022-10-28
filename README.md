

### Installation
Installation steps:
```shell
sudo apt install python3 python3-pip python3-gst-1.0 gstreamer-1.0-alsa gstreamer1.0-plugins-ugly gstreamer1.0-plugins-good
pip3 install -r requirements.txt
```

Note: might need to also install `gstreamer1.0-plugins-bad`
Test the audio pipeline with:
```shell
gst-launch-1.0 -m audiotestsrc ! alsasink 
gst-launch-1.0 filesrc location=/home/pi/dragon_box/audio/wolf.mp3 ! mpegaudioparse ! lame ! audioconvert ! audioresample ! autoaudiosink
gst-launch-1.0 playbin uri=file:///home/pi/dragon_box/audio/wolf.mp3
```