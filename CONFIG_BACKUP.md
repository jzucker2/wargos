# WLED Config Backup Feature

This document describes the new config backup functionality added to Wargos.

## Overview

The config backup feature allows you to collect configuration backups from WLED instances and store them in a configurable directory. Each backup includes the full configuration from the WLED device's `/cfg.json` endpoint. Files are automatically organized in IP-specific subdirectories for easy management.

## Configuration

### Environment Variables

- `CONFIG_BACKUP_DIR`: Directory where config backups will be stored (default: `/backups/`)
- `WLED_IP_LIST`: Comma-separated list of WLED device IP addresses (required for bulk operations)

## API Endpoints

### Backup All Instances

```
GET /config/backup/all
```

Backs up configs from all WLED instances defined in the `WLED_IP_LIST` environment variable.

**Response:**

```json
{
  "message": "Config backup completed",
  "results": [
    {
      "device_ip": "192.168.1.100",
      "filepath": "/backups/192.168.1.100/192.168.1.100_20250728_114801.json",
      "timestamp": "20250728_114801",
      "status": "success"
    }
  ],
  "backup_dir": "/backups/"
}
```

### Backup Single Instance

```
GET /config/backup/{device_ip}
```

Backs up config from a specific WLED instance.

**Response:**

```json
{
  "message": "Config backup completed",
  "result": {
    "device_ip": "192.168.1.100",
    "filepath": "/backups/192.168.1.100/192.168.1.100_20250728_114801.json",
    "timestamp": "20250728_114801",
    "status": "success"
  },
  "backup_dir": "/backups/"
}
```

### Backup All Instances to Custom Directory

```
GET /config/backup/all/custom?backup_dir=/custom/path
```

Backs up configs from all WLED instances to a custom directory.

## Backup File Format

Each backup file contains:

- The complete WLED configuration from `/cfg.json`
- Metadata about the backup:
  - `backup_timestamp`: ISO timestamp of when the backup was created
  - `device_ip`: IP address of the source device
  - `backup_source`: Always "wargos"

**Example backup file structure:**

```json
{
  "cfg": {
    "ver": "0.14.0-b1",
    "leds": {
      "count": 60,
      "rgbw": false,
      "pin": [2],
      "pwr": 850,
      "maxseg": 16,
      "seglock": false
    }
  },
  "_backup_metadata": {
    "backup_timestamp": "2025-07-28T11:48:01.153456",
    "device_ip": "192.168.1.100",
    "backup_source": "wargos"
  }
}
```

## File Naming Convention

Backup files are stored in IP-specific subdirectories using the pattern:

```
{backup_dir}/{device_ip}/{device_ip}_{timestamp}.json
```

Where:

- `backup_dir`: The configured backup directory (default: `/backups/`)
- `device_ip`: The IP address of the WLED device
- `timestamp`: Format `YYYYMMDD_HHMMSS`

**Example directory structure:**

```
/backups/
├── 192.168.1.100/
│   ├── 192.168.1.100_20250728_114801.json
│   └── 192.168.1.100_20250728_120000.json
├── 192.168.1.101/
│   ├── 192.168.1.101_20250728_114801.json
│   └── 192.168.1.101_20250728_120000.json
└── 192.168.1.102/
    └── 192.168.1.102_20250728_114801.json
```

**Example file path:** `/backups/192.168.1.100/192.168.1.100_20250728_114801.json`

## Error Handling

The backup process handles various error conditions:

- **HTTP Errors**: If the WLED device returns an error status (e.g., 404, 500)
- **Connection Errors**: If the device is unreachable or times out
- **File System Errors**: If the backup directory cannot be created or written to

All errors are logged and returned in the API response with appropriate error messages.

## Usage Examples

### Using curl

```bash
# Backup all instances
curl http://localhost:8000/config/backup/all

# Backup single instance
curl http://localhost:8000/config/backup/192.168.1.100

# Backup to custom directory
curl "http://localhost:8000/config/backup/all/custom?backup_dir=/home/user/wled_backups"
```

### Environment Setup

```bash
# Set the backup directory
export CONFIG_BACKUP_DIR="/home/user/wled_backups"

# Set the list of WLED devices
export WLED_IP_LIST="192.168.1.100,192.168.1.101,192.168.1.102"
```

## Integration with Existing Features

The config backup feature integrates seamlessly with the existing Wargos functionality:

- Uses the same WLED IP list as the metrics scraping
- Follows the same error handling patterns
- Integrates with the existing logging system
- Compatible with the existing FastAPI application structure
- **Prometheus Metrics**: Comprehensive metrics collection for monitoring backup operations

## Prometheus Metrics

The config backup feature provides detailed Prometheus metrics for monitoring:

### Operation Metrics

- `wargos_config_backup_operations_total`: Total number of backup operations (labeled by operation_type, device_ip, status)
- `wargos_config_backup_operation_duration_seconds`: Duration of backup operations (labeled by operation_type, device_ip)

### Error Metrics

- `wargos_config_backup_operation_exceptions_total`: Exceptions during backup operations (labeled by operation_type, device_ip, exception_type)
- `wargos_config_backup_http_errors_total`: HTTP errors during backup operations (labeled by device_ip, http_status_code)
- `wargos_config_backup_connection_errors_total`: Connection errors during backup operations (labeled by device_ip, error_type)

### File Metrics

- `wargos_config_backup_files_created_total`: Number of backup files created (labeled by device_ip)
- `wargos_config_backup_file_size_bytes`: Size of the most recent backup file in bytes (labeled by device_ip)

### Example Queries

```promql
# Successful backup operations
wargos_config_backup_operations_total{status="success"}

# Backup operation duration
histogram_quantile(0.95, rate(wargos_config_backup_operation_duration_seconds_bucket[5m]))

# HTTP errors by status code
wargos_config_backup_http_errors_total

# File creation rate
rate(wargos_config_backup_files_created_total[5m])
```

## Testing

The feature includes comprehensive tests covering:

- Default and custom backup directory configuration
- Successful backup operations
- HTTP error handling
- Connection error handling
- Bulk backup operations
- Missing IP list error handling

Run the tests with:

```bash
python -m pytest tests/test_config_backup.py -v
```
