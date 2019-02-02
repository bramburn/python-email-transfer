#!/usr/bin/env python
import main.py

ms = mapsync('from_server','to_server')

ms.SyncFolder('from_emailbox','from_password','to_emailbox','to_password')

