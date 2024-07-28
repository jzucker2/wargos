# wargos

I plan on using the Home Assistant wled library: `wled` located here: https://pypi.org/project/wled/

## wled

* https://kno.wled.ge/
  * main `wled` site
* https://github.com/frenck/python-wled
  * github repo for the python client
* https://www.home-assistant.io/integrations/wled/
  * Home Assistant page for the integration

## Prometheus

For prometheus I have some options:

* https://github.com/trallnag/prometheus-fastapi-instrumentator
* https://github.com/prometheus/client_python
* https://prometheus.github.io/client_python/
* https://prometheus.github.io/client_python/exporting/http/fastapi-gunicorn/

## fastapi

I am new to fastapi

* https://fastapi.tiangolo.com/tutorial/
* https://fastapi.tiangolo.com/advanced/
* https://fastapi.tiangolo.com/how-to/general/

## Development

Notes about dev work here.

### Curl Commands

```
# healthcheck
curl -i "http://localhost:9395/healthz" \
    -H "Content-Type: application/json"

# simple WLED test
curl -i "http://localhost:9395/test" \
    -H "Content-Type: application/json"

# now test with prometheus metrics too WLED test
curl -i "http://localhost:9395/prometheus/test" \
    -H "Content-Type: application/json"
```

### Notes

```
Info(architecture='esp32', arduino_core_version='v3.3.6-16-gcc5440f6a2', brand='WLED', build=2406290, effect_count=187, filesystem=Filesystem(last_modified=datetime.datetime(2024, 7, 12, 21, 59, 57, tzinfo=datetime.timezone.utc), total=983, used=12), free_heap=178468, ip='10.0.1.xxx', leds=Leds(count=365, fps=5, light_capabilities=<LightCapability.RGB_COLOR|WHITE_CHANNEL: 3>, max_power=5000, max_segments=32, power=139, segment_light_capabilities=[<LightCapability.RGB_COLOR|WHITE_CHANNEL: 3>]), live_ip='', live_mode='', live=False, mac_address='44321c2184e9', name='Media Cabinet Light Strip', palette_count=71, product='FOSS', udp_port=21324, uptime=datetime.timedelta(days=16, seconds=2598), version=<AwesomeVersion SemVer '0.15.0-b4'>, websocket=2, wifi=Wifi(bssid='33:AB:00:CE:BA:21', channel=10, rssi=-27, signal=100))

State(brightness=255, nightlight=Nightlight(duration=60, mode=<NightlightMode.FADE: 1>, on=False, target_brightness=0), on=True, playlist_id=None, preset_id=None, segments={0: Segment(brightness=255, clones=-1, color=Color(primary=[16, 31, 14, 0], secondary=[255, 36, 182, 0], tertiary=[0, 0, 0, 0]), effect_id=0, intensity=128, length=365, on=True, palette_id=50, reverse=False, segment_id=0, selected=True, speed=128, start=0, stop=365, cct=127)}, sync=UDPSync(receive=True, receive_groups=<SyncGroup.GROUP1: 1>, send=True, send_groups=<SyncGroup.GROUP1: 1>), transition=7, live_data_override=<LiveDataOverride.OFF: 0>)
```
