# smart_device_rest
Rest API for broadlink, etc

# Install

* TBD

# Endpoints

## Discover broadlink RM mini

Discover broadlink devices.

TODO: we do not need ID.

### URL

```
GET /broadlink/discover
```

### Example

#### Responce

Code : 200

Content : 

```
[
    {
        "type": "0x2712",
        "host": "192.168.100.111",
        "mac": "bac37634abcd"
    },
    {
        "type": "0x2712",
        "host": "192.168.100.101",
        "mac": "bac376341234"
    }
]
```

## Register broadlink RM mini

Register base device (broadlink rm mini) to API server.
If API server accepts request, base device will be identifyed by *id*. 

If requested device is already registered in API server (has same mac address), API server do not create new *id* and just update registered information.

### URL

```
POST /broadlink/base_devices
```

### Data params

|  name  | type | description|
| --------- | ------ |----------------|
|  type  |  string  | Broadlink device type.  Only rm mini (0x2712) will be accepted|
|  host  |  string  | IP address of device. |
|  mac  |  string  | mac address of device |


### Example

```
{
    "type": "0x2712",
    "host": "192.168.100.100",
    "mac": "1234abcd5678"
}
```

#### Responce

Code : 201

Location: ``` http://localhost/broadlink/base_devices/1 ```

## Get base device infomation

### URL

```
GET /broadlink/base_devices
GET /broadlink/base_devices/:id
```

### Example


#### Responce

Code : 200

```
{
    "id": 1,
    "type": "0x2712",
    "host": "192.168.100.100",
    "mac": "1234abcd5678"
}
```

## Learn IR code

### URL

```
POST /broadlink/base_devices/:id/learn
```

### Data params

|  name  | type | description|
| --------- | ------ |----------------|
|  device  |  string  | device name|
|  action  |  string  | action of device |

### Example

```
{
    "device": "tv",
    "action": "on"
}
```

#### Responce

Code : 201

Location: ``` http://localhost/commands/1 ```



## Run command

### URL

```
PUT /commands/:id/run
```

#### Responce

Code : 200


## Get command

### URL

```
GET /commands
GET /commands/:id
```

### Example

#### Responce

Code : 200

```
[
    {
        "id": 1,
        "device": "tv",
        "action": "off",
        "type": "broadlink",
        "param": {
            "ir_code": "260050000001269213121312131213121312131213361312133613361336133613361336141113361411143514111411133614111312131213361312133614351411143514351435140005140001274814000d050000000000000000",
            }
        }
    },
    {
        "id": 2,
        "device": "plug",
        "action": "on",
        "type": "ifttt_webhook",
        "param": {
            "event": "event",
            "values" : {
                "value1": "v1",
                "value2": "foo",
                "value3": "bar"
            }
        }
    }
]
```
