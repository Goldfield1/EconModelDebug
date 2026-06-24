// functions for calculating linear indices.
#ifndef MAIN
#define INDEX
#include "myheader.cpp"
#endif

namespace index {
    long long int index2(long long int i1,long long int i2,long long int N1,long long int N2){
        return i2 + i1*N2;
    }

    /* 
    typedef struct{
            int t;
            int iL;
            int iA;
            par_struct *par; 
            long long int idx(long long int iP){
                    return index::couple(t,iP,iL,iA , par); 
            }
        
    } index_couple_struct;

    typedef struct{
            // state levels
            int t;
            double love;
            double A;
            double power;

            // indices
            int iL;
            int iA;

            // model content
            par_struct *par;
            sol_struct *sol;
    } state_couple_struct; */
}