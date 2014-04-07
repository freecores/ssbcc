################################################################################
#
# Copyright 2014, Sinclair R.F., Inc.
#
################################################################################

import re

def WriteTclScript(mode,basePortName,addrWidth,noWSTRB=False):
  """
  Write a TCL script to facilitate generating IP for micro controller
  configurations with AXI4-List master or slave busses.\n
  Usage:
    This method should be called by the python scripts creating AXI4-Lite
    peripherals as follows:\n
    import vivado_AXI4_Lite_Bus
    vivado_AXI4_Lite_Bus.WriteTclScript(mode,basePortName);\n
  where:
    mode        is either 'master' or 'slave'
    basePortName
                is the string used for the basePortName by the peripheral
  """

  #
  # Validate the arguments.
  #

  if mode not in ('master','slave',):
    raise Exception('Program Bug:  Mode "%s" should be either "master" or "slave"' % mode);

  if type(basePortName) != str:
    raise Exception('Program Bug:  basePortName must be an "str", not a "%s"', type(basePortName));

  #
  # Write the TCL script.
  #

  body = """# Auto-generated TCL script to configure the @MODE@ AXI4-Lite port "@BASEPORTNAME@"
# Usage:  source vivado_@BASEPORTNAME@.tcl

# Remove the AXI port maps auto-generated by Vivado 2013.3.
ipx::remove_address_space {i_@BASEPORTNAME@} [ipx::current_core]
ipx::remove_address_space {o_@BASEPORTNAME@} [ipx::current_core]
ipx::remove_bus_interface {i_@BASEPORTNAME@} [ipx::current_core]
ipx::remove_bus_interface {o_@BASEPORTNAME@} [ipx::current_core]
ipx::remove_bus_interface {i_@BASEPORTNAME@_signal_reset} [ipx::current_core]
ipx::remove_bus_interface {i_@BASEPORTNAME@_signal_clock} [ipx::current_core]
ipx::remove_memory_map {i_@BASEPORTNAME@} [ipx::current_core]
ipx::remove_memory_map {o_@BASEPORTNAME@} [ipx::current_core]

# Create the AXI4-Lite port.
ipx::add_bus_interface {@BASEPORTNAME@} [ipx::current_core]
set_property abstraction_type_vlnv {xilinx.com:interface:aximm_rtl:1.0} [ipx::get_bus_interface @BASEPORTNAME@ [ipx::current_core]]
set_property bus_type_vlnv {xilinx.com:interface:aximm:1.0} [ipx::get_bus_interface @BASEPORTNAME@ [ipx::current_core]]
set_property interface_mode {@MODE@} [ipx::get_bus_interface @BASEPORTNAME@ [ipx::current_core]]
set_property display_name {@BASEPORTNAME@} [ipx::get_bus_interface @BASEPORTNAME@ [ipx::current_core]]
set_property description {AXI4-Lite bus for @BASEPORTNAME@} [ipx::get_bus_interface @BASEPORTNAME@ [ipx::current_core]]

# Add the signals to the AXI4-Lite port
""";

  # mode-dependent directions for signals
  mo = 'o' if mode == 'master' else 'i';
  mi = 'i' if mode == 'master' else 'o';

  for pairs in [
    ('ARADDR',  'araddr',       mo,     ),
    ('ARREADY', 'arready',      mi,     ),
    ('ARVALID', 'arvalid',      mo,     ),
    ('AWADDR',  'awaddr',       mo,     ),
    ('AWREADY', 'awready',      mi,     ),
    ('AWVALID', 'awvalid',      mo,     ),
    ('BREADY',  'bready',       mo,     ),
    ('BRESP',   'bresp',        mi,     ),
    ('BVALID',  'bvalid',       mi,     ),
    ('RDATA',   'rdata',        mi,     ),
    ('RREADY',  'rready',       mo,     ),
    ('RRESP',   'rresp',        mi,     ),
    ('RVALID',  'rvalid',       mi,     ),
    ('WDATA',   'wdata',        mo,     ),
    ('WREADY',  'wready',       mi,     ),
    ('WSTRB',   'wstrb',        mo,     ) if not noWSTRB else None,
    ('WVALID',  'wvalid',       mo,     ),
  ]:
    if not pairs:
      continue;
    body += "ipx::add_port_map {%s} [ipx::get_bus_interface @BASEPORTNAME@ [ipx::current_core]]\n" % pairs[0];
    body += "set_property physical_name {%s_@BASEPORTNAME@_%s} [ipx::get_port_map %s [ipx::get_bus_interface @BASEPORTNAME@ [ipx::current_core]]]\n" % (pairs[2],pairs[1],pairs[0],);

  body += """
# Fix the address space
ipx::add_address_space {@BASEPORTNAME@} [ipx::current_core]
""";
  if mode == 'master':
    body += """set_property master_address_space_ref {@BASEPORTNAME@} [ipx::get_bus_interface @BASEPORTNAME@ [ipx::current_core]]
set_property range {@ADDR_WIDTH@} [ipx::get_address_space @BASEPORTNAME@ [ipx::current_core]]
set_property width {32} [ipx::get_address_space @BASEPORTNAME@ [ipx::current_core]]
""";
  else:
    body += "ipx::remove_address_space {@BASEPORTNAME@} [ipx::current_core]\n";

  body += """
# Fix the reset port definition
ipx::add_bus_interface {@BASEPORTNAME@_aresetn} [ipx::current_core]
set_property abstraction_type_vlnv {xilinx.com:signal:reset_rtl:1.0} [ipx::get_bus_interface @BASEPORTNAME@_aresetn [ipx::current_core]]
set_property bus_type_vlnv {xilinx.com:signal:reset:1.0} [ipx::get_bus_interface @BASEPORTNAME@_aresetn [ipx::current_core]]
set_property display_name {@BASEPORTNAME@_aresetn} [ipx::get_bus_interface @BASEPORTNAME@_aresetn [ipx::current_core]]
ipx::add_port_map {RST} [ipx::get_bus_interface @BASEPORTNAME@_aresetn [ipx::current_core]]
set_property physical_name {i_@BASEPORTNAME@_aresetn} [ipx::get_port_map RST [ipx::get_bus_interface @BASEPORTNAME@_aresetn [ipx::current_core]]]
ipx::add_bus_parameter {POLARITY} [ipx::get_bus_interface @BASEPORTNAME@_aresetn [ipx::current_core]]
set_property value {ACTIVE_LOW} [ipx::get_bus_parameter POLARITY [ipx::get_bus_interface @BASEPORTNAME@_aresetn [ipx::current_core]]]
""";

  body += """
# Fix the clock port definition
ipx::add_bus_interface {@BASEPORTNAME@_aclk} [ipx::current_core]
set_property abstraction_type_vlnv {xilinx.com:signal:clock_rtl:1.0} [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]
set_property bus_type_vlnv {xilinx.com:signal:clock:1.0} [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]
set_property display_name {@BASEPORTNAME@_aclk} [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]
ipx::add_port_map {CLK} [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]
set_property physical_name {i_@BASEPORTNAME@_aclk} [ipx::get_port_map CLK [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]]
ipx::add_bus_parameter {ASSOCIATED_BUSIF} [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]
set_property value {@BASEPORTNAME@} [ipx::get_bus_parameter ASSOCIATED_BUSIF [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]]
ipx::add_bus_parameter {ASSOCIATED_RESET} [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]
set_property value {i_@BASEPORTNAME@_aresetn} [ipx::get_bus_parameter ASSOCIATED_RESET [ipx::get_bus_interface @BASEPORTNAME@_aclk [ipx::current_core]]]
""";

  addrWidth = max(addrWidth,12);
  for subpair in [
    ('@ADDR_WIDTH@',    str(2**addrWidth),      ),
    ('@BASEPORTNAME@',  basePortName,           ),
    ('@MODE@',          mode,                   ),
  ]:
    body = re.sub(subpair[0],subpair[1],body);

  fp = open('vivado_%s.tcl' % basePortName, 'wt');
  fp.write(body);
  fp.close();
