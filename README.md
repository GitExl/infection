# Infection

_UAC Research Base Delta has unexpectedly gone dark. Delta base, situated in an undisclosed location in the northern United States, is tasked with experimenting on salvaged remnants of the demon army that invaded Mars. Your job is to find out what the hell happened and at your own discretion, take care of whatever evil is taking place there now._

This mapset should take around 60 minutes to complete on Ultra-Violence, provided you don't die too often. All maps were balanced to be played in order, though pistol starts are doable with some extra effort.

This was tested with GZDoom, DSDADoom and PrBoom+ UM. It should be playable in all limit removing source ports that have support for MBF21, DEHEXTRA and UMAPINFO. There are a few minor enhancements available when playing in GZDoom and in recent versions of Eternity.


## Build requirements

To build the resource WAD and release WAD:

* Python > 3.8
* Pillow (`pip install pillow`)

Photoshop is required for editing the sprite, texture and graphics source files.


## Build instructions

Copy `config_assemble_local.example.json` to `config_assemble_local.json` and adjust the paths to match your local ones.

To make a `data.wad` file containing all the project's resources, run

```py assemble.py resources```

Building the resources will also output the used flats and textures into CSV files.

To make a release build that includes the maps and has all unused textures and flats stripped, run

```py assemble.py release```


## Corruption instructions

Copy `config_corrupt_local.example.json` to `config_corrupt_local.json` and adjust the list of WADs that you want to load from to match your local paths.

To generate corrupted versions of the sprites and sounds configured in `config_corrupt.json`, run

```py corrupt.py```
