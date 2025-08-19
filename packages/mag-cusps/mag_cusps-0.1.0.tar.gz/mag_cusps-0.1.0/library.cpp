#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>

#ifdef USE_CUSP_HEADERS
#include "points.h"
#include "matrix.h"
#include "streamlines.h"
#include "magnetopause.h"
#include "read_file.h"
#include "preprocessing.h"
#include "raycast.h"
#include "fit_to_analytical.h"
#include "analysis.h"
#else
#include "../headers_cpp/points.h"
#include "../headers_cpp/matrix.h"
#include "../headers_cpp/streamlines.h"
#include "../headers_cpp/magnetopause.h"
#include "../headers_cpp/read_file.h"
#include "../headers_cpp/preprocessing.h"
#include "../headers_cpp/raycast.h"
#include "../headers_cpp/fit_to_analytical.h"
#include "../headers_cpp/analysis.h"
#endif


namespace casters
{
    pybind11::array_t<double> array_from_matrix( Matrix& matrix )
    {
        const Shape& sh = matrix.get_shape();
        const Shape& st = matrix.get_strides();

        return pybind11::array_t<double>(
            {sh.x, sh.y, sh.z, sh.i},                                                                       // shape
            {sizeof(double)*st.x, sizeof(double)*st.y, sizeof(double)*st.z, sizeof(double)*st.i},           // strides
            matrix.get_array(),                                                                             // data pointer
            pybind11::cast(matrix.get_array())                                                              // parent object (keeps data alive)
        );
    }

    pybind11::array_t<double> array_from_point_vec( const std::vector<Point>& points )
    {
        int length = points.size();
        double* arr = new double[length*3];
        if (arr == nullptr) { std::cout << "ERROR: out of memory when allocating array from point vector.\n"; exit(1); };

        for (int i=0; i<length; i++)
        {
            arr[3*i] = points[i].x;
            arr[3*i+1] = points[i].y;
            arr[3*i+2] = points[i].z;
        }

        return pybind11::array_t<double>(
            {length, 3},                        // shape
            {sizeof(double)*3, sizeof(double)},   // strides
            arr,                                // data pointer
            pybind11::cast(arr)                 // parent object (keeps data alive)
        );
    }

    pybind11::array_t<double> array_from_interest_point_vec( InterestPoint* interest_points, int nb_interest_points )
    {
        double* arr = new double[nb_interest_points*4];
        if (arr == nullptr) { std::cout << "ERROR: out of memory when allocating array from interest point vector.\n"; exit(1); };

        for (int i=0; i<nb_interest_points; i++)
        {
            arr[4*i] = interest_points[i].theta;
            arr[4*i+1] = interest_points[i].phi;
            arr[4*i+2] = interest_points[i].radius;
            arr[4*i+3] = interest_points[i].weight;
        }

        delete[] interest_points;

        return pybind11::array_t<double>(
            {nb_interest_points, 4},            // shape
            {sizeof(double)*4, sizeof(double)},   // strides
            arr,                                // data pointer
            pybind11::cast(arr)                 // parent object (keeps data alive)
        );
    }


    Matrix matrix_from_array( const pybind11::array_t<double>& arr )
    {
        int nb_dim = arr.ndim();
        Shape sh;
        Shape strides;

        if (nb_dim==4) 
        { 
            sh = Shape( arr.shape(0), arr.shape(1), arr.shape(2), arr.shape(3) ); 
            strides = Shape( arr.strides(0)/sizeof(double), arr.strides(1)/sizeof(double), arr.strides(2)/sizeof(double), arr.strides(3)/sizeof(double) );
        }
        else if (nb_dim==3) 
        { 
            sh = Shape( arr.shape(0), arr.shape(1), arr.shape(2), 1 ); 
            strides = Shape( arr.strides(0)/sizeof(double), arr.strides(1)/sizeof(double), arr.strides(2)/sizeof(double), 0 );
        }
        else if (nb_dim==2) 
        { 
            sh = Shape( arr.shape(0), arr.shape(1), 1, 1 ); 
            strides = Shape( arr.strides(0)/sizeof(double), arr.strides(1)/sizeof(double), 0, 0 );
        }
        else if (nb_dim==1) 
        { 
            sh = Shape( arr.shape(0), 1, 1, 1 ); 
            strides = Shape( arr.strides(0)/sizeof(double), 0, 0, 0 );
        }

        int total_size = sh.x*sh.y*sh.z*sh.i;

        double* mat = new double[total_size];
        if (mat == nullptr) { std::cout << "ERROR: out of memory when allocating Matrix from array.\n"; exit(1); };
        std::memcpy( mat, arr.data(), sizeof(double)*total_size );

        return Matrix( sh, strides, mat );
    }

