module event_counter_async #(
	parameter WIDTH = 32
) (
	input wire rst_i,
	input wire event_i,
	input wire enable_i,
	input wire polarity_i,
	input wire [WIDTH-1:0] threshold_i,
	output reg [WIDTH-1:0] count_o,
	output reg trigger_o
);

wire event_int = polarity_i ? !event_i : event_i;

always @(posedge event_int or posedge rst_i) begin
	if (rst_i) begin
		count_o <= 0;
		trigger_o <= 0;
	end else begin
		if (enable_i) begin
			count_o <= count_o + 1;
			if (count_o >= (threshold_i - 1)) begin
				trigger_o <= 1;
			end
		end
	end
end

endmodule
