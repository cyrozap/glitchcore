all: glitchcore_uart.bin

%.v: %.py
	python3 $<

glitchcore_wb_tb.vvp: glitchcore_wb_tb.v glitchcore_wb.v event_counter_async.v
	iverilog -o $@ $^

glitchcore_wb_tb.vcd: glitchcore_wb_tb.vvp
	./$<

%.json: %.v event_counter_async.v
	yosys -p 'read_verilog $^; synth_ice40; write_json $@'

%.asc: %.json %.pcf
	nextpnr-ice40 \
		--hx1k --package tq144 \
		--asc $@ \
		--json $< \
		--pcf glitchcore_uart.pcf \
		--log glitchcore_uart.rpt

%.bin: %.asc
	icepack $< $@

flash: glitchcore_uart.bin
	iceprog $<

sim: glitchcore_wb_tb.vcd
	gtkwave $<

clean:
	rm -f *.asc *.bin *.json *.vcd delay.v event_counter_sync.v glitchcore.v glitchcore_wb.v glitchcore_uart.v pulse.v glitchcore_wb_tb.vvp


.PHONY: all clean flash sim