    std::vector<InterestPoint> ip_vec_from_array( const pybind11::array_t<double>& arr )
    {
        std::vector<InterestPoint> ip(arr.shape(0));

        const double* p_arr = arr.data();
        
        for (int i=0; i<arr.shape(0); i++)
            ip[i] = { p_arr[4*i], p_arr[4*i+1], p_arr[4*i+2], p_arr[4*i+3] };

        return ip;
    }

    std::vector<Point> point_vec_from_array( const pybind11::array_t<double>& arr )
    {
        std::vector<Point> points(arr.shape(0));
        
        const double* p_arr = arr.data();
        
        for (int i=0; i<arr.shape(0); i++)
            points[i] = { p_arr[3*i], p_arr[3*i+1], p_arr[3*i+2] };

        return points;
    }

    Point point_from_array( const pybind11::array_t<double>& point )
    {
        pybind11::ssize_t nb_dims = point.ndim();
        if ( nb_dims > 1 || point.shape(0) != 3 )
        {
            throw pybind11::index_error("Point needs to be an array of shape (3)");
        }

        return Point( *point.data(0), *point.data(1), *point.data(2) );
    }

    Shape shape_from_array( const pybind11::array_t<int>& shape )
    {
        pybind11::ssize_t nb_dims = shape.ndim();
        if ( nb_dims > 1 || shape.shape(0) != 4 )
        {
            throw pybind11::index_error("Shape needs to be an array of shape (4)");
        }

        return Shape( *shape.data(0), *shape.data(1), *shape.data(2), *shape.data(3) );
    }
}


namespace preprocessing
{
    pybind11::array_t<double> orthonormalise_numpy( 
        const pybind11::array_t<double>& mat, 
        const pybind11::array_t<double>& X, const pybind11::array_t<double>& Y, const pybind11::array_t<double>& Z, 
        const pybind11::array_t<int>& new_shape )
    {
        Shape _shape = casters::shape_from_array( new_shape );
        Matrix _mat = casters::matrix_from_array( mat );
        Matrix _X = casters::matrix_from_array( X );
        Matrix _Y = casters::matrix_from_array( Y );
        Matrix _Z = casters::matrix_from_array( Z );

        _shape.i = _mat.get_shape().i;

        Matrix new_mat = orthonormalise( _mat, _X, _Y, _Z, &_shape ); 

        pybind11::array_t<double> ret = casters::array_from_matrix( new_mat );
        
        _X.del(); _Y.del(); _Z.del();
        _mat.del();

        return ret;
    }
}


namespace raycasting
{
    double get_bowshock_radius_numpy(  
        double theta, double phi,
        const pybind11::array_t<double>& Rho, const pybind11::array_t<double>& earth_pos,
        double dr )
    {
        Matrix _Rho = casters::matrix_from_array( Rho );
        Point _earth_pos = casters::point_from_array( earth_pos );

        double rad = get_bowshock_radius(theta, phi, _Rho, _earth_pos, dr);

        _Rho.del();

        return rad;
    }

    pybind11::array_t<double> get_bowshock_numpy( 
        const pybind11::array_t<double>& Rho, const pybind11::array_t<double>& earth_pos, 
        double dr, int nb_phi, int max_nb_theta )
    {
        Matrix _Rho = casters::matrix_from_array( Rho );
        Point _earth_pos = casters::point_from_array( earth_pos );

        pybind11::array_t<double> ret = casters::array_from_point_vec( get_bowshock(_Rho, _earth_pos, dr, nb_phi, max_nb_theta, true) );

        _Rho.del();

        return ret;
    }



