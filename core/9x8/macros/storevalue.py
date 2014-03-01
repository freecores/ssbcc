# Copyright 2014, Sinclair R.F., Inc.

def storevalue(ad):
  """
  Built-in macro to store the top of the data stack in the specified
  variable.\n
    <v> .storevalue(variable[,op])
  where:
    <v>         is the value to be stored from the next-to-top of the data
                stack
    variable    is the name of the variable
    op          is an optional instruction to override the default "drop"
                instruction at the end of the instruction sequence\n
  The effect is:  variable = v\n
  ( u_value - )
  """

  # Add the macro to the list of recognized macros.
  ad.AddMacro('.storevalue', 3, [
                                  ['','symbol'],
                                  ['drop','instruction','singlemacro','singlevalue','symbol']
                                ]);

  # Define the macro functionality.
  def emitFunction(ad,fp,argument):
    name = argument[0]['value'];
    (addr,ixBank,bankName) = ad.Emit_GetAddrAndBank(name);
    ad.EmitPush(fp,addr,ad.Emit_String(name),argument[0]['loc']);
    ad.EmitOpcode(fp,ad.specialInstructions['store'] | ixBank,'store '+bankName);
    ad.EmitOptArg(fp,argument[1]);
  ad.EmitFunction['.storevalue'] = emitFunction;
