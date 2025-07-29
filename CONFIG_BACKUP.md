# Config and Preset Backup

This document describes the config and preset backup functionality in Wargos.

## Overview

The backup feature allows you to collect configuration and preset backups from WLED instances and store them in an organized directory structure. Files are stored in IP-specific subdirectories with separate folders for configs and presets.

## Directory Structure

Backups are stored in the following structure:

```
{backup_dir}/
├── {device_ip}/
│   ├── configs/
│   │   └── {device_ip}_{timestamp}_configs.json
│   └── presets/
│       └── {device_ip}_{timestamp}_presets.json
```

## Configuration

### Environment Variables

- `CONFIG_BACKUP_DIR`: Directory to store backups (default: `/backups/`)
- `WLED_IP_LIST`: Comma-separated list of WLED device IP addresses

## API Endpoints

### Config Backup

#### Backup All Configs

```
GET /config/backup/all
```

Backs up configs from all WLED instances.

#### Backup Single Config

```
GET /config/backup/{device_ip}
```

Backs up config from a single WLED instance.

#### Backup All Configs to Custom Directory

```
GET /config/backup/all/custom?backup_dir=/custom/path
```

Backs up configs from all WLED instances to a custom directory.

### Preset Backup

#### Backup All Presets

```
GET /presets/backup/all
```

Backs up presets from all WLED instances.

#### Backup Single Preset

```
GET /presets/backup/{device_ip}
```

Backs up presets from a single WLED instance.

### Combined Backup

#### Backup All (Configs and Presets)

```
GET /backup/all
```

Backs up both configs and presets from all WLED instances.

### Download Latest Backup

#### Download Latest Config

```
GET /config/download/{device_ip}?include_metadata=false
```

Downloads the latest config backup file for a specific WLED instance as a JSON file.

**Parameters:**

- `device_ip` (path): The IP address of the WLED device
- `include_metadata` (query, optional): Whether to include backup metadata in the response (default: false)

#### Download Latest Presets

```
GET /presets/download/{device_ip}?include_metadata=false
```

Downloads the latest presets backup file for a specific WLED instance as a JSON file.

**Parameters:**

- `device_ip` (path): The IP address of the WLED device
- `include_metadata` (query, optional): Whether to include backup metadata in the response (default: false)

**Response:**

- **Success**: Returns the backup file as a downloadable JSON file
- **Not Found**: Returns error message if no backup directory or files exist
- **Error**: Returns error message if an exception occurs

**Examples:**

```bash
# Download latest config for a device (metadata stripped by default)
curl -O -J "http://localhost:8000/config/download/192.168.1.100"

# Download latest config with metadata
curl -O -J "http://localhost:8000/config/download/192.168.1.100?include_metadata=true"

# Download latest presets for a device
curl -O -J "http://localhost:8000/presets/download/192.168.1.100"

# Download latest presets with metadata
curl -O -J "http://localhost:8000/presets/download/192.168.1.100?include_metadata=true"
```

**File Response Headers:**

- `Content-Type: application/json`
- `Content-Disposition: attachment; filename="{device_ip}_latest_backup.json"`

**Note:** By default, the `_backup_metadata` field is stripped from the downloaded file to provide a clean WLED configuration. Use `include_metadata=true` to preserve the backup metadata.

## Backup File Format

### Config Files

Config files contain the WLED device configuration in JSON format with added metadata:

```json
{
  "wifi": {
    "ssid": "MyNetwork",
    "pass": "password123"
  },
  "leds": {
    "count": 60,
    "fps": 60
  },
  "_backup_metadata": {
    "backup_timestamp": "2025-07-28T11:48:01.123456",
    "device_ip": "192.168.1.100",
    "backup_source": "wargos"
  }
}
```

### Preset Files

Preset files contain the WLED device presets in JSON format with added metadata:

```json
{
  "presets": [
    {
      "id": 1,
      "name": "Rainbow",
      "segments": [...]
    }
  ],
  "_backup_metadata": {
    "backup_timestamp": "2025-07-28T11:48:01.123456",
    "device_ip": "192.168.1.100",
    "backup_source": "wargos",
  }
}
```

