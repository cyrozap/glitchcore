`timescale 1 ns/10 ps  // time-unit = 1 ns, precision = 10 ps

module glitchcore_wb_tb;

	reg event_in, rst, clk, wb_we_i, wb_sel_i, wb_stb_i, wb_cyc_i;
	wire glitch_out, wb_ack_o;
	reg [31:0] wb_adr_i;
	reg [31:0] wb_dat_i;
	wire [31:0] wb_dat_o;

	localparam period = 20;

	glitchcore_wb DUT (.clk(clk), .rst(rst), .event_in(event_in), .glitch_out(glitch_out), .wb_adr_i(wb_adr_i), .wb_dat_i(wb_dat_i), .wb_dat_o(wb_dat_o), .wb_we_i(wb_we_i), .wb_sel_i(wb_sel_i), .wb_stb_i(wb_stb_i), .wb_ack_o(wb_ack_o), .wb_cyc_i(wb_cyc_i));

	always
	begin
		clk = 1'b1;
		#10;

		clk = 1'b0;
		#10;
	end

	always @(posedge clk) begin
		$dumpfile("glitchcore_wb_tb.vcd");
		$dumpvars();

		event_in = 0;
		wb_we_i = 0;
		wb_sel_i = 0;
		wb_stb_i = 0;
		wb_cyc_i = 0;
		wb_adr_i = 0;
		wb_dat_i = 0;

		rst = 1;
		#period;
		rst = 0;
		#period;

		wb_adr_i = 32'h14;
		wb_dat_i = 32'h08;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h24;
		wb_dat_i = 32'h10;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h34;
		wb_dat_i = 32'h02;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h30;
		wb_dat_i = 32'h01;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h20;
		wb_dat_i = 32'h01;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h10;
		wb_dat_i = 32'h01;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		#(period * 4);

		event_in = 1;
		#period;
		event_in = 0;
		#period;
		event_in = 1;
		#period;
		event_in = 0;
		#period;
		event_in = 1;
		#period;
		event_in = 0;
		#period;
		event_in = 1;
		#period;
		event_in = 0;
		#period;
		event_in = 1;
		#period;
		event_in = 0;
		#period;
		event_in = 1;
		#period;
		event_in = 0;
		#period;
		event_in = 1;
		#period;
		event_in = 0;
		#period;
		event_in = 1;
		#period;
		event_in = 0;
		#period;

		#(period * 30);

		wb_adr_i = 32'h10;
		wb_dat_i = 32'h00;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h20;
		wb_dat_i = 32'h00;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h30;
		wb_dat_i = 32'h00;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h14;
		wb_dat_i = 32'h02;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h24;
		wb_dat_i = 32'h18;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h34;
		wb_dat_i = 32'h20;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h30;
		wb_dat_i = 32'h01;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h20;
		wb_dat_i = 32'h01;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		wb_adr_i = 32'h10;
		wb_dat_i = 32'h01;
		wb_stb_i = 1;
		wb_we_i = 1;
		#period;
		wb_we_i = 0;
		wb_stb_i = 0;
		#period;

		#(period * 4);

		event_in = 1;
		#period;
		event_in = 0;
		#period;
		event_in = 1;
		#period;
		event_in = 0;
		#period;

		#(period * 100);

		$finish;
	end
endmodule
