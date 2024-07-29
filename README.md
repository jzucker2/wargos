# wargos

I plan on using the Home Assistant wled library: `wled` located here: https://pypi.org/project/wled/

## How to Run

### Configure Docker Compose

Example `docker-compose.yml` like:

```yaml
services:

  wargos:
    container_name: wargos
    image: ghcr.io/jzucker2/wargos
    restart: always
    extra_hosts:
      - "host.docker.internal:host-gateway"
    healthcheck:
      test: [ "CMD-SHELL", "curl -f http://host.docker.internal:9395/healthz || exit 1" ]
      interval: 30s
      timeout: 60s
      retries: 5
      start_period: 80s
    environment:
      - WLED_IP_LIST=10.0.1.1,10.0.1.2,10.0.1.3
    ports:
      - "9395:9395"
    stdin_open: true
    tty: true
```

### Set Env Vars

By default, logging is info level. To set to debug, provide the env `DEBUG=true` flag

|                   Env Var Name                   | Default Value |                 Example Value                  |                                         Description                                          |
|:------------------------------------------------:|:-------------:|:----------------------------------------------:|:--------------------------------------------------------------------------------------------:|
|                     `DEBUG`                      |    `false`    |                     `true`                     |                     This determines debug logging and a few other things                     |
| `DEFAULT_WLED_INSTANCE_SCRAPE_INTERVAL_SECONDS`  |     `60`      |                      `30`                      |     This determines how often `wargos` scrapes prometheus metrics from `wled` instances      |
|                  `WLED_IP_LIST`                  |    `None`     |       `10.0.1.150,10.0.1.179,10.0.1.153`       | This is the list of `,` separated IP addresses of `wled` instances that `wargos` will scrape |

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

### Add to Prometheus for Metrics Collection

Add this to your `prometheus.yml`

```yaml
- job_name: 'wargos'

  # metrics_path defaults to '/metrics'
  # scheme defaults to 'http'.
  static_configs:
    - targets: [ '<host_ip>:9395' ]
      labels:
        instance: 'host_machine'
```

## Scheduler

* https://fastapi-utils.davidmontague.xyz/
  * https://github.com/dmontagu/fastapi-utils
* https://github.com/amisadmin/fastapi-scheduler
* https://github.com/amisadmin/fastapi-amis-admin

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

# now test with prometheus metrics on default WLED instance
curl -i "http://localhost:9395/prometheus/default" \
    -H "Content-Type: application/json"

# now test with prometheus metrics for all WLED instances (set in env var for now)
curl -i "http://localhost:9395/prometheus/all" \
    -H "Content-Type: application/json"
```

### Logging

* https://stackoverflow.com/questions/77001129/how-to-configure-fastapi-logging-so-that-it-works-both-with-uvicorn-locally-and
  * This is the pattern I went with for now
* https://github.com/tiangolo/fastapi/discussions/7457

### Notes

```
Info(architecture='esp32', arduino_core_version='v3.3.6-16-gcc5440f6a2', brand='WLED', build=2406290, effect_count=187, filesystem=Filesystem(last_modified=datetime.datetime(2024, 7, 12, 21, 59, 57, tzinfo=datetime.timezone.utc), total=983, used=12), free_heap=178468, ip='10.0.1.xxx', leds=Leds(count=365, fps=5, light_capabilities=<LightCapability.RGB_COLOR|WHITE_CHANNEL: 3>, max_power=5000, max_segments=32, power=139, segment_light_capabilities=[<LightCapability.RGB_COLOR|WHITE_CHANNEL: 3>]), live_ip='', live_mode='', live=False, mac_address='44321c2184e9', name='Media Cabinet Light Strip', palette_count=71, product='FOSS', udp_port=21324, uptime=datetime.timedelta(days=16, seconds=2598), version=<AwesomeVersion SemVer '0.15.0-b4'>, websocket=2, wifi=Wifi(bssid='33:AB:00:CE:BA:21', channel=10, rssi=-27, signal=100))

State(brightness=255, nightlight=Nightlight(duration=60, mode=<NightlightMode.FADE: 1>, on=False, target_brightness=0), on=True, playlist_id=None, preset_id=None, segments={0: Segment(brightness=255, clones=-1, color=Color(primary=[16, 31, 14, 0], secondary=[255, 36, 182, 0], tertiary=[0, 0, 0, 0]), effect_id=0, intensity=128, length=365, on=True, palette_id=50, reverse=False, segment_id=0, selected=True, speed=128, start=0, stop=365, cct=127)}, sync=UDPSync(receive=True, receive_groups=<SyncGroup.GROUP1: 1>, send=True, send_groups=<SyncGroup.GROUP1: 1>), transition=7, live_data_override=<LiveDataOverride.OFF: 0>)
```