    pybind11::array_t<double> get_interest_points_numpy( 
        const pybind11::array_t<double>& J_norm, const pybind11::array_t<double>& earth_pos,
        const pybind11::array_t<double>& Rho,
        double theta_min, double theta_max, 
        int nb_theta, int nb_phi, 
        double dx, double dr,
        double alpha_0_min, double alpha_0_max, int nb_alpha_0,
        double r_0_mult_min, double r_0_mult_max, int nb_r_0,
        double& avg_std_dev )
    {
        Matrix _Rho = casters::matrix_from_array( Rho );
        Matrix _J_norm = casters::matrix_from_array( J_norm );
        Point _earth_pos = casters::point_from_array( earth_pos );

        pybind11::array_t<double> ret = casters::array_from_interest_point_vec( get_interest_points(
            _J_norm, _earth_pos, 
            _Rho,
            theta_min, theta_max,
            nb_theta, nb_phi,
            dx, dr, alpha_0_min, alpha_0_max, nb_alpha_0,
            r_0_mult_min, r_0_mult_max, nb_r_0,
            &avg_std_dev
        ), nb_theta*nb_phi);

        _Rho.del();
        _J_norm.del();

        return ret;
    }

    pybind11::array_t<double> get_interest_points_numpy_no_std_dev( 
        const pybind11::array_t<double>& J_norm, const pybind11::array_t<double>& earth_pos,
        const pybind11::array_t<double>& Rho,
        double theta_min, double theta_max, 
        int nb_theta, int nb_phi, 
        double dx, double dr,
        double alpha_0_min, double alpha_0_max, double nb_alpha_0,
        double r_0_mult_min, double r_0_mult_max, double nb_r_0 )
    {
        Matrix _J_norm = casters::matrix_from_array( J_norm );
        Matrix _Rho = casters::matrix_from_array( Rho );
        Point _earth_pos = casters::point_from_array( earth_pos );

        pybind11::array_t<double> ret = casters::array_from_interest_point_vec( get_interest_points(
            _J_norm, _earth_pos, 
            _Rho,
            theta_min, theta_max,
            nb_theta, nb_phi,
            dx, dr, alpha_0_min, alpha_0_max, nb_alpha_0,
            r_0_mult_min, r_0_mult_max, nb_r_0,
            nullptr
        ), nb_theta*nb_phi);

        _Rho.del();
        _J_norm.del();

        return ret;
    }


    pybind11::array_t<double> process_interest_points_numpy(   
        const pybind11::array_t<double>& interest_points, 
        int nb_theta, int nb_phi, 
        const pybind11::array_t<int>& shape_sim, const pybind11::array_t<int>& shape_real,
        const pybind11::array_t<double>& earth_pos_sim, const pybind11::array_t<double>& earth_pos_real )
    {
        std::vector<InterestPoint> _interest_points = casters::ip_vec_from_array(interest_points);
        Shape _shape_sim = casters::shape_from_array(shape_sim), _shape_real = casters::shape_from_array(shape_real);
        Point _earth_pos_sim = casters::point_from_array(earth_pos_sim), _earth_pos_real = casters::point_from_array(earth_pos_real);

        process_interest_points( _interest_points.data(), nb_theta, nb_phi, _shape_sim, _shape_real, _earth_pos_sim, _earth_pos_real );

        return casters::array_from_interest_point_vec( _interest_points.data(), _interest_points.size() );
    }

    pybind11::array_t<double> process_points_numpy(    
        const pybind11::array_t<double>& points, 
        const pybind11::array_t<int>& shape_sim, const pybind11::array_t<int>& shape_real,
        const pybind11::array_t<double>& earth_pos_sim, const pybind11::array_t<double>& earth_pos_real )
    {
        std::vector<Point> _points = casters::point_vec_from_array( points );
        Shape _shape_sim = casters::shape_from_array(shape_sim), _shape_real = casters::shape_from_array(shape_real);
        Point _earth_pos_sim = casters::point_from_array(earth_pos_sim), _earth_pos_real = casters::point_from_array(earth_pos_real);

        process_points( _points, _shape_sim, _shape_real, _earth_pos_sim, _earth_pos_real );

        return casters::array_from_point_vec( _points );
    }
}


