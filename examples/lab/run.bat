REM proper ordering is important
start /B python lobby.py virtual 127.0.0.3
start /B python bathroom.py virtual 127.0.0.1
start /B python bedroom.py virtual 127.0.0.2
start /B python kitchen.py virtual 127.0.0.4
start /B python living_room.py virtual 127.0.0.5
