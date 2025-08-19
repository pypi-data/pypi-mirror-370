use numpy::{PyReadonlyArray1, PyReadonlyArray2, PyUntypedArrayMethods};
use pyo3::Python;

pub fn add_functions(
    _py: pyo3::Python,
    m: &pyo3::Bound<pyo3::types::PyModule>,
) -> pyo3::PyResult<()> {
    use pyo3::types::PyModuleMethods;
    m.add_function(pyo3::wrap_pyfunction!(
        merge_linear_solid_to_bsr_for_meshtri2,
        m
    )?)?;
    Ok(())
}

#[pyo3::pyfunction]
fn merge_linear_solid_to_bsr_for_meshtri2<'a>(
    _py: Python<'a>,
    tri2vtx: PyReadonlyArray2<'a, usize>,
    vtx2xy: PyReadonlyArray2<'a, f32>,
    row2idx: PyReadonlyArray1<'a, usize>,
    idx2col: PyReadonlyArray1<'a, usize>,
    mut idx2val: numpy::PyReadwriteArray3<'a, f32>,
) {
    let num_vtx = vtx2xy.shape()[0];
    assert_eq!(idx2val.shape(), [idx2col.shape()[0], 2, 2]);
    let tri2vtx = tri2vtx.as_slice().unwrap();
    let vtx2xy = vtx2xy.as_slice().unwrap();
    let row2idx = row2idx.as_slice().unwrap();
    let idx2col = idx2col.as_slice().unwrap();
    let idx2val = idx2val.as_slice_mut().unwrap();
    let mut buffer = vec![usize::MAX, num_vtx];
    for node2vtx in tri2vtx.chunks(3) {
        let node2vtx = arrayref::array_ref!(node2vtx, 0, 3);
        let (i0, i1, i2) = (node2vtx[0], node2vtx[1], node2vtx[2]);
        let p0 = arrayref::array_ref!(vtx2xy, i0 * 2, 2);
        let p1 = arrayref::array_ref!(vtx2xy, i1 * 2, 2);
        let p2 = arrayref::array_ref!(vtx2xy, i2 * 2, 2);
        let ddw = del_fem_cpu::solid_linear_tri2::emat_tri2(1.0, 1.0, p0, p1, p2);
        del_fem_cpu::merge::blkcsr::<f32, 4, 3>(
            node2vtx,
            node2vtx,
            &ddw,
            row2idx,
            idx2col,
            idx2val,
            &mut buffer,
        );
    }
}
