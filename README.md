# glitchcore

An FPGA core for glitching circuits, written with Amaranth HDL.


## Introduction

Note: This introduction assumes you already know what "voltage
glitching"/"voltage fault injection" is.

glitchcore is a system designed to facilitate glitching by counting a
configurable number of "events" (changes in voltage from high to low or low to
high), waiting for a configurable period of time, and then transmitting a
voltage pulse with a configurable width. Each parameter is configurable at
run-time, either directly via the signals in each module or via a
[Wishbone interface][wishbone]. A simplified and slightly outdated schematic of
glitchcore can be seen below:

[![glitchcore schematic diagram][schematic]][schematic]


[wishbone]: https://en.wikipedia.org/wiki/Wishbone_(computer_bus)
[schematic]: doc/schematic.svg
