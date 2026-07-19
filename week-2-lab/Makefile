# Optional local simulation helper.
# Requires Icarus Verilog (iverilog and vvp).

SIM_DIR := sim/build
SIM_EXE := $(SIM_DIR)/tb_week2_counter.out

.PHONY: test clean

test: $(SIM_EXE)
	vvp $(SIM_EXE)

$(SIM_EXE): src/week2_counter.v sim/tb_week2_counter.v
	mkdir -p $(SIM_DIR)
	iverilog -g2012 -o $@ $^

clean:
	rm -rf $(SIM_DIR)
