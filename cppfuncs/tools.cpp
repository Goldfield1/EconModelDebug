// functions related to the institutional environment.
#ifndef MAIN
#define TOOLS
#include "myheader.cpp"
#endif


namespace tools {   

double maxf(double* vec, int num){

    double max = vec[0];
    for(int i=1;i<num;i++){
        if(vec[i]>max){
            max = vec[i];
        }
    }

    return max;
}
double minf(double* vec, int num){

    double min = vec[0];
    for(int i=1;i<num;i++){
        if(vec[i]<min){
            min = vec[i];
        }
    }

    return min;
}

int binary_search(int imin, int Nx, double *x, double xi)
{
    int imid, half;

    // a. checks
    if(xi <= x[0]){
        return 0;
    } else if(xi >= x[Nx-2]) {
        return Nx-2;
    }

    // b. binary search
    Nx = Nx-imin;
    while((half = Nx/2)){
        imid = imin + half;
        imin = (x[imid] <= xi) ? imid:imin;
        Nx  -= half;
    }

    return imin;

}

double interp_1d_index(double* grid1,int num1 ,double* value1,double xi1,int j1){
    /* 1d interpolation for one point
        
    Args:
        grid1 : 1d grid
        value : value array (2d)
        xi1 : input point
    Returns:
        yi : output
    */

    // a. left/right
    double nom_left = grid1[j1+1]-xi1;
    double nom_right = xi1-grid1[j1];

    // b. interpolation
    double denom = (grid1[j1+1]-grid1[j1]);
    double nom = 0.0;
    for (size_t k1 = 0; k1 < 2; k1++){
        double nom_1 = nom_left;
        if (k1==1){
            nom_1 = nom_right;
        }
        nom += nom_1*value1[j1+k1];
    }

    return nom/denom;

} // interp_1d

double interp_1d(double* grid1,int num1 ,double* value1,double xi1){
    /* 1d interpolation for one point
        
    Args:
        grid1 : 1d grid
        value : value array (2d)
        xi1 : input point
    Returns:
        yi : output
    */

    // a. search 
    int j1 = binary_search(0,num1,grid1,xi1);

    return interp_1d_index(grid1,num1 ,value1,xi1,j1);

} // interp_1d


double interp_1d_index_delta(double* grid1,int num1 ,double* value1,double xi1,int j1, long long int delta_y=1, int idx_y=0, long long int delta_x=1, int idx_x=0){
    /* 1d interpolation for one point
        
    Args:
        grid1 : 1d grid
        value : value array (2d)
        xi1 : input point
        delta_y : delta in y direction
        idx_y : start index in y direction
        delta_x : delta in x direction
        idx_x : start index in x direction
    Returns:
        yi : output
    */
    // a. left/right
    double nom_left = grid1[idx_x+(j1+1)*delta_x]-xi1;
    double nom_right = xi1-grid1[idx_x+j1*delta_x];
    // b. interpolation
    double denom = (grid1[idx_x+(j1+1)*delta_x]-grid1[idx_x+j1*delta_x]);
    double nom = 0.0;
    for (size_t k1 = 0; k1 < 2; k1++){
        double nom_1 = nom_left;
        if (k1==1){
            nom_1 = nom_right;
        }
        nom += nom_1*value1[idx_y + (j1+k1)*delta_y];
    }
    return nom/denom;
} // interp_1d_delta



void interp_1d_2out_index(double* grid1,int num1 ,double* value1,double* value2,double xi1 , double* out1,double* out2 ,int j1){

    // a. left/right
    double nom_1_left = grid1[j1+1]-xi1;
    double nom_1_right = xi1-grid1[j1];

    // b. interpolation
    double denom = (grid1[j1+1]-grid1[j1]);
    double nom1 = 0.0;
    double nom2 = 0.0;
    for (size_t k1 = 0; k1 < 2; k1++){
        double nom_1 = nom_1_left;
        if (k1==1){
            nom_1 = nom_1_right;
        }
        nom1 += nom_1*value1[j1+k1];
        nom2 += nom_1*value2[j1+k1];
    }

    out1[0] = nom1/denom;
    out2[0] = nom2/denom;
}


void interp_1d_2out(double* grid1,int num1 ,double* value1,double* value2,double xi1 , double* out1,double* out2 ){
    /* 1d interpolation for one point
        
    Args:
        grid1 : 1d grid
        value : value array (2d)
        xi1 : input point
    Returns:
        yi : output
    */

    // a. search in each dimension
    int j1 = binary_search(0,num1,grid1,xi1);

    // b. calculate the interpolants using the index
    interp_1d_2out_index(grid1,num1,value1,value2,xi1,out1,out2 ,j1);

} // interp_1d_2out

} // tools