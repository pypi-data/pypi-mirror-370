use numpy::{PyReadonlyArray1, PyReadonlyArray2, PyUntypedArrayMethods};
use pyo3::prelude::PyModuleMethods;
use pyo3::Python;

pub fn add_functions(
    _py: pyo3::Python,
    m: &pyo3::Bound<pyo3::types::PyModule>,
) -> pyo3::PyResult<()> {
    use pyo3::wrap_pyfunction;
    m.add_function(wrap_pyfunction!(optimal_rotations_arap_spoke, m)?)?;
    m.add_function(wrap_pyfunction!(residual_arap_spoke, m)?)?;
    m.add_function(wrap_pyfunction!(
        optimal_rotations_arap_spoke_rim_trimesh3,
        m
    )?)?;
    m.add_function(wrap_pyfunction!(residual_arap_spoke_rim_trimesh3, m)?)?;
    Ok(())
}

#[pyo3::pyfunction]
pub fn optimal_rotations_arap_spoke<'a>(
    _py: Python<'a>,
    vtx2xyz_ini: PyReadonlyArray2<'a, f64>,
    vtx2xyz_def: PyReadonlyArray2<'a, f64>,
    vtx2idx: PyReadonlyArray1<'a, usize>,
    idx2vtx: PyReadonlyArray1<'a, usize>,
    idx2val: PyReadonlyArray1<'a, f64>,
    mut vtx2rot: numpy::PyReadwriteArray3<'a, f64>,
) {
    use del_geo_core::mat3_col_major::Mat3ColMajor;
    assert!(vtx2xyz_ini.is_c_contiguous());
    let num_vtx = vtx2xyz_ini.shape()[0];
    assert_eq!(vtx2xyz_ini.shape(), [num_vtx, 3]);
    assert!(vtx2xyz_def.is_c_contiguous());
    assert_eq!(vtx2xyz_ini.shape(), vtx2xyz_def.shape());
    assert!(vtx2idx.is_c_contiguous());
    assert_eq!(vtx2idx.shape(), [num_vtx + 1]);
    assert!(idx2vtx.is_c_contiguous());
    assert!(idx2val.is_c_contiguous());
    assert!(vtx2rot.is_c_contiguous());
    assert_eq!(vtx2rot.shape(), [num_vtx, 3, 3]);
    let vtx2xyz_ini = vtx2xyz_ini.as_slice().unwrap();
    let vtx2xyz_def = vtx2xyz_def.as_slice().unwrap();
    let vtx2idx = vtx2idx.as_slice().unwrap();
    let idx2col = idx2vtx.as_slice().unwrap();
    let idx2val = idx2val.as_slice().unwrap();
    let vtx2rot = vtx2rot.as_slice_mut().unwrap();
    for i_vtx in 0..num_vtx {
        let adj2vtx = &idx2col[vtx2idx[i_vtx]..vtx2idx[i_vtx + 1]];
        let adj2weight = &idx2val[vtx2idx[i_vtx]..vtx2idx[i_vtx + 1]];
        let rot = del_fem_cpu::arap::optimal_rotation_for_arap_spoke(
            i_vtx,
            adj2vtx,
            vtx2xyz_ini,
            vtx2xyz_def,
            adj2weight,
            -1.,
        );
        // transpose to change column-major to row-major
        rot.transpose()
            .iter()
            .enumerate()
            .for_each(|(i, &v)| vtx2rot[i_vtx * 9 + i] = v);
    }
}

#[pyo3::pyfunction]
#[allow(clippy::too_many_arguments)]
pub fn residual_arap_spoke<'a>(
    _py: Python<'a>,
    vtx2xyz_ini: PyReadonlyArray2<'a, f64>,
    vtx2xyz_def: PyReadonlyArray2<'a, f64>,
    vtx2idx: PyReadonlyArray1<'a, usize>,
    idx2vtx: PyReadonlyArray1<'a, usize>,
    idx2val: PyReadonlyArray1<'a, f64>,
    vtx2rot: numpy::PyReadonlyArray3<'a, f64>,
    mut vtx2res: numpy::PyReadwriteArray2<'a, f64>,
) {
    use del_geo_core::mat3_col_major::Mat3ColMajor;
    use del_geo_core::vec3::Vec3;
    assert!(vtx2xyz_ini.is_c_contiguous());
    let num_vtx = vtx2xyz_ini.shape()[0];
    assert!(vtx2xyz_def.is_c_contiguous());
    assert_eq!(vtx2xyz_ini.shape(), [num_vtx, 3]);
    assert_eq!(vtx2xyz_ini.shape(), vtx2xyz_def.shape());
    assert!(vtx2idx.is_c_contiguous());
    assert!(idx2vtx.is_c_contiguous());
    assert!(idx2val.is_c_contiguous());
    assert!(vtx2rot.is_c_contiguous());
    assert_eq!(vtx2rot.shape(), [num_vtx, 3, 3]);
    let vtx2xyz_ini = vtx2xyz_ini.as_slice().unwrap();
    let vtx2xyz_def = vtx2xyz_def.as_slice().unwrap();
    let vtx2idx = vtx2idx.as_slice().unwrap();
    let idx2col = idx2vtx.as_slice().unwrap();
    let idx2val = idx2val.as_slice().unwrap();
    let vtx2rot = vtx2rot.as_slice().unwrap();
    let vtx2res = vtx2res.as_slice_mut().unwrap();
    vtx2res.fill(0.);
    for i_vtx in 0..num_vtx {
        let r_i = arrayref::array_ref!(&vtx2rot, i_vtx * 9, 9);
        let p_i = del_msh_cpu::vtx2xyz::to_vec3(vtx2xyz_ini, i_vtx);
        let q_i = del_msh_cpu::vtx2xyz::to_vec3(vtx2xyz_def, i_vtx);
        let adj2vtx = &idx2col[vtx2idx[i_vtx]..vtx2idx[i_vtx + 1]];
        let adj2weight = &idx2val[vtx2idx[i_vtx]..vtx2idx[i_vtx + 1]];
        for (&j_vtx, &w) in adj2vtx.iter().zip(adj2weight.iter()) {
            let r_j = arrayref::array_ref![&vtx2rot, j_vtx * 9, 9];
            let p_j = del_msh_cpu::vtx2xyz::to_vec3(vtx2xyz_ini, j_vtx);
            let q_j = del_msh_cpu::vtx2xyz::to_vec3(vtx2xyz_def, j_vtx);
            let rm = r_i.add(r_j).scale(0.5);
            let r = q_i.sub(q_j).sub(&rm.mult_vec(&p_i.sub(p_j)));
            let r = r.scale(w);
            vtx2res[i_vtx * 3] += r[0];
            vtx2res[i_vtx * 3 + 1] += r[1];
            vtx2res[i_vtx * 3 + 2] += r[2];
        }
    }
}

