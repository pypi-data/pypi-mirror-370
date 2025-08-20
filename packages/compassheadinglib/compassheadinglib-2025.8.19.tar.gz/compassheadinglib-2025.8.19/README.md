<span style="font-variant: small-caps">CompassHeadingLib</span> is a small, dependency-free, pure python library for working with compass headings in terms of comparison and transformation between decimal degree and natural language space. While it originally only suported English, it supports multiple languages.

<span style="font-variant: small-caps">CompassHeadingLib</span> follows the [worse is better](https://en.wikipedia.org/wiki/Worse_is_better) design philosophy; it's better to have a slower less featureful implementation then no implementation at all. Optimizations will be executed when we have to.

### License

<span style="font-variant: small-caps">CompassHeadingLib</span> is licensed under the MIT License and offered as is without warranty of any kind, express or implied. 

### Installation

#### From PyPi
`pip install -u compassheadinglib`

#### From Git
`pip install pip@git+https://github.com/Peter-E-Lenz/compassheadinglib/`

#### Usage

## Basic Usage

### Importing the Library

```python
# Import with default English language support
from compassheadinglib import Compass

# Or import with specific language support
from compassheadinglib.fr import Compass  # French
from compassheadinglib.de import Compass  # German
from compassheadinglib.es import Compass  # Spanish
```

### Creating a Compass Object

```python
compass = Compass()
```

## Finding Headings from Bearings

### Basic Heading Lookup

```python
# Find the closest heading for a given bearing (in decimal degrees)
heading = compass.findHeading(45.0)
print(heading.name)        # "Northeast"
print(heading.abbr)        # "NE" 
print(heading.azimuth)     # 45.0
print(heading.order)       # 2

# You can also call the compass object directly
heading = compass(45.0)    # Same as compass.findHeading(45.0)
```

### Specifying Heading Precision with Order

```python
bearing = 80.0

# Order 1: Cardinal directions only (N, E, S, W)
heading_order1 = compass.findHeading(bearing, order=1)
print(heading_order1.name)  # "East"

# Order 2: Half-winds (NE, SE, SW, NW)
heading_order2 = compass.findHeading(bearing, order=2)
print(heading_order2.name)  # "East"

# Order 3: Quarter-winds (default)
heading_order3 = compass.findHeading(bearing, order=3)
print(heading_order3.name)  # "East-Northeast"

# Order 4: Eighth-winds (most precise)
heading_order4 = compass.findHeading(bearing, order=4)
print(heading_order4.name)  # "East by North"
```

## Rotating Headings

### Basic Rotation with Wraparound

```python
# Start with a North heading
north = compass.findHeading(0.0)
print(north.name)  # "North"

# Rotate 45 degrees clockwise
northeast = north.rotate(45)
print(northeast.name)  # "Northeast"

# Rotate 90 degrees counter-clockwise
west = north.rotate(-90)
print(west.name)  # "West"

# Rotation automatically wraps around
north_by_west = north.rotate(-30)
print(north_by_west.name)      # "North by West"
print(north_by_west.azimuth)   # 330.0 (wraps from -30 to 330)

# Large rotations also wrap
east_northeast = north.rotate(405)  # 405° = 45° after wrapping
print(east_northeast.name)     # "Northeast"
```

### Using Nautical Terminology

```python
# Start with an East heading
east = compass.findHeading(90.0)

# Turn to starboard (right/clockwise)
southeast = east.starboard(45)
print(southeast.name)  # "Southeast"

# Turn to port (left/counter-clockwise)
northeast = east.port(45)
print(northeast.name)  # "Northeast"

# Wraparound examples
north = compass.findHeading(0.0)
northwest = north.port(45)      # 0° - 45° = 315° (wraps around)
print(northwest.name)           # "Northwest"

west = compass.findHeading(270.0)
northeast = west.starboard(135)  # 270° + 135° = 405° → 45° (wraps around)
print(northeast.name)           # "Northeast"
```

### Using Land-based Terminology

```python
# Same functionality with familiar left/right terms
east = compass.findHeading(90.0)

# Turn right (clockwise)
southeast = east.right(45)
print(southeast.name)  # "Southeast"

# Turn left (counter-clockwise)
northeast = east.left(45)
print(northeast.name)  # "Northeast"
```

## Arithmetic Operations

### Adding and Subtracting Headings

```python
compass = Compass()

# Create some headings
north = compass(0)      # 0°
east = compass(90)      # 90°
south = compass(180)    # 180°
west = compass(270)     # 270°

# Add headings (adds their azimuth values)
result1 = north + east  # 0° + 90° = 90°
print(result1.name)     # "East"

# Add degrees to headings
northeast = north + 45  # 0° + 45° = 45°
print(northeast.name)   # "Northeast"

# Reverse addition works too
northeast2 = 45 + north # Same as above
print(northeast2.name)  # "Northeast"

# Subtract headings
result2 = east - north  # 90° - 0° = 90°
print(result2.name)     # "East"

# Subtract degrees from headings
northwest = north - 45  # 0° - 45° = 315° (wraps around)
print(northwest.name)   # "Northwest"

# Reverse subtraction
result3 = 360 - east    # 360° - 90° = 270°
print(result3.name)     # "West"

# Wraparound examples
west_by_north = west + 45   # 270° + 45° = 315°
print(west_by_north.name)   # "Northwest"

south_by_east = south - 45  # 180° - 45° = 135°
print(south_by_east.name)   # "Southeast"
```

## Working with Multiple Languages

### Translating Headings

```python
# Start with English compass
from compassheadinglib import Compass
compass = Compass()

# Get a heading in English
north_en = compass.findHeading(0.0)
print(north_en.name)  # "North"

# Translate to other languages
north_fr = north_en.translate('FR')
print(north_fr.name)  # "Nord" (French)

north_de = north_en.translate('DE')  
print(north_de.name)  # "Nord" (German)

north_es = north_en.translate('ES')
print(north_es.name)  # "Norte" (Spanish)
```

### Using Language-Specific Compasses

```python
# Create compass objects for different languages
from compassheadinglib.fr import Compass as CompassFR
from compassheadinglib.de import Compass as CompassDE

compass_fr = CompassFR()
compass_de = CompassDE()

# Get headings directly in different languages
heading_fr = compass_fr.findHeading(45.0)
print(heading_fr.name)  # "Nord-Est" (French)

heading_de = compass_de.findHeading(45.0)
print(heading_de.name)  # "Nordost" (German)
```

## Practical Examples

### Navigation Planning with Arithmetic

```python
compass = Compass()

# Current heading
current_bearing = 75.5
current_heading = compass.findHeading(current_bearing)
print(f"Current heading: {current_heading.name} ({current_heading.azimuth}°)")

# Need to turn 30 degrees to starboard
new_heading = current_heading.starboard(30)
print(f"New heading: {new_heading.name} ({new_heading.azimuth}°)")

# Alternative using addition
new_heading_alt = current_heading + 30
print(f"Same result with addition: {new_heading_alt.name}")

# Calculate the course correction needed
correction = new_heading.azimuth - current_heading.azimuth
print(f"Turn {correction}° to starboard")
```

### Working with Heading Data

```python
compass = Compass()

# Get multiple headings
bearings = [0, 45, 90, 135, 180, 225, 270, 315]
headings = [compass.findHeading(b) for b in bearings]

# Convert to dictionary format for data processing
heading_data = [h.asDict() for h in headings]
print(heading_data)
# [{'name': 'North', 'abbr': 'N', 'azimuth': 0.0, 'order': 1}, ...]

# Compare headings
north = compass.findHeading(0)
east = compass.findHeading(90)

print(north < east)      # True (0° < 90°)
print(float(north))      # 0.0
print(str(north))        # "North"
```

### Course Plotting with Arithmetic Operations

```python
compass = Compass()

# Define a base course
base_course = compass(0)  # North
print(f"Base course: {base_course.name}")

# Apply course corrections using arithmetic
corrections = [15, -30, 45, -60]
current_course = base_course

print("Course corrections:")
for i, correction in enumerate(corrections):
    current_course = current_course + correction
    print(f"Leg {i+1}: {current_course.name} ({current_course.azimuth}°)")

# Calculate reciprocal bearings (opposite direction)
reciprocal = current_course + 180
print(f"Reciprocal bearing: {reciprocal.name} ({reciprocal.azimuth}°)")

# Calculate relative bearings
target_bearing = compass(120)  # East-Southeast
relative_bearing = target_bearing - current_course
print(f"Relative bearing to target: {relative_bearing.azimuth}°")
```

### Language support

To use a specific language import the library as import compassheadinglib.<language-two-letter-code>, i.e. to have Korean language support use `from
compassheadinglib.kr import Compass` or to use Portugese use `from
compassheadinglib.kr import Compass`. Because the library was originally available with only English language support `from compassheadinglib import Compass` is equivalent to `from  compassheadinglib.en import Compass`.

| Language | Two letter code |
| ---- | ------- |
| ar | Arabic |
| cn | Chinese |
| de | German |
| en | English |
| es | Spanish |
| fr | French |
| hi | Hindi |
| jp | Japanese |
| kr | Korean |
| pt | Portugese |

Unfortunately the developer of this library in an English monoglot. Translations were achieved via machine. The developer apologizes for any mistakes in those translations - corrections are graciously accepted.

## Example

### Dependencies

<span style="font-variant: small-caps">CompassHeadingLib</span> has only dependencies from the python's standard library.
It was originally written to run on Python 2.7 but is now only tested on Python 3.7+. 

## Compass Object
###### Compass(Float *heading*, Int *order* = 3)
###### Compass.findHeading(Float *heading*, Int *order* = 3)

| Type | Returns |
| ---- | ------- |
| Object(based on Dict)| Heading |

These functions take a heading between two points as a float (i.e. in decimal degrees) and returns the best matching heading with `order` degree of specificity. `Order` is a 1-indexed description of how specific the natural language The higher the order the more specific the heading. At an `order` of 1 the decimal degree heading of 80.0 will return a heading object of 'East' while at an `order` of 4 it would return 'East by North' heading object. 

Internally, calling the Compass object directly will silently call it's `findHeading` method.

## Heading Object
Heading objects are returned by Compass objects and are not intended to be created by end users.

| Type | Returns |
| ---- | ------- |
| Object| N/A|

Heading objects are containers for information about headings that are designed to be comparable to each other (and other python objects) using built-in methods. There are four pieces of information for each heading, each a method of the object: `name`, `abbr`, `azimuth`, and `order`. The various built-in comparisons look to different methods (and thus different pieces of the information) as appropriate. For the most part you can safely ignore all this background stuff.

###### Heading.name

| Type | Returns |
| ---- | ------- |
| string| string|

The full name of this heading, along the lines of 'North' or 'South by East'.
Note: despite what the festival has told you there is no such heading as 'South by Southwest'.

###### Heading.abbr

| Type | Returns |
| ---- | ------- |
| string| string|

The abbreviated name of this heading, along the lines of 'N' or 'SbE'

###### Heading.azimuth

| Type | Returns |
| ---- | ------- |
| float| float|

The decimal degree value of this heading. For example; 'West' is 270.0 while 'North-Northeast' is 22.5

###### Heading.order

| Type | Returns |
| ---- | ------- |
| integer| integer|

Order defines how specific the heading is. The cardinal directions ('North', 'East', 'South' & 'West') are of order 1 while 'South by East' is order 4. The Compass Headings Reference chart at the end of this document will be more illustrative of this difference.
Put another way: order 1 headings are 90° apart, order 2 headings are 45° apart, order 3 headings are 22.5° apart, and order 4 headings are 11.25° apart. By default this library uses order 3 where ever that value can be specified. Each order includes the headings of that order and all headings of any lower valued orders. Hence order 2 includes all headings labeled order 2 and order 1.

When treated as a string the Heading object returns the value for the `name` method
When treated as a numeric(regardless of int or float) it will return the values for the `azimuth` method.

### Arithmetic Operations

Heading objects support addition and subtraction operations that work with their azimuth values:

- **Adding headings**: `heading1 + heading2` adds their azimuth values
- **Adding degrees**: `heading + 45` or `45 + heading` adds degrees to the heading
- **Subtracting headings**: `heading1 - heading2` subtracts their azimuth values  
- **Subtracting degrees**: `heading - 30` subtracts degrees from the heading
- **Reverse subtraction**: `360 - heading` subtracts the heading's azimuth from a number

All arithmetic operations automatically wrap around to keep results within 0-360°.

Examples:
```python
north = compass(0)      # 0°
east = compass(90)      # 90°

northeast = north + east    # 0° + 90° = 90° (East)
southeast = east + 45       # 90° + 45° = 135° (Southeast)
northwest = north - 45      # 0° - 45° = 315° (Northwest, wraps around)
```

###### Heading.translate(String *lang*)

| Type | Returns |
| ---- | ------- |
| Heading| Heading object|

Returns a new Heading object with the name and abbreviation translated to the specified language. The language parameter should be the two-letter language code (e.g., 'EN', 'FR', 'DE'). The azimuth, order, and other properties remain unchanged. This method allows you to get the same compass heading in different languages while maintaining all the mathematical properties.

Example: `north_heading.translate('FR')` would return a Heading object with French names for the same compass direction.

###### Heading.rotate(Float *degrees*)

| Type | Returns |
| ---- | ------- |
| Heading| Heading object|

Rotates the current heading by the specified number of degrees and returns a new Heading object for the resulting direction. Positive degrees rotate clockwise, negative degrees rotate counter-clockwise. The resulting azimuth automatically wraps around to stay within 0-360°. This method calls the parent Compass object to find the appropriate heading for the new azimuth.

Example: `north_heading.rotate(45)` would return a Northeast heading. `north_heading.rotate(-30)` would return a heading at 330° (North-Northwest).

###### Heading.starboard(Float *degrees*)
###### Heading.right(Float *degrees*)

| Type | Returns |
| ---- | ------- |
| Heading| Heading object|

Rotates the current heading to starboard (right/clockwise) by the specified number of degrees. The degrees parameter must be non-negative (>= 0). The resulting azimuth automatically wraps around to stay within 0-360°. Returns a new Heading object for the resulting direction. `right()` is an alias for `starboard()` for those more familiar with land-based terminology.

Example: `north_heading.starboard(90)` would return an East heading. `west_heading.starboard(135)` would return a Northeast heading (270° + 135° = 405°, wraps to 45°).

###### Heading.port(Float *degrees*)
###### Heading.left(Float *degrees*)

| Type | Returns |
| ---- | ------- |
| Heading| Heading object|

Rotates the current heading to port (left/counter-clockwise) by the specified number of degrees. The degrees parameter must be non-negative (>= 0). The resulting azimuth automatically wraps around to stay within 0-360°. Returns a new Heading object for the resulting direction. `left()` is an alias for `port()` for those more familiar with land-based terminology.

Example: `east_heading.port(45)` would return a Northeast heading. `north_heading.port(30)` would return a heading at 330° (0° - 30°, wraps to 330°).

###### Heading.asDict()

| Type | Returns |
| ---- | ------- |
| dict| dictionary|

Returns a dictionary representation of the Heading object containing the core properties (name, abbr, azimuth, order) but excluding the langs and parent references. This is useful for serialization or when you need a simple data structure representation of the heading.

## English Language Compass Headings Reference
| Heading            | Abbreviation | Azimuth| Order |
|--------------------|-----------|---------|-------|
| North              | N         | 0       | 1     |
| North by East      | NbE       | 11.25   | 4     |
| North-Northeast    | NNE       | 22.5    | 3     |
| Northeast by North | NEbN      | 33.75   | 4     |
| Northeast          | NE        | 45      | 2     |
| Northeast by East  | NEbE      | 56.25   | 4     |
| East-Northeast     | ENE       | 67.5    | 3     |
| East by North      | EbN       | 78.75   | 4     |
| East               | E         | 90      | 1     |
| East by South      | EbS       | 101.25  | 4     |
| East-Southeast     | ESE       | 112.5   | 3     |
| Southeast by East  | SEbE      | 123.75  | 4     |
| Southeast          | SE        | 135     | 2     |
| Southeast by South | SEbS      | 146.25  | 4     |
| South-Southeast    | SSE       | 157.5   | 3     |
| South by East      | SbE       | 168.75  | 4     |
| South              | S         | 180     | 1     |
| South by West      | SbW       | 191.25  | 4     |
| South-Southwest    | SSW       | 202.5   | 3     |
| Southwest by South | SWbS      | 213.75  | 4     |
| Southwest          | SW        | 225     | 2     |
| Southwest by West  | SWbW      | 236.25  | 4     |
| West-Southwest     | WSW       | 247.5   | 3     |
| West by South      | WbS       | 258.75  | 4     |
| West               | W         | 270     | 1     |
| West by North      | WbN       | 281.25  | 4     |
| West-Northwest     | WNW       | 292.5   | 3     |
| Northwest by West  | NWbW      | 303.75  | 4     |
| Northwest          | NW        | 315     | 2     |
| Northwest by North | NWbN      | 326.25  | 4     |
| North-Northwest    | NNW       | 337.5   | 3     |
| North by West      | NbW       | 348.75  | 4     |