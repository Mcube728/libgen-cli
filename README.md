# libgen-cli

A command line utility written in python to download books from https://gen.lib.rus.ec/

## Dependencies
You can install the dependencies like so:
```
pip install -r requirements.txt
```
## Usage
First create a file config.py and configure the settings in it. This allows for optimal execution of the script!!! This is how the configure.py file looks like: 
```
DOWNLOAD_PATH = "/path/to/download/directory/"  # Put your download directory here!!
```
libgen-cli.py help:
```
libgen-cli.py --help
usage: libgen-cli.py [-h] [-t | -a | -p] search [search ...]        

A simple python script to download books off https://gen.lib.rus.ec/

positional arguments:
  search           search term

options:
  -h, --help       show this help message and exit
  -t, --title      get books with the queried title
  -a, --author     get books written by the queried author
  -p, --publisher  get books from the queried publisher
```
A screenshot:
![A Screenshot of the interface](https://i.imgur.com/nWTXCZh.png)
(I have taken a bit of inspiration from <a href="https://github.com/NadalVRoMa/PyLibGen">Nadal Rodrigo's</a> python script!)
