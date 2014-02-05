/*******************************************************************************
 *
 * Copyright 2012, Sinclair R.F., Inc.
 *
 * Top-level module to demonstrate I2C EEPROM write/read operation.
 *
 ******************************************************************************/

module sp601(
  // 200 MHz differential clock
  input  wire   ip_sysclk_p,
  input  wire   ip_sysclk_n,
  // I2C bus
  inout  wire   iop_i2c_scl,
  inout  wire   iop_i2c_sda,
  // UART Tx
  output wire   op_usb_1_rx
);

/*
 * Generate a 100 MHz clock from the 200 MHz oscillator.
 */

wire s_sysclk;
IBUFGDS sysclk_inst(
  .I    (ip_sysclk_p),
  .IB   (ip_sysclk_n),
  .O    (s_sysclk)
);

wire s_divclk;
BUFIO2 bufio2_inst(
  .I            (s_sysclk),
  .IOCLK        (),
  .DIVCLK       (s_divclk),
  .SERDESSTROBE ()
);
defparam bufio2_inst.DIVIDE             = 2;
defparam bufio2_inst.DIVIDE_BYPASS      = "FALSE";

wire s_clk;
BUFG sclk_inst(
  .I    (s_divclk),
  .O    (s_clk)
);

/*
 * Generate a synchronous reset.
 */

reg [3:0] s_reset_count = 4'hF;
always @ (posedge s_clk)
  s_reset_count <= s_reset_count - 4'd1;

reg s_rst = 1'b1;
always @ (posedge s_clk)
  if (s_reset_count == 4'd0)
    s_rst <= 1'b0;
  else
    s_rst <= s_rst;

/*
 * Instantiate the micro controller.
 */

i2c_eeprom ie_inst(
  // synchronous reset and processor clock
  .i_rst        (s_rst),
  .i_clk        (s_clk),
  // I2C bus
  .io_scl       (iop_i2c_scl),
  .io_sda       (iop_i2c_sda),
  // UART_Tx port
  .o_UART_Tx    (op_usb_1_rx)
);

endmodule
