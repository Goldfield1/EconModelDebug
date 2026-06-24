#ifndef MAIN
#define SINGLE
#include "myheader.cpp"
#endif

namespace solution {
    typedef struct {
        
        int t;
        double resources;             
        double *V_next;      
        par_struct *par;      

    } solver_struct;


    double util(double c, par_struct* par) {
        return pow(c, 1.0-par->rho) / (1.0-par->rho);
    }

    double value_of_choice(double cons,double resources,int t, double* V_next, par_struct* par){

        // flow-utility
        double Util = util(cons,par);

        auto assets = resources - cons;

        auto idx_next = index::index2(t+1, 0, par->T, par->Nm);

        double EV_next = 0.0;
        for (int ix=0; ix<par->Nxi;ix++){
            for (int i_psi=0; i_psi<par->Npsi;i_psi++) {

                auto fac = par->G*par->psi_grid[i_psi]; // normalization factor

                // interpolate next period value function for this combination of transitory and permanent income shocks
                auto m_next = (1.0+par->r)*assets/fac + par->xi_grid[ix];

                /// b. calculate expected marginal utility
                int mPoint = tools::binary_search(0, par->Nm, par->m_grid, m_next);
                
                //double V_next_interp = par->beta*tools::interp_1d_index(par->m_grid, par->Nm, V_next,m_next, mPoint);
                double V_next_interp = tools::interp_1d(par->m_grid, par->Nm, V_next,m_next);
                V_next_interp = pow(fac, 1.0-par->rho) * V_next_interp; // normalization factor

                // weight the interpolated value with the likelihood
                EV_next += V_next_interp*par->xi_weight[ix]*par->psi_weight[i_psi];

            }

        }       
        return Util + par->beta*EV_next;
    }

    double objfunc(unsigned n, const double *x, double *grad, void *solver_data_in){

        // unpack
        solver_struct *solver_data = (solver_struct *) solver_data_in;  
        
        double c = x[0];
        double resources = solver_data->resources;
        int t = solver_data->t;
        par_struct *par = solver_data->par;

        return - value_of_choice(c,resources,t,solver_data->V_next,par);
    }

    void solve(int t,sol_struct *sol,par_struct *par){
        double love = 0.0; // no love for singles 

        // terminal period
        if (t == (par->T-1)){
            for (int iM=0; iM<par->Nm;iM++){
                int idx = index::index2(t,iM,par->T, par->Nm);

                sol->c[idx] = par->m_grid[iM];
                sol->V[idx] = util(sol->c[idx], par);

            }
        } else {
            #pragma omp parallel num_threads(1)
            {
                // 1. allocate objects for solver
                solver_struct* solver_data = new solver_struct;
                
                int const dim = 1;
                double lb[dim],ub[dim],x[dim];
                
                auto opt = nlopt_create(NLOPT_LN_BOBYQA, dim); // NLOPT_LD_MMA NLOPT_LD_LBFGS NLOPT_GN_ORIG_DIRECT
                double minf=0.0;

                // 2. loop over assets
                #pragma omp for
                for (int iM=0; iM<par->Nm;iM++){
                    auto idx = index::index2(t,iM,par->T, par->Nm);
                    
                    // resources
                    double resources = par->m_grid[iM];
                    
                    // settings
                    solver_data->resources = resources;
                    solver_data->t = t;
                    solver_data->V_next = &sol->V[index::index2(t+1, 0, par->T, par->Nm)]; // sol->EVm_start_singl;
                    solver_data->par = par;
                    nlopt_set_min_objective(opt, objfunc, solver_data);
                        
                    // bounds
                    lb[0] = 1.0e-6;
                    ub[0] = solver_data->resources;
                    nlopt_set_lower_bounds(opt, lb);
                    nlopt_set_upper_bounds(opt, ub);

                    // optimize
                    x[0] = solver_data->resources/2.0;
                    nlopt_optimize(opt, x, &minf);

                    sol->c[idx] = x[0];
                    sol->V[idx] = -minf;       
                    
                } // iA

                // 4. destroy optimizer
                nlopt_destroy(opt);
                delete solver_data;

            } // pragma
            
        }   
        
    }

}
