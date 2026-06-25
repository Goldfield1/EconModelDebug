
def update_natvis(model_state, file_path="Visualizers.natvis"):
    size = len(model_state)
    
    header = f'<?xml version="1.0" encoding="utf-8"?><AutoVisualizer xmlns="http://schemas.microsoft.com/vstudio/debugger/natvis/2010"><Type Name="sol_struct"><DisplayString>Solution (Size={size})</DisplayString><Expand>'
    
    items = ""
    
    for name, array in model_state:
        items += f'<Item Name="{name}">(double*){name}, [{len(array)}]</Item>'
        
    footer = '</Expand></Type></AutoVisualizer>'
    
    with open(file_path, "w") as f:
        f.write(header + items + footer)


def update_natvis_with_T(model_state, T, Nm, file_path="Visualizers.natvis"):
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