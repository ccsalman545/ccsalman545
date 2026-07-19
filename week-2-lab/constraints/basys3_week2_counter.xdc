## Week 2 Digital Design Lab
## Target board: Digilent Basys 3, XC7A35T-1CPG236C
## Top-level module: week2_counter
##
## Inputs
##   clk     : 100 MHz oscillator
##   reset   : centre pushbutton, active-high synchronous reset
##   enable  : SW0, high enables counting
##   up_down : SW1, high increments and low decrements
##
## Output
##   count[3:0] : LED0..LED3, least-significant bit first

## 100 MHz clock
set_property PACKAGE_PIN W5 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
create_clock -add -name sys_clk_pin -period 10.000 -waveform {0 5} [get_ports clk]

## Centre pushbutton: synchronous active-high reset
set_property PACKAGE_PIN U18 [get_ports reset]
set_property IOSTANDARD LVCMOS33 [get_ports reset]

## Slide switches
set_property PACKAGE_PIN V17 [get_ports enable]
set_property IOSTANDARD LVCMOS33 [get_ports enable]

set_property PACKAGE_PIN V16 [get_ports up_down]
set_property IOSTANDARD LVCMOS33 [get_ports up_down]

## Four user LEDs: count[0] is the least-significant bit
set_property PACKAGE_PIN U16 [get_ports {count[0]}]
set_property IOSTANDARD LVCMOS33 [get_ports {count[0]}]

set_property PACKAGE_PIN E19 [get_ports {count[1]}]
set_property IOSTANDARD LVCMOS33 [get_ports {count[1]}]

set_property PACKAGE_PIN U19 [get_ports {count[2]}]
set_property IOSTANDARD LVCMOS33 [get_ports {count[2]}]

set_property PACKAGE_PIN V19 [get_ports {count[3]}]
set_property IOSTANDARD LVCMOS33 [get_ports {count[3]}]