namespace fitting
{
    double Shue97( const pybind11::array_t<double>& params, double theta )
    {
        // if (theta<0 || theta>PI) { std::cout << "theta should be in [0; pi]\n"; exit(1); }

        double cos_theta = std::cos(theta);

        return *params.data(0) * std::pow( 2.0 / (1.0+cos_theta), *params.data(1) );
    }

    double Liu12( const pybind11::array_t<double>& params, double theta, double phi )
    {
        // if (theta<0 || theta>PI) { std::cout << "theta should be in [0; pi]\n"; exit(1); }
        // if (phi<-PI || phi>PI) { std::cout << "phi should be in [-pi; pi)\n"; exit(1); }

        double cos_theta = std::cos(theta);
        double cos_phi = std::cos(phi);

        double pos_side = is_pos<double>( cos_phi );

        return *params.data(0) * std::pow(
            2.0 / (1.0+cos_theta), 
            *params.data(1) + *params.data(2)*cos_phi + *params.data(3)*cos_phi*cos_phi
        ) - (
            *params.data(4) * std::exp( std::abs(theta-*params.data(5)) / *params.data(6) ) * pos_side +
            *params.data(7) * std::exp( std::abs(theta-*params.data(8)) / *params.data(9) ) * (1.0-pos_side)
        ) * cos_phi*cos_phi;
    }

    double EllipsisPoly( const pybind11::array_t<double>& params, double theta, double phi )
    {
        // if (theta<0 || theta>PI) { std::cout << "theta should be in [0; pi]\n"; exit(1); }
        // if (phi<-PI || phi>PI) { std::cout << "phi should be in [-pi; pi)\n"; exit(1); }

        double cos_theta = std::cos(theta);
        double cos_phi = std::cos(phi);

        double sigm_cos_phi = sigmoid<double>(cos_phi);

        double theta_by_ln_to_sn = std::pow( theta / *params.data(5), *params.data(6) );
        double theta_by_ls_to_ss = std::pow( theta / *params.data(8), *params.data(9) );

        return *params.data(0) * (
            (1.0+*params.data(10)) / (1.0+*params.data(10)*cos_theta)
        ) * std::pow(
            2.0 / (1.0+cos_theta), 
            *params.data(1) + *params.data(2)*cos_phi + *params.data(3)*cos_phi*cos_phi
        ) + (
            *params.data(4) * ( std::abs((1.0-theta_by_ln_to_sn)/(1.0+theta_by_ln_to_sn )) - 1.0 ) * sigm_cos_phi +
            *params.data(7) * ( std::abs((1.0-theta_by_ls_to_ss)/(1.0+theta_by_ls_to_ss )) - 1.0 ) * (1.0-sigm_cos_phi)
        ) * cos_phi*cos_phi;
    }



    template <typename Residual, int nb_params>
    pybind11::tuple fit_MP_numpy( 
        const pybind11::array_t<double>& interest_points, int nb_interest_points,
        const pybind11::array_t<double>& initial_params, 
        pybind11::array_t<double>& lowerbound, 
        pybind11::array_t<double>& upperbound,
        pybind11::array_t<double>& radii_of_variation, 
        int nb_runs=1, int max_nb_iterations_per_run=50
    )
    {
        std::vector<InterestPoint> _interest_points = casters::ip_vec_from_array( interest_points );

        OptiResult res = fit_MP<Residual, nb_params>( 
            _interest_points.data(), nb_interest_points,
            initial_params.data(), 
            lowerbound.mutable_data(),
            upperbound.mutable_data(),
            radii_of_variation.mutable_data(),
            nb_runs, max_nb_iterations_per_run
        );

        return pybind11::make_tuple( 
            pybind11::cast(res.params),
            res.cost
        );
    }
}



