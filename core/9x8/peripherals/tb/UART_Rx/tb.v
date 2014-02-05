/*******************************************************************************
 *
 * Copyright 2013, Sinclair R.F., Inc.
 *
 * Test bench for the UART_Rx peripheral.
 *
 ******************************************************************************/

`timescale 1ns/1ps

module tb;

// 100 MHz clock
reg s_clk = 1'b1;
always @ (s_clk)
  s_clk <= #5 ~s_clk;

reg s_rst = 1'b1;
initial begin
  repeat (5) @ (posedge s_clk);
  s_rst = 1'b0;
end

// 115200 baud, 1 stop bit
reg [15*10:0] s_buf1 = {
                      // list last byte first
                      1'b1, 8'h00, 1'b0, // null character (also terminates program)
                      1'b1, 8'h0A, 1'b0, // LF
                      1'b1, 8'h0D, 1'b0, // CR
                      1'b1, 8'h12, 1'b0, // '!'
                      1'b1, 8'h63, 1'b0, // 'd'
                      1'b1, 8'h6C, 1'b0, // 'l'
                      1'b1, 8'h72, 1'b0, // 'r'
                      1'b1, 8'h6F, 1'b0, // 'o'
                      1'b1, 8'h57, 1'b0, // 'W'
                      1'b1, 8'h20, 1'b0, // ' '
                      1'b1, 8'h6F, 1'b0, // 'o'
                      1'b1, 8'h6C, 1'b0, // 'l'
                      1'b1, 8'h6C, 1'b0, // 'l'
                      1'b1, 8'h65, 1'b0, // 'e'
                      1'b1, 8'h48, 1'b0, // 'H'
                      1'b1
                    };
wire s_uart = s_buf1[0];
initial begin
  @ (negedge s_rst);
  #100;
  forever begin
    #8680.555;
    s_buf1 <= { 1'b1, s_buf1[1+:15*10] };
  end
end

wire [7:0] s_data;
wire       s_data_wr;
wire       s_done;
tb_UART_Rx uut(
  // synchronous reset and processor clock
  .i_rst        (s_rst),
  .i_clk        (s_clk),
  .i_uart       (s_uart),
  .o_data       (s_data),
  .o_data_wr    (s_data_wr),
  .o_done       (s_done)
);

always @ (posedge s_clk)
  if (s_data_wr)
    $display("%h", s_data);

always @ (posedge s_clk)
  if (s_done)
    $finish;

endmodule
