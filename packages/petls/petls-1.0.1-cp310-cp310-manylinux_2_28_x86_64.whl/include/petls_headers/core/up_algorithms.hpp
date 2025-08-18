#ifndef up_algs_H
#define up_algs_H

#include "../typedefs.hpp"
#include "FilteredBoundaryMatrix.hpp"
// #include <Eigen/IterativeLinearSolvers>
// #include <unsupported/Eigen/SparseExtra>
#include <Eigen/Cholesky>
#include <Eigen/QR>
#include <chrono>
// #include "Eigen/Eigenvalues"
// #include "Eigen/SVD"
// #include "../petls.hpp"
namespace petls{

    // wrapper classes for algorithms to compute up Laplacian.
    // just need to implement the following signature:
    // void operator()(FilteredBoundaryMatrix<storage>* fbm, filtration_type a, filtration_type b, DenseMatrix_PL &L_up);

    template <typename storage>
    inline void schur_algorithm(petls::FilteredBoundaryMatrix<storage>* fbm, filtration_type a, filtration_type b, DenseMatrix_PL &L_up){
        // using storage = float;
        int a_row_index = fbm->index_of_filtration(false,a);
        int b_row_index = fbm->index_of_filtration(false,b);
        int b_col_index = fbm->index_of_filtration(true,b);

        if (a_row_index == b_row_index){
            Eigen::SparseMatrix<storage> B_pers(b_row_index, b_col_index);
            fbm->submatrix_at_filtration(b, B_pers);
            L_up = (B_pers*B_pers.transpose()).template cast<coefficient_type>();
            return;
        } else if (a_row_index == -1){ // no rows, return 0x0 empty matrix
            L_up.setZero(0,0);
            return;

        } else if (b_col_index == -1){ // no columns, return nxn 0-matrix for n = number of cells in C_{up_dim}^a
            L_up.setZero(a_row_index+1,a_row_index+1);
            return;

        }
        // NOTE: doing the self adjoint lower triangular trick here is slower
        // possibly because of the conversions between dense and sparse

        Eigen::SparseMatrix<storage> B_pers_int(b_row_index, b_col_index);
        fbm->submatrix_at_filtration(b, B_pers_int);
        
    
        Eigen::SparseMatrix<storage> L_up_b_int(B_pers_int.rows(), B_pers_int.rows());
        // L_up_b_int = B_pers_int*B_pers_int.transpose();
        L_up_b_int.template selfadjointView<Eigen::Lower>().rankUpdate(B_pers_int);
        SparseMatrix_PL L_up_b(L_up_b_int.rows(), L_up_b_int.cols());
        L_up_b = L_up_b_int.template cast<coefficient_type>();

        int a_rows = a_row_index + 1;
        int b_rows = b_row_index + 1;

        
        
        // auto start_solve = std::chrono::high_resolution_clock::now();
        // split L_up_b into 4 along those borders
        // A B
        // C D
        // and compute A - B*D^{-1}*C
        // by the structure of L, we know B = C^T
        // and we want A - B * (things)
        // Also compute D^{-1}*C by solving the sparse lower-triangular linear system

        SparseMatrix_PL A = L_up_b.topLeftCorner(a_rows, a_rows);
        SparseMatrix_PL C = L_up_b.bottomLeftCorner(b_rows-a_rows, a_rows);
        SparseMatrix_PL B = C.transpose();
        SparseMatrix_PL D = L_up_b.bottomRightCorner(b_rows-a_rows, b_rows-a_rows);
        // D.makeCompressed();
        // Eigen::LeastSquaresConjugateGradient<SparseMatrix_PL> solver(D);        
        // Eigen::BiCGSTAB<SparseMatrix_PL> solver(D);
        // solver.setMaxIterations(1000);
        
        // Eigen::SparseQR<SparseMatrix_PL, Eigen::COLAMDOrdering<int>> solver(D);
        // Eigen::ConjugateGradient<SparseMatrix_PL, Eigen::Lower> solver(D);
        // solver.setTolerance(1e-4)
        // L_up = A - B * solver.solve(C); 

        L_up = A - B * DenseMatrix_PL(D).ldlt().solve(DenseMatrix_PL(C));
        
        // The computed matrix is only correct in the lower triangular portion.
        // Eigen::SelfAdjointEigensolver is okay with this, but to avoid confusion and issues with other eigensolvers,
        // We symmetrize the matrix:
        L_up = DenseMatrix_PL(L_up.selfadjointView<Eigen::Lower>());
        

        // auto end_solve = std::chrono::high_resolution_clock::now();
        // auto duration_solve = std::chrono::duration_cast<std::chrono::milliseconds>(end_solve - start_solve);
        // std::cout << "duration solve (ms):" << duration_solve.count() << std::endl;

        return;
    }

                                
    // inline void schur_algorithm(petls::FilteredBoundaryMatrix<int>* fbm, filtration_type a, filtration_type b, DenseMatrix_PL &L_up){
    //     using storage = int;
    //     int a_row_index = fbm->index_of_filtration(false,a);
    //     int b_row_index = fbm->index_of_filtration(false,b);
    //     int b_col_index = fbm->index_of_filtration(true,b);

