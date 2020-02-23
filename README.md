# Train Scraper

Lots of trains go past my flat. This tells me when they're coming so I can turn the TV volume up. 

## How to run

Uses python 3.8. Run as a package from the directory above:

```
$ python -m trains  --map lec1 --berths foo,bar,baz
```

## Find your parameters

* Load up your local map on www.opentraintimes.com
* The "map" argument will be the last part of the url (e.g. 'lec1' for Euston to Wembley Central)
* Either:
    * Open the network tab and download the svg map
    * "Inspect Element" on each berth (black box)
* example berth: WY0118

## Set defaults

Make a file called `my_defaults.py` and add the default variables:

```python
default_map = "lec1"
default_berths = [
    "WY0118",  # Random ones. I do not live here.
    "WS0004",
    "WS0002",
]
```