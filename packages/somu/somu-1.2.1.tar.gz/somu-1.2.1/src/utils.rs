use arrayfire::*;
use itertools::Itertools;
use rand::rngs::StdRng;
use rand::seq::SliceRandom;
use rand::SeedableRng;

pub fn configure_backend(device: Option<&str>) {
    match device {
        Some("cuda") => {
            set_backend(Backend::CUDA);
        }
        Some("cpu") => {
            set_backend(Backend::CPU);
        }
        _ => {
            let backends = get_available_backends();
            if backends.contains(&Backend::CUDA) {
                set_backend(Backend::CUDA);
            } else {
                set_backend(Backend::CPU);
            }
        }
    }
}

pub fn sample_rows(arr: &Array<f32>, n: usize) -> Array<f32> {
    let total_rows = arr.dims()[0] as usize;

    assert!(n <= total_rows, "Cannot sample more rows than exist.");

    // Randomly choose `n` unique indices
    let mut rng = StdRng::seed_from_u64(get_seed());
    let indices: Vec<u32> = (0..total_rows as u32)
        .collect::<Vec<_>>()
        .choose_multiple(&mut rng, n)
        .cloned()
        .collect();

    let index_array = Array::new(&indices, dim4!(indices.len() as u64));
    lookup(arr, &index_array, 0)
}

pub fn array2d(data: Vec<Vec<f32>>) -> Array<f32> {
    let flat_vec = data.concat();
    let rows = data.len();
    let cols = data[0].len();
    arrayfire::transpose(
        &Array::new(&flat_vec, dim4!(cols as u64, rows as u64)),
        false,
    )
}

pub fn generate_grid(dims: Vec<usize>) -> Array<f32> {
    array2d(
        dims.into_iter()
            .map(|dim_size| (0..dim_size).map(|x| x as f32))
            .multi_cartesian_product()
            .collect(),
    )
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_array2d() {
        let data = vec![vec![1.0, 2.0], vec![3.0, 4.0], vec![5.0, 6.0]];
        let af_array = array2d(data);
        assert_eq!(af_array.dims(), dim4!(3, 2, 1, 1));
    }

    #[test]
    fn test_generate_grid() {
        let grid = generate_grid(vec![3, 3, 3]);
        assert_eq!(grid.dims(), dim4!(3 * 3 * 3, 3, 1, 1));
    }

    #[test]
    fn test_sample_rows() {
        let grid = generate_grid(vec![4, 4, 4, 4]);
        let sampled_rows = sample_rows(&grid, 16);
        assert_eq!(sampled_rows.dims(), dim4!(16, 4, 1, 1));
    }
}
