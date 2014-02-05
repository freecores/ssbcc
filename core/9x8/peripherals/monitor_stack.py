################################################################################
#
# Copyright 2012-2013, Sinclair R.F., Inc.
#
################################################################################

import math
import re

from ssbccPeripheral import SSBCCperipheral
from ssbccUtil import SSBCCException;

class monitor_stack(SSBCCperipheral):
  """
  Simulation-specific peripheral to flag invalid stack operations and display
  the execution history immediately before the invalid operation.\n
  Invalid data stack operations are:
    pushing onto a full data stack
    dropping from an empty data stack
    nipping from an almost empty data stack\n
  Invalid return stack operations are:
    pushing onto a full return stack
    dropping values from an empty return stack
    returns from a data entry on the return stack
    non-return  operations from an address entry on the return stack\n
  Invalid data operations are:
    swap on an empty or almost empty data stack
    in-place operations on an empty or almost empty data stack\n
  Usage:
    PERIPHERAL monitor_stack \\
               [history==n]\n
  Where:
    history=n
      display the n most recent operations when a stack error is encountered
      Note:  Normally the last 50 instructions are displayed.
  """

  def __init__(self,peripheralFile,config,param_list,loc):
    # Use the externally provided file name for the peripheral
    self.peripheralFile = peripheralFile;
    # Get the parameters.
    for param in param_list:
      param_name = param_list[0];
      param_arg = param_list[1:];
      if param_name == 'history':
        self.AddAttr(config,param,param_arg,r'[1-9]\d*$',loc,int);
      else:
        raise SSBCCException('Unrecognized parameter at %s: %s' % (loc,param,));
    # Set optional parameters.
    if not hasattr(self,'history'):
      self.history = 50;
    # Configure the system for this peripheral.
    config.functions['display_trace'] = True;

  def GenVerilog(self,fp,config):
    body = self.LoadCore(self.peripheralFile,'.v');
    outport_pure_strobe = '';
    for ix in range(config.NOutports()):
      thisPort = config.outports[ix][2:];
      thisIsStrobe = True;
      for jx in range(len(thisPort)):
        signal = thisPort[jx];
        signalType = signal[2];
        if signalType == 'data':
          thisIsStrobe = False;
        elif signalType == 'strobe':
          pass;
        else:
          raise Exception('Program Bug:  Unrecognized outport signal type "%s"' % signalType);
      if thisIsStrobe:
        if len(outport_pure_strobe) > 0:
          outport_pure_strobe += ' || ';
        outport_pure_strobe += ('(s_T == 8\'h%02X)' % ix);
    if len(outport_pure_strobe) == 0:
      outport_pure_strobe = '1\'b0';
    outport_pure_strobe = 'wire s__outport_pure_strobe = ' + outport_pure_strobe + ';';
    for subs in (
                  (r'\\bix__',                  'ix__monitor_stack__',),
                  (r'\\bs__',                   's__monitor_stack__',),
                  (r'@CORENAME@',               config.Get('outCoreName'),),
                  (r'@HISTORY@',                str(self.history),),
                  (r'@LAST_INPORT@',            '9\'h%03X' % config.NInports(),),
                  (r'@LAST_OUTPORT@',           '9\'h%03X' % config.NOutports(),),
                  (r'@NINSTRUCTIONS@',          str(config.Get('nInstructions')['length']),),
                  (r'@OUTPORT_PURE_STROBE@',    outport_pure_strobe,),
                ):
      body = re.sub(subs[0],subs[1],body);
    for ixBank in range(4):
      memParam = config.GetMemoryByBank(ixBank);
      if memParam:
        maxLength = memParam['maxLength'];
      else:
        maxLength = 0;
      body = re.sub('@MEM_LIMIT_%d@' % ixBank, str(maxLength), body);
    fp.write(body);
