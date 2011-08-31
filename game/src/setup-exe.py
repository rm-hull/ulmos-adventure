#!/usr/bin/env python

from distutils.core import setup

import py2exe

setup(windows = ["play.py"],
      # console = ["play.py"],
      name = "rpg-world",
      version = "0.9",
      packages=["rpg"],
      author="Sam Eldred",
      author_email="samuel.eldred@googlemail.com",
      url="http://code.google.com/p/rpg-world/",
      data_files=[("maps", ["maps/caves.map", "maps/central.map", "maps/east.map"]),
                  ("sounds", ["sounds/door.wav", "sounds/lifelost.wav", "sounds/pickup.wav", "sounds/wasp.wav"]),
                  ("tiles", ["tiles/dungeon.png", "tiles/dungeon_metadata.txt", "tiles/earth.png", "tiles/earth_metadata.txt", "tiles/grass.png", "tiles/grass_metadata.txt", "tiles/objects.png", "tiles/objects_metadata.txt", "tiles/water.png", "tiles/water_metadata.txt", "tiles/wood.png", "tiles/wood_metadata.txt"]),
                  ("sprites", ["sprites/beetle-frames.png", "sprites/chest.png", "sprites/coin-frames.png", "sprites/door-frames.png", "sprites/flame-frames.png", "sprites/font.png", "sprites/key-frames.png", "sprites/life.png", "sprites/numbers.png", "sprites/rock.png", "sprites/small-coin.png", "sprites/small-key.png", "sprites/ulmo-frames.png", "sprites/wasp-frames.png"])]
)
