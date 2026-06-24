////////////////
// 1. generic //
////////////////

#include <windows.h>
#include <cmath>
#include <stdio.h>
#include <omp.h>

#include <algorithm>

#include "nlopt-2.4.2-dll64\nlopt.h"

///////////////
// 2. custom //
///////////////

#define EXPORT extern "C" __declspec(dllexport)

////////////////
// 3. structs //
////////////////

#include "par_struct.cpp"
#include "sol_struct.cpp"
#include "sim_struct.cpp"

////////////////
// 5. Logs    //
////////////////
// #include "logs.cpp"

/////////////////
// 6. includes //
/////////////////
#ifndef INDEX
#include "index.cpp"
#endif
#ifndef TOOLS
#include "tools.cpp"
#endif
#ifndef SOLUTION
#include "solution.cpp"
#endif
#ifndef SIMULATION
#include "simulation.cpp"
#endif