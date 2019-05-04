# Endpoints

Get optimal antenna positions inside an area.

**URL** : `/get-positions`

**Method** : `GET`

## Query parameters

### Required

`bbox=x1,y1,x2,y2`

Coordinates defining the area (bounding box) in EPSG:3301 projection.

### Optional

`existing=x1,y1,type1,x2,y2,type2,...`

Predefined antenna positions.

## Success Response

```json
[
    {
        "x": 1.234,
        "y": 3.22,
        "type": "mm-wave"
    },
    {
        "x": -1.234,
        "y": 5,
        "type": "small-cell"
    }
]
```

`x` and `y` are coordinates in EPSG:3301 projection.
Type is one of `mm-wave` or `small-cell`.