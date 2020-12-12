# agh-coap-copernicus

CoAP server for VirtualCopernicus provided GPIO

## Requirements

- Python 3.7
- virtualenvwrapper (optional)

## Installation

With virtualenvwrapper installed:

```bash
mkvirtualenv agh-coap-copernicus
pip install -r requirements.txt
```

## Running

```bash
workon agh-coap-copernicus
python server/server.py virtual
python server/client.py
```

## Adding new dependencies

```bash
pip install <name>
pip freeze > requirements.txt
```

# TODO

## Research
1. Ogarnąć jak działają zasoby w CoAPie
2. Ogarnąć libkę do serwera CoAP w Pythonie
3. Ogarnąć jak działa wszystkie 5 wymaganych typów zasobów w gpiozero
4. Zobaczyć w jaki sposób podawać implementację gpiozero (virtualcopernicus)

## TODO
5. Serwer w CoAPie sterujący GPIO
6. Próba uruchomienia na Raspberry Pi i nagranie(?)
7. Dokumentacja
8. Przygotować przykładowe programy
