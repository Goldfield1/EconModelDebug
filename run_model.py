from BufferStockModel import BufferStockModelClass
from NatvisBuilder import update_natvis
import sys
# This forces every print statement to output immediately
sys.stdout.reconfigure(line_buffering=True)

model = BufferStockModelClass()
sol,par = model.sol, model.par

#update_natvis(sol.__dict__.items(),par.T, par.Nm)
update_natvis(sol.__dict__.items())

# crucial, adding debug flag to EconModel compiler
model.cpp_options = {'compiler':'vs', 'flags':'/LD /EHsc /Zi /Od /openmp'}
model.link_to_cpp(do_print=False)

model.cpp.solve(model.sol,model.par)