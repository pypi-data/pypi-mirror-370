# module load miniforge/3 > /dev/null 2>&1
module load tools/prod > /dev/null 2>&1
# module load SciPy-bundle/2025.07-gfbf-2025.07 > /dev/null 2>&1

# for reading the .pvtr files
# module load VTK > /dev/null 2>&1		

# dependency of the Ceres least squares solver
module load Eigen 	
module load Abseil/20230125.3-GCCcore-12.3.0				
module load googletest 

module load FlexiBLAS

module load CMake

# to create the library 
module load pybind11