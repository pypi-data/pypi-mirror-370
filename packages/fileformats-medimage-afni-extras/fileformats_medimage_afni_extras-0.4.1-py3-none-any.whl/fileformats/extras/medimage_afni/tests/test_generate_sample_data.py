import pytest
from fileformats.medimage_afni import (
    OneD,
    Dset,
    ThreeD,
    Head,
    NCorr,
    R1,
    All1,
)


@pytest.mark.xfail(reason="generate_sample_data not implemented")
def test_generate_one_d_data():
    assert isinstance(OneD.sample(), OneD)


@pytest.mark.xfail(reason="generate_sample_data not implemented")
def test_generate_three_d_data():
    assert isinstance(ThreeD.sample(), ThreeD)


@pytest.mark.xfail(reason="generate_sample_data not implemented")
def test_generate_dset_data():
    assert isinstance(Dset.sample(), Dset)


@pytest.mark.xfail(reason="generate_sample_data not implemented")
def test_generate_head_data():
    assert isinstance(Head.sample(), Head)


@pytest.mark.xfail(reason="generate_sample_data not implemented")
def test_generate_ncorr_data():
    assert isinstance(NCorr.sample(), NCorr)


@pytest.mark.xfail(reason="generate_sample_data not implemented")
def test_generate_r1_data():
    assert isinstance(R1.sample(), R1)


@pytest.mark.xfail(reason="generate_sample_data not implemented")
def test_generate_all1_data():
    assert isinstance(All1.sample(), All1)
