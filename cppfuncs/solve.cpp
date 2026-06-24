#define MAIN
#include "myheader.h"

// include these again here to ensure that they are automatically compiled by consav
#ifndef MAIN
#endif

/////////////
// 5. MAIN //
/////////////

EXPORT void solve(sol_struct *sol, par_struct *par){
    
    // pre-compute intra-temporal optimal allocation

    // loop backwards
    for (int t = par->T-1; t >= 0; t--){
        solution::solve(t,sol,par); 
    }
}


EXPORT void simulate(sim_struct *sim, sol_struct *sol, par_struct *par){
    return;
}
