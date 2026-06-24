import shutil
import numpy as np
import numba as nb

from EconModel import EconModelClass, jit

from EconModel import cpptools

from BufferStockModel import BufferStockModelClass

import sys
# This forces every print statement to output immediately
sys.stdout.reconfigure(line_buffering=True)



def update_natvis(model_state, file_path="Visualizers.natvis"):
    size = len(model_state)
    
    header = f'<?xml version="1.0" encoding="utf-8"?><AutoVisualizer xmlns="http://schemas.microsoft.com/vstudio/debugger/natvis/2010"><Type Name="sol_struct"><DisplayString>Solution (Size={size})</DisplayString><Expand>'
    
    items = ""
    
    for name, array in model_state:
        print( len(array) , array)
        items += f'<Item Name="{name}">(double*){name}, [{len(array)}]</Item>'
        
    footer = '</Expand></Type></AutoVisualizer>'
    
    with open(file_path, "w") as f:
        f.write(header + items + footer)


def update_natvis(model_state, T, Nm, file_path="Visualizers.natvis"):
    # The header defines the structure
    header = (
        '<?xml version="1.0" encoding="utf-8"?>'
        '<AutoVisualizer xmlns="http://schemas.microsoft.com/vstudio/debugger/natvis/2010">'
        '<Type Name="sol_struct">'
        '<DisplayString>Solution (T={T}, Nm={Nm})</DisplayString>'
        '<Expand>'
    )
    
    # We create a Synthetic node for each array (c and V)
    items = ""
    for name, _ in model_state:
        items += f'''
        <Synthetic Name="{name} (Time Slices)">
            <Expand>
                <IndexListItems>
                    <Size>{T}</Size>
                    <ValueNode>({name}) + ($i * {Nm}), [{Nm}]</ValueNode>
                </IndexListItems>
            </Expand>
        </Synthetic>'''
        
    footer = '</Expand></Type></AutoVisualizer>'
    
    with open(file_path, "w") as f:
        f.write(header.format(T=T, Nm=Nm) + items + footer)

model = BufferStockModelClass()
sol,par = model.sol, model.par

update_natvis(sol.__dict__.items(),par.T, par.Nm)

try:
    model.cpp_options = {'compiler':'vs', 'flags':'/LD /EHsc /Zi /Od /openmp'}
    model.link_to_cpp(do_print=False)
except:
    exit()
    pass

model.cpp.solve(model.sol,model.par)