PYBIND11_MODULE(mag_cusps, m)
{
    m.doc() = "Topology analysis module for magnetic field data";


    m.def("preprocess", &preprocessing::orthonormalise_numpy, 
        pybind11::arg("mat"), 
        pybind11::arg("X"), pybind11::arg("Y"), pybind11::arg("Z"),
        pybind11::arg("new_shape")
    );

    m.def("get_bowshock_radius", &raycasting::get_bowshock_radius_numpy, 
        pybind11::arg("theta"), pybind11::arg("phi"),
        pybind11::arg("Rho"), pybind11::arg("earth_pos"), pybind11::arg("dr")
    );
    m.def("get_bowshock", &raycasting::get_bowshock_numpy,
        pybind11::arg("Rho"), pybind11::arg("earth_pos"), pybind11::arg("dr"),
        pybind11::arg("nb_phi"), pybind11::arg("max_nb_theta")
    );


    m.def("get_interest_points", &raycasting::get_interest_points_numpy,
        pybind11::arg("J_norm"), pybind11::arg("earth_pos"), pybind11::arg("Rho"),
        pybind11::arg("theta_min"), pybind11::arg("theta_max"),
        pybind11::arg("nb_theta"), pybind11::arg("nb_phi"),
        pybind11::arg("dx"), pybind11::arg("dr"),
        pybind11::arg("alpha_0_min"), pybind11::arg("alpha_0_max"), pybind11::arg("nb_alpha_0"),
        pybind11::arg("r_0_mult_min"), pybind11::arg("r_0_mult_max"), pybind11::arg("nb_r_0"),
        pybind11::arg("avg_std_dev")
    );
    m.def("get_interest_points", &raycasting::get_interest_points_numpy_no_std_dev,
        pybind11::arg("J_norm"), pybind11::arg("earth_pos"), pybind11::arg("Rho"),
        pybind11::arg("theta_min"), pybind11::arg("theta_max"),
        pybind11::arg("nb_theta"), pybind11::arg("nb_phi"),
        pybind11::arg("dx"), pybind11::arg("dr"),
        pybind11::arg("alpha_0_min"), pybind11::arg("alpha_0_max"), pybind11::arg("nb_alpha_0"),
        pybind11::arg("r_0_mult_min"), pybind11::arg("r_0_mult_max"), pybind11::arg("nb_r_0")
    );

    m.def("process_interest_points", &raycasting::process_interest_points_numpy,
        pybind11::arg("interest_points"),
        pybind11::arg("nb_theta"), pybind11::arg("nb_phi"),
        pybind11::arg("shape_sim"), pybind11::arg("shape_real"),
        pybind11::arg("earth_pos_sim"), pybind11::arg("earth_pos_real")
    );
    m.def("process_points", &raycasting::process_points_numpy,
        pybind11::arg("points"),
        pybind11::arg("shape_sim"), pybind11::arg("shape_real"),
        pybind11::arg("earth_pos_sim"), pybind11::arg("earth_pos_real")
    );


    m.def("Shue97", &fitting::Shue97,
        pybind11::arg("params"),
        pybind11::arg("theta")
    );

    m.def("Liu12", &fitting::Liu12,
        pybind11::arg("params"),
        pybind11::arg("theta"), pybind11::arg("phi")
    );

    m.def("Rolland25", &fitting::EllipsisPoly,
        pybind11::arg("params"),
        pybind11::arg("theta"), pybind11::arg("phi")
    );

    m.def("fit_to_Shue97", &fitting::fit_MP_numpy<Shue97Residual, 2>,
        pybind11::arg("interest_points"), pybind11::arg("nb_interest_points"),
        pybind11::arg("initial_params"),
        pybind11::arg("lowerbound"), pybind11::arg("upperbound"),
        pybind11::arg("radii_of_variation"),
        pybind11::arg("nb_runs") = 10, pybind11::arg("max_nb_iterations_per_run") = 50
    );

    m.def("fit_to_Liu12", &fitting::fit_MP_numpy<Liu12Residual, 10>,
        pybind11::arg("interest_points"), pybind11::arg("nb_interest_points"),
        pybind11::arg("initial_params"),
        pybind11::arg("lowerbound"), pybind11::arg("upperbound"),
        pybind11::arg("radii_of_variation"),
        pybind11::arg("nb_runs") = 10, pybind11::arg("max_nb_iterations_per_run") = 50
    );

    m.def("fit_to_Rolland25", &fitting::fit_MP_numpy<EllipsisPolyResidual, 11>,
        pybind11::arg("interest_points"), pybind11::arg("nb_interest_points"),
        pybind11::arg("initial_params"),
        pybind11::arg("lowerbound"), pybind11::arg("upperbound"),
        pybind11::arg("radii_of_variation"),
        pybind11::arg("nb_runs") = 10, pybind11::arg("max_nb_iterations_per_run") = 50
    );
}

