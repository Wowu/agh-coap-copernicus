# agh-coap-copernicus

CoAP server for VirtualCopernicus

## Requirements

- Python 3.7
- `virtualenvwrapper` (optional)

## Installation

With `virtualenvwrapper` installed:

```bash
mkvirtualenv agh-coap-copernicus
pip install -r requirements.txt
```

It may be required to install `portaudio` library in system:

```bash
apt install libportaudio2
```

On Raspberry pi you may need to install additional dependencies:

```bash
sudo apt install libatlas3-base
```

#### Adding new dependencies

```bash
pip install <name>
pip freeze > requirements.txt
```

## Running

```bash
workon agh-coap-copernicus
python server/server.py virtual
python client/client.py
```

## Usage instruction

### Server

CoAP server allows to create following types of resources:

- Generic GPIO
- LED
- Buzzer
- AngularServo
- Button

Resources can be added in the following way:
```
root.add_resource(['.well-known', 'core'],
                  resource.WKCResource(root.get_resources_as_linkheader))
root.add_resource(['servo'], ServoResource(17))
root.add_resource(['led1'], LEDResource(21))
root.add_resource(['button1'], ButtonResource(11, lambda: print("Pressed")), lambda: print("Released")))
root.add_resource(['buzzer'], BuzzerResource(16))
root.add_resource(['gpio_buzzer'], GPIOResource(15))
```

### Client

#### Get resource value
```
g <resource_name>
```

#### Set resource value
```
s <resource_name> <options>
```
##### GPIO options:

- `0`, `off`
- `1`, `on`

##### Servo options:

- `<angle>` - must be between `min_angle` and `max_angle`

##### Buzzer/LED options:

- `0`, `off`
- `1`, `on`
- `-1`, `toggle`
- `beep <on_time> <off_time> <n>` for buzzer
- `blink <on_time> <off_time> <n>` for LED


## Systemd service

Install using the following commands:

```bash
sudo cp agh-coap-copernicus.service /etc/systemd/system
sudo systemctl enable agh-coap-copernicus
sudo systemctl start agh-coap-copernicus
```

View logs:

```bash
sudo journalctl -xfu agh-coap-copernicus
```

---


# TODO

## Phase 1
~~1. Ogarnąć jak działają zasoby w CoAPie~~

~~2. Ogarnąć libkę do serwera CoAP w Pythonie~~

## Phase 2
~~3. Ogarnąć jak działa wszystkie 5 wymaganych typów zasobów w gpiozero~~

~~4. Zobaczyć w jaki sposób podawać implementację gpiozero (virtualcopernicus)~~

## Phase 3

- [ ] Próba uruchomienia na Raspberry Pi i nagranie @wowu @def-au1t
- [x] Observable button ~~@rivit98~~ @def-au1t
- [ ] Przygotować projekt @wowu @def-au1t
   - [ ] Opisujemy scenariusz - sterownik świateł w oparciu o CoAP
   - [ ] Jest serwer który udostępnia observable button
   - [ ] Jest klient który zapala diodę po kliknięciu buttona
   - [ ] Małe sprawozdanie @kuczi55
- [ ] Dokumentacja (uwzględnić m3 i dostosować rozmiary obrazków) @kuczi55
  - [ ] Dopisać o systemd

@wowu Tue Jan 12 00:17:49 2021: Dodałem plik `lab.md` który zawiera wstęp do laboratorium.