    //     if (a_row_index == b_row_index){
    //         Eigen::SparseMatrix<storage> B_pers(b_row_index, b_col_index);
    //         fbm->submatrix_at_filtration(b, B_pers);
    //         L_up = (B_pers*B_pers.transpose()).template cast<coefficient_type>();
    //         return;
    //     } else if (a_row_index == -1){ // no rows, return 0x0 empty matrix
    //         L_up.setZero(0,0);
    //         return;

    //     } else if (b_col_index == -1){ // no columns, return nxn 0-matrix for n = number of cells in C_{up_dim}^a
    //         L_up.setZero(a_row_index+1,a_row_index+1);
    //         return;

    //     }
    //     // NOTE: doing the self adjoint lower triangular trick here is slower
    //     // possibly because of the conversions between dense and sparse

    //     Eigen::SparseMatrix<storage> B_pers_int(b_row_index, b_col_index);
    //     fbm->submatrix_at_filtration(b, B_pers_int);
        
    
    //     Eigen::SparseMatrix<storage> L_up_b_int(B_pers_int.rows(), B_pers_int.rows());
    //     // L_up_b_int = B_pers_int*B_pers_int.transpose();
    //     L_up_b_int.template selfadjointView<Eigen::Lower>().rankUpdate(B_pers_int);
    //     SparseMatrix_PL L_up_b(L_up_b_int.rows(), L_up_b_int.cols());
    //     L_up_b = L_up_b_int.template cast<coefficient_type>();

    //     int a_rows = a_row_index + 1;
    //     int b_rows = b_row_index + 1;

        
        
    //     // auto start_solve = std::chrono::high_resolution_clock::now();
    //     // split L_up_b into 4 along those borders
    //     // A B
    //     // C D
    //     // and compute A - B*D^{-1}*C
    //     // by the structure of L, we know B = C^T
    //     // and we want A - B * (things)
    //     // Also compute D^{-1}*C by solving the sparse lower-triangular linear system

    //     SparseMatrix_PL A = L_up_b.topLeftCorner(a_rows, a_rows);
    //     SparseMatrix_PL C = L_up_b.bottomLeftCorner(b_rows-a_rows, a_rows);
    //     SparseMatrix_PL B = C.transpose();
    //     SparseMatrix_PL D = L_up_b.bottomRightCorner(b_rows-a_rows, b_rows-a_rows);
    //     // D.makeCompressed();
    //     // Eigen::LeastSquaresConjugateGradient<SparseMatrix_PL> solver(D);        
    //     // Eigen::BiCGSTAB<SparseMatrix_PL> solver(D);
    //     // solver.setMaxIterations(1000);
        
    //     // Eigen::SparseQR<SparseMatrix_PL, Eigen::COLAMDOrdering<int>> solver(D);
    //     // Eigen::ConjugateGradient<SparseMatrix_PL, Eigen::Lower> solver(D);
    //     // solver.setTolerance(1e-4)
    //     // L_up = A - B * solver.solve(C); 

    //     L_up = A - B * DenseMatrix_PL(D).ldlt().solve(DenseMatrix_PL(C));
        
    //     // The computed matrix is only correct in the lower triangular portion.
    //     // Eigen::SelfAdjointEigensolver is okay with this, but to avoid confusion and issues with other eigensolvers,
    //     // We symmetrize the matrix:
    //     L_up = DenseMatrix_PL(L_up.selfadjointView<Eigen::Lower>());
        

    //     // auto end_solve = std::chrono::high_resolution_clock::now();
    //     // auto duration_solve = std::chrono::duration_cast<std::chrono::milliseconds>(end_solve - start_solve);
    //     // std::cout << "duration solve (ms):" << duration_solve.count() << std::endl;

    //     return;
    // }

}

#endif