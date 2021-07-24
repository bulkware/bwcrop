# bwcrop

An application to automatically crop image files.


## Running on Linux

### Installing dependencies (Debian-based systems)
Open your terminal application and type:
`sudo apt install python3 python3-gi python3-gi-cairo gir1.2-gtk-3.0`

Hit enter. Enter your password when prompted. Answer yes to the question about
using additional disk space.

### Downloading the source
git clone https://github.com/bulkware/bwcrop.git

### Running the application
Enter the application directory using this command:
`cd bwcrop`

Generate DConf settings:
`make dconf-schema`

You can run the application from the source code using this command:
`python3 src/bwcrop.py`
