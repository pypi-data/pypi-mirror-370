mod algo;
mod utils;

use core::panic;

use arrayfire::*;
use numpy::{PyArray2, PyArrayMethods};
use pyo3::prelude::*;
use pyo3::PyObject;
use rand::Rng;

use crate::algo::self_organizing_map;
use crate::utils::{array2d, configure_backend, generate_grid};

#[pyfunction]
#[pyo3(signature = (data, units, iters=1, sigma_initial=1.0, batch_size=1, device=None, seed=None))]
fn som(
    data: Vec<Vec<f32>>,
    units: PyObject,
    iters: usize,
    sigma_initial: f32,
    batch_size: usize,
    device: Option<String>,
    seed: Option<u64>,
    py: Python,
) -> Bound<PyArray2<f32>> {
    configure_backend(device.as_deref());

    set_seed(seed.unwrap_or_else(|| rand::thread_rng().gen::<u64>()));

    let units_array = if let Ok(dims) = units.extract::<Vec<usize>>(py) {
        generate_grid(dims)
    } else if let Ok(unit_data) = units.extract::<Vec<Vec<f32>>>(py) {
        array2d(unit_data)
    } else {
        panic!("Units must be either a vector of dimensions or a 2D vector of unit weights");
    };

    let result_af = self_organizing_map(
        &array2d(data),
        &units_array,
        iters,
        sigma_initial,
        batch_size,
    );

    let mut host_data: Vec<f32> = vec![f32::default(); result_af.elements() as usize];
    result_af.host(&mut host_data);

    let stacked_vec = host_data
        .chunks_exact(result_af.dims()[0] as usize)
        .map(|chunk| chunk.to_vec())
        .collect::<Vec<_>>();

    PyArray2::from_vec2(py, &stacked_vec)
        .expect("Failed to create PyArray2")
        .transpose()
        .expect("Failed to transpose PyArray2")
}

#[pymodule]
mod somu {
    #[pymodule_export]
    use super::som;
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_main() {
        let data = randn::<f32>(dim4!(100, 2));
        let grid = generate_grid(vec![3, 3, 3]);
        self_organizing_map(&data, &grid, 10, 1.0, 1);
        self_organizing_map(&data, &grid, 10, 1.0, 100);
    }

    #[test]
    fn test_convert() {
        let data = vec![vec![1.0, 2.0], vec![3.0, 4.0], vec![5.0, 6.0]];
        let af_array = array2d(data);
        assert_eq!(af_array.dims(), dim4!(3, 2, 1, 1));
    }
}
