import numpy as np

def test_shapes(systems, filtered):
    assert systems.shape == (9, 495, 495)
    assert filtered.shape == (9, 230, 230)

def test_headers_symmetric_andnonneg(systems):
    header_row = systems[0, 0, 1:]
    header_col = systems[0, 1:, 0]
    np.testing.assert_array_equal(header_row, header_col, err_msg="indices dont match")
    mat = systems[:, 1:, 1:]
    assert np.all(mat >= 0)
    assert np.allclose(mat, np.swapaxes(mat, 1, 2))
    assert np.all(np.diagonal(mat, axis1=1, axis2=2) == 0)

def test_filtered_integrity(filtered):
    filtered_header = filtered[0, 0, 1:]
    filtered_colheader = filtered[0, 1:, 0]
    np.testing.assert_array_equal(filtered_header, filtered_colheader, err_msg="indices dont match")
    fmat = filtered[:, 1:, 1:]
    assert np.all(fmat >= 0)
    assert np.allclose(fmat, np.swapaxes(fmat, 1, 2))
    assert np.all(np.diagonal(fmat, axis1=1, axis2=2) == 0)
