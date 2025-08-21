import pathlib
import pytest
import numpy
import h5py
from dh5io import DH5File
from dh5io import DH5Error
from dh5io.validation import validate_dh5_file
from dh5io.cont import Cont
from dh5io.trialmap import Trialmap

filename = pathlib.Path(__file__).parent / "test.dh5"


@pytest.fixture
def test_file() -> DH5File:
    return DH5File(filename)


dh5 = DH5File("tests/test.dh5", mode="r")


class TestDH5File:
    def test_load(self, test_file: DH5File):
        print(test_file)

    def test_get_version(self, test_file):
        assert test_file.version == 2


class TestDH5FileCont:
    def test_get_cont_groups(self, test_file: DH5File):
        contGroups = test_file.get_cont_groups()
        assert len(contGroups) == 7
        assert all([isinstance(cont, Cont) for cont in contGroups])

    def test_get_cont_group_names(self, test_file: DH5File):
        contNames = test_file.get_cont_group_names()
        assert len(contNames) == 7
        assert contNames == [
            "CONT1",
            "CONT60",
            "CONT61",
            "CONT62",
            "CONT63",
            "CONT64",
            "CONT1001",
        ]

    def test_get_cont_group_ids(self, test_file: DH5File):
        contIds = test_file.get_cont_group_ids()
        assert len(contIds) == 7
        assert contIds == [1, 60, 61, 62, 63, 64, 1001]

    def test_get_cont_group_by_id(self, test_file: DH5File):
        contGroup = test_file.get_cont_group_by_id(1)
        assert isinstance(contGroup, Cont)
        assert contGroup.id == 1
        # expect an DH5Error if the group does not exist
        with pytest.raises(DH5Error):
            test_file.get_cont_group_by_id(99999)

    def test_get_cont_data_by_id(self, test_file: DH5File):
        contData = test_file.get_cont_data_by_id(1)
        assert isinstance(contData, numpy.ndarray)

    def test_get_calibrated_cont_data_by_id(self, test_file: DH5File):
        contData = test_file.get_calibrated_cont_data_by_id(1)
        assert contData.dtype == numpy.float64

    def test_validate_existing_dh5_file(self, test_file: DH5File):
        validate_dh5_file(filename)


class TestDH5FileSpike:
    # spike groups
    def test_get_spike_groups(self, test_file: DH5File):
        spikeGroups = test_file.get_spike_groups()
        assert len(spikeGroups) == 1
        assert all([isinstance(spike, h5py.Group) for spike in spikeGroups])

    def test_get_spike_group_names(self, test_file: DH5File):
        spikeNames = test_file.get_spike_group_names()
        assert len(spikeNames) == 1
        assert spikeNames == ["SPIKE0"]

    def test_get_spike_group_by_id(self, test_file: DH5File):
        spikeGroup = test_file.get_spike_group_by_id(0)
        assert isinstance(spikeGroup, h5py.Group)
        assert spikeGroup.name == "/SPIKE0"
        assert test_file.get_spike_group_by_id(99999) is None


class TestDH5FileEvent:
    def test_get_events(self, test_file: DH5File):
        events = test_file.get_events_dataset()
        assert events is not None
        assert events.shape == (10460,)
        assert isinstance(events, h5py.Dataset)
        assert events.name == "/EV02"
        for event in events:
            assert len(event) == 2


class TestDH5FileTrialmap:
    def test_get_trialmap(self, test_file: DH5File):
        trialmap = test_file.get_trialmap()
        assert isinstance(trialmap, Trialmap)
        assert trialmap is not None
        assert trialmap.recarray.shape == (385,)
        # assert trialmap.name == "/TRIALMAP"
        assert len(trialmap.recarray.dtype) == 5
        assert trialmap.recarray.dtype.names == (
            "TrialNo",
            "StimNo",
            "Outcome",
            "StartTime",
            "EndTime",
        )

        # test properties
        assert len(trialmap) == 385
