import numpy as np
from scipy.optimize import minimize

from EconModel import EconModelClass, jit

from consav.grids import nonlinspace
from consav.linear_interp import interp_1d
from consav.quadrature import log_normal_gauss_hermite

class BufferStockModelClass(EconModelClass):

    def settings(self):
        
        self.cpp_filename = 'cppfuncs/solve.cpp' # required for using C++
        self.cpp_options = {'compiler':'vs'} # optional
        self.cpp_structsmap = {'par':'par_struct'} # optional


    def setup(self):
        """ set baseline parameters """

        # unpack
        par = self.par

        par.T = 20 # time periods
        
        # preferences
        par.beta = 0.99 # discount factor
        par.rho = 1.5 # CRRA coefficient

        # income
        par.G = 1.02 # income growth level
        par.sigma_trans = 0.1 # transitory income shock standard deviation
        par.sigma_perm = 0.1 # permanent income shock standard deviation

        # saving
        par.r = 0.03 # interest rate

        # grid
        par.m_max = 20.0 # maximum point in resource grid
        par.Nm = 200 # number of grid points in resource grid    

        par.Nxi = 5 # number of points in transitory income shock expectaion
        par.Npsi = 5  # number of points in permanent income shock expectaion

        # simulation
        par.seed = 9210
        par.simT = par.T # number of periods
        par.simN = 1_000 # number of individuals


    def allocate(self):
        """ allocate model """

        # unpack
        par = self.par
        sol = self.sol
        sim = self.sim
        
        # a. asset grid
        odd_num = np.mod(par.Nm,2)
        first_part = nonlinspace(0.0001,par.m_max//2,(par.Nm+odd_num)//2,1.3)
        last_part = np.flip(par.m_max - nonlinspace(0.0001,par.m_max//2,(par.Nm-odd_num)//2 + 1,1.3))[1:]
        par.m_grid = np.append(first_part,last_part)
        par.m_grid = nonlinspace(0.00001,par.m_max,par.Nm,1.1) # always have a bit of resources


        # b. income shock grids
        par.xi_grid,par.xi_weight = log_normal_gauss_hermite(par.sigma_trans,par.Nxi)
        par.psi_grid,par.psi_weight = log_normal_gauss_hermite(par.sigma_perm,par.Npsi)

        # b. solution arrays
        shape = (par.T,par.Nm)
        sol.c = np.nan + np.zeros(shape)
        sol.V = np.nan + np.zeros(shape)

        # c. simulation arrays
        shape = (par.simN,par.simT)
        sim.c = np.nan + np.zeros(shape)
        sim.m = np.nan + np.zeros(shape)
        sim.a = np.nan + np.zeros(shape)
        sim.C = np.nan + np.zeros(shape)
        sim.M = np.nan + np.zeros(shape)
        sim.A = np.nan + np.zeros(shape)
        sim.P = np.nan + np.zeros(shape)
        sim.Y = np.nan + np.zeros(shape)
        
        # d. initialization
        sim.a_init = np.zeros(par.simN)
        sim.P_init = np.ones(par.simN)

        # e. random log-normal mean one income shocks
        np.random.seed(par.seed)
        sim.xi = np.exp(par.sigma_trans*np.random.normal(size=shape) - 0.5*par.sigma_trans**2)
        sim.psi = np.exp(par.sigma_perm*np.random.normal(size=shape) - 0.5*par.sigma_perm**2)


    ############
    # Solution #
    def solve(self):

        # a. unpack
        par = self.par
        sol = self.sol
        
        # b. solve last period
        t = par.T-1
        sol.c[t,:] = par.m_grid
        sol.V[t,:] = self.util(sol.c[t,:])

        # c. loop backwards [note, the last element, N, in range(N) is not included in the loop due to index starting at 0]
        for t in reversed(range(par.T-1)):

            # i. loop over state variable: resources in beginning of period
            for im,resources in enumerate(par.m_grid):

                # ii. find optimal consumption at this level of resources in this period t.

                # objective function: negative since we minimize
                obj = lambda c: - self.value_of_choice(c[0],resources,t)  

                # bounds on consumption
                lb = 0.000001 # avoid dividing with zero
                ub = resources

                # call optimizer
                c_init = np.array(0.5*ub) # initial guess on optimal consumption
                res = minimize(obj,c_init,bounds=((lb,ub),),method='SLSQP', tol = 1e-10)
                
                # store results
                sol.c[t,im] = res.x[0]
                sol.V[t,im] = -res.fun
        
    def solve_egm(self):

        # a. unpack
        par = self.par
        sol = self.sol

        # 1. Initialize arrays to store today's raw EGM results
        # (Assuming par.Na is the number of points in your asset grid)

        # b. solve last period
        t = par.T-1
        sol.c[t,:] = par.m_grid
        sol.V[t,:] = self.util(sol.c[t,:])

        # c. loop backwards [note, the last element, N, in range(N) is not included in the loop due to index starting at 0]
        for t in range(par.T-2, -1, -1):
            # 2. Loop over the exogenous asset grid (this replaces your missing state)
            sol_c_raw = np.zeros(par.Nm)
            sol_m_raw = np.zeros(par.Nm)

            for i_a, a_state in enumerate(par.m_grid):
                
                EV_next = 0.0
                
                # 3. Integrate over the shocks
                for i_xi, xi in enumerate(par.xi_grid):
                    for i_psi, psi in enumerate(par.psi_grid):
                        
                        # Normalization factor
                        fac = par.G * psi 
                        
                        # Calculate next period's cash-on-hand based on chosen assets
                        m_next = (a_state * (par.r + 1.0)) / fac + xi
                        
                        # Interp next period's consumption using consav's interp_1d
                        # (Assuming sol_next_c is the solved consumption array from t+1)
                        c_next = interp_1d(par.m_grid, sol.c[t+1], m_next) 
                        
                        # Calculate and weight marginal utility
                        marg_util_next = (fac ** (-par.rho)) * (c_next ** (-par.rho)) 
                        weighted_MU_next = marg_util_next * par.xi_weight[i_xi] * par.psi_weight[i_psi]
                        
                        # Accumulate (Only once per shock combination!)
                        EV_next += weighted_MU_next

                # 4. EGM Inversion step for this asset state
                c_today = (par.beta * (par.r + 1.0) * EV_next) ** (-1.0 / par.rho) 
                m_today = a_state + c_today
                
                # Save raw results
                sol_c_raw[i_a] = c_today
                sol_m_raw[i_a] = m_today


            # Euler equation-derived points
            c_today_interp = np.interp(par.m_grid, sol_m_raw, sol_c_raw)
            c_today_interp = np.minimum(c_today_interp, par.m_grid)
            #c_today_interp = np.maximum(c_today_interp, par.m_grid)

            #slope = (sol_c_raw[-1] - sol_c_raw[-2]) / (sol_m_raw[-1] - sol_m_raw[-2])
                
            # Fill the tail using this slope
            #mask = par.m_grid > sol_m_raw[-1]
            #c_today_interp[mask] = sol_c_raw[-1] + slope * (par.m_grid [mask] - sol_m_raw[-1])

            sol.c[t, :] = c_today_interp
            for i_a, a_state in enumerate(par.m_grid):
                sol.V[t, i_a] = self.value_of_choice( sol.c[t, i_a], a_state,t)




    def value_of_choice(self,cons,resources,t):

        # a. unpack
        par = self.par
        sol = self.sol

        # b. utility from consumption
        util = self.util(cons)
        
        # c. expected continuation value from savings
        V_next = sol.V[t+1]
        assets = resources - cons
        
        # loop over income shocks 
        EV_next = 0.0
        for i_xi,xi in enumerate(par.xi_grid):
            for i_psi,psi in enumerate(par.psi_grid):
                fac = par.G*par.psi_grid[i_psi] # normalization factor

                # interpolate next period value function for this combination of transitory and permanent income shocks
                m_next = (1.0+par.r)*assets/fac + par.xi_grid[i_xi]
                V_next_interp = interp_1d(par.m_grid,V_next,m_next)
                V_next_interp = (fac**(1.0-par.rho)) * V_next_interp # normalization factor

                # weight the interpolated value with the likelihood
                EV_next += V_next_interp*par.xi_weight[i_xi]*par.psi_weight[i_psi]

        # d. return value of choice
        return util + par.beta*EV_next


    def util(self,c):
        par = self.par

        return (c)**(1.0-par.rho) / (1.0-par.rho)


    ##############
    # Simulation #
    def simulate(self):

        # a. unpack
        par = self.par
        sol = self.sol
        sim = self.sim

        # b. loop over individuals and time
        for i in range(par.simN):

            # i. initialize permanent income and normalized assets 
            t = 0
            sim.P[i,t] = sim.P_init[i]
            sim.Y[i,t] = sim.P[i,t]*sim.xi[i,t]

            sim.a[i,t] = sim.a_init[i]
            sim.A[i,t] = sim.a[i,t]*sim.P[i,t]
            
            # ii. resources (normalized)
            sim.M[i,t] = (1.0+par.r)*sim.A[i,t] + sim.Y[i,t]
            sim.m[i,t] = sim.M[i,t]/sim.P[i,t]

            for t in range(par.simT):
                if t<par.T: # check that simulation does not go further than solution                 

                    # iii. interpolate optimal consumption (normalized)
                    sim.c[i,t] = interp_1d(par.m_grid,sol.c[t],sim.m[i,t])

                    # iv. Update next-period states
                    if t<par.simT-1:
                        sim.P[i,t+1] = par.G*sim.P[i,t]*sim.psi[i,t+1]
                        sim.Y[i,t+1] = sim.P[i,t+1]*sim.xi[i,t+1]

                        sim.a[i,t+1] = sim.m[i,t] - sim.c[i,t]
                        sim.A[i,t+1] = sim.a[i,t+1]*sim.P[i,t+1]

                        sim.M[i,t+1] = (1.0+par.r)*sim.A[i,t+1] + sim.Y[i,t+1]
                        sim.m[i,t+1] = sim.M[i,t+1]/sim.P[i,t+1]


