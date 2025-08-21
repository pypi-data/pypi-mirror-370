# rtcvis

rtcvis is an educational tool that can create interactive visualizations for convolution operations in the min-plus algebra, such as needed for real time calculus (RTC). RTC is a method for performance analysis of real time systems. Note that rtcvis cannot be used for performance analysis however, since it only supports finite curves - for this purpose, you can use the [RTC toolbox from ETH Zurich](https://www.mpa.ethz.ch/). Please note that I'm in no way affiliated with and that this project is in no way endorsed by ETH Zurich.

## Installation

```shell
pip install rtcvis\[plot\]
```

## Usage

```python
from rtcvis import plot_conv

plot_conv()
```

### Curve Syntax

Curves can be specified using a syntax similar to the one from [RTC toolbox](https://www.mpa.ethz.ch/):

```python
[(x, y, m), ...], l
```

- The first argument is a list of points: `x` and `y` are the coordinates of this points and `m` is the slope of the line section starting at this point
- `l` is the length of the curve, or, in other words, the x coordinate at which the curve ends

Note that Curves are allowed to have discontinuities


## Development

```shell
pip install -e .\[dev,plot\]
pre-commit install
```
