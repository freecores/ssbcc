# Copyright 2014, Sinclair R.F., Inc.

def storevector(ad):
  """
  Built-in macro to move multiple bytes from the data stack to memory.  The MSB
  (top of the data stack) is store at the specified memory location with
  subsequent bytes stored at subsequent memory locations.\n
  Usage:
    .storevector(variable,N)
  where
    variable    is the name of a variable
    N           is the constant number of bytes to transfer\n
  The effect is:  variable[0]=u_MSB, ..., variable[N-1]=u_LSB\n
  ( u_LSB ... u_MSB - )
  """

  def length(ad,argument):
    return int(argument[1]['value']) + 2;

  # Add the macro to the list of recognized macros.
  ad.AddMacro('.storevector', length, [
                                        ['','symbol'],
                                        ['','singlevalue','symbol'],
                                      ]);

  # Define the macro functionality.
  def emitFunction(ad,fp,argument):
    variableName = argument[0]['value'];
    (addr,ixBank,bankName) = ad.Emit_GetAddrAndBank(variableName);
    N = int(argument[1]['value']);
    ad.EmitPush(fp,addr,argument[0]['value']);
    for dummy in range(N):
      ad.EmitOpcode(fp,ad.specialInstructions['store+'] | ixBank,'store+ '+bankName);
    ad.EmitOpcode(fp,ad.InstructionOpcode('drop'),'drop -- .storevector(%s,%d)' % (variableName,N,) );
  ad.EmitFunction['.storevector'] = emitFunction;