#[pyo3::pyfunction]
pub fn optimal_rotations_arap_spoke_rim_trimesh3<'a>(
    _py: Python<'a>,
    tri2vtx: PyReadonlyArray2<'a, usize>,
    vtx2xyz_ini: PyReadonlyArray2<'a, f64>,
    vtx2xyz_def: PyReadonlyArray2<'a, f64>,
    mut vtx2rot: numpy::PyReadwriteArray3<'a, f64>,
) {
    assert!(tri2vtx.is_c_contiguous());
    assert_eq!(tri2vtx.shape().len(), 2);
    assert_eq!(tri2vtx.shape()[1], 3);
    assert!(vtx2xyz_ini.is_c_contiguous());
    assert!(vtx2xyz_def.is_c_contiguous());
    assert_eq!(vtx2xyz_ini.shape(), vtx2xyz_def.shape());
    assert_eq!(vtx2xyz_ini.shape().len(), 2);
    assert_eq!(vtx2xyz_ini.shape()[1], 3);
    assert!(vtx2rot.is_c_contiguous());
    assert_eq!(vtx2rot.shape().len(), 3);
    assert_eq!(vtx2rot.shape()[1], 3);
    assert_eq!(vtx2rot.shape()[2], 3);
    let tri2vtx = tri2vtx.as_slice().unwrap();
    let vtx2xyz_ini = vtx2xyz_ini.as_slice().unwrap();
    let vtx2xyz_def = vtx2xyz_def.as_slice().unwrap();
    let vtx2rot = vtx2rot.as_slice_mut().unwrap();
    del_fem_cpu::arap::optimal_rotations_mesh_vertx_for_arap_spoke_rim(
        vtx2rot,
        tri2vtx,
        vtx2xyz_ini,
        vtx2xyz_def,
    );
}

#[pyo3::pyfunction]
pub fn residual_arap_spoke_rim_trimesh3<'a>(
    _py: Python<'a>,
    tri2vtx: PyReadonlyArray2<'a, usize>,
    vtx2xyz_ini: PyReadonlyArray2<'a, f64>,
    vtx2xyz_def: PyReadonlyArray2<'a, f64>,
    vtx2rot: numpy::PyReadonlyArray3<'a, f64>,
    mut vtx2res: numpy::PyReadwriteArray2<'a, f64>,
) {
    assert!(tri2vtx.is_c_contiguous());
    assert_eq!(tri2vtx.shape().len(), 2);
    assert_eq!(tri2vtx.shape()[1], 3);
    assert!(vtx2xyz_ini.is_c_contiguous());
    assert!(vtx2xyz_def.is_c_contiguous());
    assert_eq!(vtx2xyz_ini.shape(), vtx2xyz_def.shape());
    assert_eq!(vtx2xyz_ini.shape().len(), 2);
    assert_eq!(vtx2xyz_ini.shape()[1], 3);
    assert!(vtx2rot.is_c_contiguous());
    assert_eq!(vtx2rot.shape().len(), 3);
    assert_eq!(vtx2rot.shape()[1], 3);
    assert_eq!(vtx2rot.shape()[2], 3);
    let tri2vtx = tri2vtx.as_slice().unwrap();
    let vtx2xyz_ini = vtx2xyz_ini.as_slice().unwrap();
    let vtx2xyz_def = vtx2xyz_def.as_slice().unwrap();
    let vtx2rot = vtx2rot.as_slice().unwrap();
    let vtx2res = vtx2res.as_slice_mut().unwrap();
    del_fem_cpu::arap::residual_arap_spoke_rim(vtx2res, tri2vtx, vtx2xyz_ini, vtx2xyz_def, vtx2rot);
}
