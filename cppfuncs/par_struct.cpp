typedef struct par_struct
{
 int T;
 double beta;
 double rho;
 double G;
 double sigma_trans;
 double sigma_perm;
 double r;
 double m_max;
 int Nm;
 int Nxi;
 int Npsi;
 int seed;
 int simT;
 int simN;
 double* m_grid;
 double* xi_grid;
 double* xi_weight;
 double* psi_grid;
 double* psi_weight;
} par_struct;

int get_int_par_struct(par_struct* x, char* name){

 if( strcmp(name,"T") == 0 ){ return x->T; }
 else if( strcmp(name,"Nm") == 0 ){ return x->Nm; }
 else if( strcmp(name,"Nxi") == 0 ){ return x->Nxi; }
 else if( strcmp(name,"Npsi") == 0 ){ return x->Npsi; }
 else if( strcmp(name,"seed") == 0 ){ return x->seed; }
 else if( strcmp(name,"simT") == 0 ){ return x->simT; }
 else if( strcmp(name,"simN") == 0 ){ return x->simN; }
 else {return -9999;}

}


double get_double_par_struct(par_struct* x, char* name){

 if( strcmp(name,"beta") == 0 ){ return x->beta; }
 else if( strcmp(name,"rho") == 0 ){ return x->rho; }
 else if( strcmp(name,"G") == 0 ){ return x->G; }
 else if( strcmp(name,"sigma_trans") == 0 ){ return x->sigma_trans; }
 else if( strcmp(name,"sigma_perm") == 0 ){ return x->sigma_perm; }
 else if( strcmp(name,"r") == 0 ){ return x->r; }
 else if( strcmp(name,"m_max") == 0 ){ return x->m_max; }
 else {return NAN;}

}


double* get_double_p_par_struct(par_struct* x, char* name){

 if( strcmp(name,"m_grid") == 0 ){ return x->m_grid; }
 else if( strcmp(name,"xi_grid") == 0 ){ return x->xi_grid; }
 else if( strcmp(name,"xi_weight") == 0 ){ return x->xi_weight; }
 else if( strcmp(name,"psi_grid") == 0 ){ return x->psi_grid; }
 else if( strcmp(name,"psi_weight") == 0 ){ return x->psi_weight; }
 else {return NULL;}

}


