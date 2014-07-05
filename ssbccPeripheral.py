################################################################################
#
# Copyright 2012-2014, Sinclair R.F., Inc.
#
################################################################################

import re

from ssbccUtil import IsPosInt
from ssbccUtil import IsPowerOf2
from ssbccUtil import SSBCCException

class SSBCCperipheral:
  """Base class for peripherals"""

  def __init__(self,peripheralFile,config,param_list,loc):
    """
    Prototype constructor.
    peripheralFile      the full path name of the peripheral source
                        Note:  "__file__" doesn't work because 'execfile" and
                        "exec" are used to load the python script for the
                        peripheral.
    config              the ssbccConfig object for the processor core
    param_list          parameter list for the processor
    loc                 file name and line number for error messages
    """
    pass;

  def AddAttr(self,config,name,value,reformat,loc,optFn=None):
    """
    Add attribute to the peripheral:
    config      ssbccConfig object for the procedssor core
    name        attribute name
    value       possibly optional value for the attribute
    reformat    regular expression format for the attribute value
                Note:  reformat=None means the attribute can only be set to True
    loc         file name and line number for error messages
    optFn       optional function to set stored type
                Note:  See IntPow, RateMethod, etc. below for example methods.
    """
    if hasattr(self,name):
      raise SSBCCException('%s repeated at %s' % (name,loc,));
    if reformat == None:
      if value != None:
        raise SSBCCException('No parameter allowed for %s at %s' % (name,loc,));
      setattr(self,name,True);
    else:
      if value == None:
        raise SSBCCException('%s missing value at %s' % (name,loc,));
      if not re.match(reformat,value):
        raise SSBCCException('I/O symbol at %s does not match required format "%s":  "%s"' % (loc,reformat,value,));
      if optFn != None:
        try:
          value = optFn(value);
        except SSBCCException,msg:
          raise SSBCCException('Parameter "%s=%s" at %s:  %s' % (name,value,loc,str(msg),));
        except:
          raise SSBCCException('Value for "%s" not parsable at %s:  "%s"' % (name,loc,value,));
      setattr(self,name,value);

  def GenAssembly(self,config):
    """
    Virtual method to generate assembly modules associated with the peripheral.
    """
    pass;

  def GenHDL(self,fp,config):
    """
    Generate the peripheral HDL.
    fp          file pointer for the output processor
    config      ssbccConfig object for the procedssor core
    """
    if config.Get('hdl') == 'Verilog':
      self.GenVerilog(fp,config);
    elif config.Get('hdl') == 'VHDL':
      self.GenVHDL(fp,config);
    else:
      raise SSBCCException('HDL "%s" not implemented' % config.Get('hdl'));

  def GenVerilog(self,fp,config):
    """
    Virtual method to generate the Verilog version of the peripheral.
    Raise an exception if there is no Verilog version of the peripheral.
    """
    raise Exception('Verilog is not implemented for this peripheral');

  def GenVerilogFinal(self,config,body):
    """
    Clean up the peripheral code.
    Change "$clog2" to "clog2" for simulators and synthesis tools that don't
      recognize or process "$clog2."
    """
    if config.Get('define_clog2'):
      body = re.sub('\$clog2','clog2',body);
    return body;

  def GenVHDL(self,fp,config):
    """
    Virtual method to generate the VHDL version of the peripheral.
    Raise an exception if there is no VHDL version of the peripheral.
    """
    raise Exception('VHDL is not implemented for this peripheral');

  def IsIntExpr(self,value):
    """
    Test the string to see if it is a well-formatted integer or multiplication
    of two integers.
    Allow underscores as per Verilog.
    """
    if re.match(r'[1-9][0-9_]*',value):
      return True;
    elif re.match(r'\([1-9][0-9_]*(\*[1-9][0-9_]*)+\)',value):
      return True;
    else:
      return False;

  def IsParameter(self,config,name):
    """
    See if the provided symbol name is a parameter in the processor core.
    config      ssbccConfig object for the procedssor core
    name        symbol name
    """
    return config.IsParameter(name);

  def LoadCore(self,filename,extension):
    """
    Read the source HDL for the peripheral from the same directory as the python
    script.
    filename    name for the python peripheral (usually "__file__")
    extension   the string such as ".v" or ".vhd" required by the HDL\n
    Note:  The '.' must be included in the extension.  For example, the UART
           peripheral uses '_Rx.v' and '_Tx.v' or similar to invoke the UART_Tx
           and UART_Rx HDL files.
    """
    hdlName = re.sub(r'\.py$',extension,filename);
    fp = open(hdlName,'r');
    body = fp.read();
    fp.close();
    return body;

  def ParseIntExpr(self,value):
    """
    Convert a string containing well-formatted integer or multiplication of two
    integers.
    Allow underscores as per Verilog.
    Note:  If this routine is called, then the value should have already been
           verified to be a well-formatted integer string.
    """
    if not self.IsIntExpr(value):
      raise Exception('Program Bug -- shouldn\'t call with a badly formatted integer expression');
    return eval(re.sub('_','',value));

  ##############################################################################
  #
  # Methods to supplement python intrisics for the optFn argument of AddAttr
  #
  # Note:  AddAttr embelleshes exception messages with the symbol name and
  #        source code line number.
  #
  # Note:  One weird side effect of using lambda expressions is that the
  #        functions won't be recognized unless they're members of the
  #        SSBCCperipheral class.
  #
  ##############################################################################

  def FixedPow2(self,config,lowLimit,highLimit,value):
    """
    Check the provided constant as a power of 2 between the provided limits.\n
    Note:  This differs from InpPow2 in that localparams and constants are
           permitted.
    """
    if re.match(r'L_\w+$',value):
      if not config.IsParameter(value):
        raise SSBCCException('Unrecognized parameter');
      ix = [param[0] for param in config.parameters].index(value);
      value = config.parameters[ix][1];
    elif re.match(r'C_\w+$',value):
      if not config.IsConstant(value):
        raise SSBCCException('Unrecognized constant');
      value = config.constants[value];
    if not IsPosInt(value):
      raise SSBCCException('Must be a constant positive integer');
    value = self.ParseIntExpr(value);
    if not IsPowerOf2(value):
      raise SSBCCException('Must be a power of 2');
    if not (lowLimit <= value <= highLimit):
      raise SSBCCException('Must be between %d and %d inclusive' % (lowLimit,highLimit,));
    return value;

  def IntPow2(self,value,minValue=1):
    """
    Return the integer value of the argument if it is a power of 2.  Otherwise
    throw an error.
    """
    if not IsPosInt(value):
      raise SSBCCException('Not a positive integer');
    value = self.ParseIntExpr(value);
    if not IsPowerOf2(value):
      raise SSBCCException('Not a power of 2');
    if value < minValue:
      raise SSBCCException('Must be at least %d' % minValue);
    return value;

  def PosInt(self,value,maxValue=0):
    """
    Return the integer value of the argument unless it is out of bounds.\n
    Note:  maxValue=0 means that there is no upper limit.
    """
    if not IsPosInt(value):
      raise SSBCCException('Not a positive integer');
    value = self.ParseIntExpr(value);
    if (maxValue != 0) and (value > maxValue):
      raise SSBCCException('Out of bounds -- can be at most %d' % maxValue);
    return value;

  def RateMethod(self,config,value):
    """
    Return the string to evaluate the provided value or ratio of two values.
    The value can be an integer (including underscores) or a parameter.  Ratios
    are restated to do rounding instead of truncation.\n
    Examples:
      123456
      123_456
      L_DIVISION_RATIO
      G_CLOCK_FREQUENCY_HZ/19200
      G_CLOCK_FREQUENCY_HZ/L_BAUD_RATE
      100_000_000/G_BAUD_RATE
    """
    if value.find('/') < 0:
      if self.IsIntExpr(value):
        return str(self.ParseIntExpr(value));
      elif self.IsParameter(config,value):
        return value;
      else:
        raise SSBCCException('Value must be a positive integer or a previously declared parameter');
    else:
      ratearg = re.findall('([^/]+)',value);
      if len(ratearg) != 2:
        raise SSBCCException('Only one "/" allowed in expression');
      if not self.IsIntExpr(ratearg[0]) and not self.IsParameter(config,ratearg[0]):
        raise SSBCCException('Numerator must be an integer or a previously declared parameter');
      if not self.IsIntExpr(ratearg[1]) and not self.IsParameter(config,ratearg[1]):
        raise SSBCCException('Denominator must be an integer or a previously declared parameter');
      return '(%s+%s/2)/%s' % (ratearg[0],ratearg[1],ratearg[1],);
