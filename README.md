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

## Project docs:
[Link](dokumentacja.pdf)