**Special Case - Empty Presets:**
If a WLED device returns `{"0": {}}` for its presets, no backup file is created. This is tracked in Prometheus metrics with status `empty_presets`. When downloading presets, if the latest file contains `{"0": {}}`, the download endpoint returns a JSON response indicating no presets are available.

## File Naming Convention

Files are named using the pattern: `{device_ip}_{timestamp}_{type}.json`

- **Config files**: `{device_ip}_{timestamp}_configs.json`
- **Preset files**: `{device_ip}_{timestamp}_presets.json`

Example:

- `192.168.1.100_20250728_114801_configs.json`
- `192.168.1.100_20250728_114801_presets.json`

## Error Handling

The backup system handles various error conditions:

- **Network errors**: Connection timeouts, unreachable devices
- **HTTP errors**: 404, 500, etc.
- **File system errors**: Permission denied, disk full
- **Invalid responses**: Malformed JSON, unexpected data

All errors are logged and returned in the API response with appropriate status codes.

## Usage Examples

### Basic Usage

```bash
# Backup all configs
curl "http://localhost:8000/config/backup/all"

# Backup all presets
curl "http://localhost:8000/presets/backup/all"

# Backup both configs and presets
curl "http://localhost:8000/backup/all"

# Backup single device config
curl "http://localhost:8000/config/backup/192.168.1.100"

# Backup single device presets
curl "http://localhost:8000/presets/backup/192.168.1.100"
```

### Download Examples

```bash
# Download latest config (clean)
curl -O -J "http://localhost:8000/config/download/192.168.1.100"

# Download latest config with metadata
curl -O -J "http://localhost:8000/config/download/192.168.1.100?include_metadata=true"

# Download latest presets (clean)
curl -O -J "http://localhost:8000/presets/download/192.168.1.100"

# Download latest presets with metadata
curl -O -J "http://localhost:8000/presets/download/192.168.1.100?include_metadata=true"
```

## Integration with Existing Features

The backup feature integrates seamlessly with the existing Wargos functionality:

- Uses the same WLED IP list as the metrics scraping
- Follows the same error handling patterns
- Integrates with the existing logging system
- Compatible with the existing FastAPI application structure
- **Prometheus Metrics**: Comprehensive metrics collection for monitoring backup operations

## Prometheus Metrics

The backup feature provides detailed Prometheus metrics for monitoring:

### Operation Metrics

- `wargos_backup_operations_total`: Total number of backup operations (labeled by operation_type, device_ip, status, backup_type)
- `wargos_backup_operation_duration_seconds`: Duration of backup operations (labeled by operation_type, device_ip, backup_type)

**Status Values:**

- `success`: Operation completed successfully
- `error`: Operation failed with an error
- `not_found`: No backup directory or files found
- `empty_presets`: Preset backup skipped due to empty presets (special case)

**Backup Type Values:**

- `config`: Config backup operations
- `preset`: Preset backup operations
- `combined`: Combined config and preset backup operations

### Error Metrics

- `wargos_backup_operation_exceptions_total`: Total number of exceptions during backup operations (labeled by operation_type, device_ip, exception_type, backup_type)
- `wargos_backup_http_errors_total`: Total number of HTTP errors during backup operations (labeled by device_ip, http_status_code, backup_type)
- `wargos_backup_connection_errors_total`: Total number of connection errors during backup operations (labeled by device_ip, error_type, backup_type)

### File Metrics

- `wargos_backup_files_created_total`: Total number of backup files created (labeled by device_ip, backup_type)
- `wargos_backup_file_size_bytes`: Size of the most recent backup file in bytes (labeled by device_ip, backup_type)

### Example Queries

```promql
# Successful config backup operations
wargos_backup_operations_total{status="success", backup_type="config"}

# Successful preset backup operations
wargos_backup_operations_total{status="success", backup_type="preset"}

# Empty presets operations
wargos_backup_operations_total{status="empty_presets", backup_type="preset"}

# Config backup operation duration
histogram_quantile(0.95, rate(wargos_backup_operation_duration_seconds_bucket{backup_type="config"}[5m]))

# Preset backup operation duration
histogram_quantile(0.95, rate(wargos_backup_operation_duration_seconds_bucket{backup_type="preset"}[5m]))

# HTTP errors by status code and backup type
wargos_backup_http_errors_total

# File creation rate by backup type
rate(wargos_backup_files_created_total[5m])
```

## Testing
