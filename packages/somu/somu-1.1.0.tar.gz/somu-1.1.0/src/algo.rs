use arrayfire::*;

use crate::utils::sample_rows;

pub fn compute_distance_matrix(p: &Array<f32>, q: &Array<f32>) -> Array<f32> {
    let (p_rows, q_rows, feat_dim) = (p.dims()[0], q.dims()[0], p.dims()[1]);

    let p_exp = tile(&moddims(p, dim4!(p_rows, 1, feat_dim)), dim4!(1, q_rows, 1));
    let q_exp = tile(&moddims(q, dim4!(1, q_rows, feat_dim)), dim4!(p_rows, 1, 1));
    let diff = p_exp - q_exp;
    sqrt(&sum(&(&diff * &diff), 2))
}

// Organize the data by updating the centroids based on Best Matching Units (BMUs)
pub fn organize(x: &Array<f32>, influence: &Array<f32>, dst: &Array<f32>) -> Array<f32> {
    let (_, bmu_indices) = imin(&dst, 1);
    let influence_rows = lookup(&influence, &bmu_indices, 0);
    let centroids = matmul(&influence_rows, &x, MatProp::TRANS, MatProp::NONE);

    let mut normalizer = sum(&influence_rows, 0) + 1e-8;
    normalizer = transpose(&normalizer, false);
    normalizer = tile(&normalizer, dim4!(1, centroids.dims()[1], 1, 1));
    centroids / normalizer.cast::<f32>()
}

pub fn self_organizing_map(
    x: &Array<f32>,
    units: &Array<f32>,
    iters: usize,
    sigma_initial: f32,
    batch_size: usize,
) -> Array<f32> {
    let mut centroids = sample_rows(x, units.dims()[0] as usize);
    let unit_dst = compute_distance_matrix(units, units);

    for i in 0..iters {
        let sigma = sigma_initial * (-(i as f32) / iters as f32).exp();
        let influence = exp(&(&unit_dst * &unit_dst / (-2.0 * sigma * sigma)));
        let batch = sample_rows(x, batch_size);
        let dst = compute_distance_matrix(&batch, &centroids);
        centroids = organize(&batch, &influence, &dst);
    }
    centroids
}
