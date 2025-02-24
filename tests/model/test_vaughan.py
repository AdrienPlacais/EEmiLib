import numpy as np
import pandas as pd
import pytest
from eemilib.emission_data.data_matrix import DataMatrix
from eemilib.model.vaughan import Vaughan, VaughanImplementation
from pytest import approx
from tests.model.mocks.mock_emission_yield import MockEmissionYield


@pytest.fixture
def vaughan_model() -> Vaughan:
    """Create a default instance of :class:`.Vaughan` model."""
    return Vaughan()


class MockDataMatrix(DataMatrix):
    """Mock a data matrix with only a TEEY."""

    def __init__(self, emission_data):
        """Set emission yield for 'all' population."""
        self.data_matrix = [
            [None, None, None],
            [None, None, None],
            [None, None, None],
            [emission_data, None, None],
        ]

    def has_all_mandatory_files(self, *args, **kwargs) -> bool:
        """Skip this check."""
        return True


def test_initial_parameters(vaughan_model: Vaughan) -> None:
    """Check that the mandatory parameters are defined."""
    expected_parameters = {
        "E_0",
        "E_max",
        "delta_E_transition",
        "teey_low",
        "teey_max",
        "k_s",
        "k_se",
        "E_c1",
    }
    assert set(vaughan_model.initial_parameters.keys()) == expected_parameters


def test_teey_output_shape(vaughan_model: Vaughan) -> None:
    """Check that TEEY array has proper shape."""
    energy = np.linspace(0, 100, 5)
    theta = np.linspace(0, 90, 3)
    result = vaughan_model.teey(energy, theta)
    assert isinstance(result, pd.DataFrame)
    assert result.shape == (5, 4)  # 3 theta columns + 1 energy column


@pytest.mark.parametrize(
    "emission_yield,expected",
    [
        (
            MockEmissionYield.cu_eroded_one(),
            {
                "E_0": 12.5,
                "E_max": 550.5505505505506,
                "delta_E_transition": 1.0,
                "teey_low": 0.5,
                "teey_max": 1.525944944944945,
                "k_s": 1.0,
                "k_se": 1.0,
                "E_c1": 95.0950950950951,
            },
        ),
        pytest.param(
            MockEmissionYield.cu_as_received_two(),
            {
                "E_0": 12.5,
                "E_max": 250.34034034034033,
                "delta_E_transition": 1.0,
                "teey_low": 0.5,
                "teey_max": 2.236948948948949,
                "k_s": 1.0,
                "k_se": 1.0,
                "E_c1": 24.714714714714717,
            },
            marks=pytest.mark.smoke,
        ),
        (
            MockEmissionYield.cu_heated_two(),
            {
                "E_0": 12.5,
                "E_max": 389.63963963963965,
                "delta_E_transition": 1.0,
                "teey_low": 0.5,
                "teey_max": 1.695873873873874,
                "k_s": 1.0,
                "k_se": 1.0,
                "E_c1": 45.31531531531532,
            },
        ),
    ],
)
def test_find_optimal_parameters(
    vaughan_model: Vaughan,
    emission_yield: MockEmissionYield,
    expected: dict[str, float],
) -> None:
    """Test on several samples that the fit gives expected results."""
    mock_data_matrix = MockDataMatrix(emission_yield)
    vaughan_model.find_optimal_parameters(mock_data_matrix)
    found_parameters = {
        name: val.value for name, val in vaughan_model.parameters.items()
    }
    assert expected == approx(found_parameters)


# Test that the TEEY function works as expected
#   1. Give in the parameters that are already defined, compare them to
#       hard-written TEEY file
#   2. Give in the parameters that are already defined to vaughan_cst, compare
#       them to hard-written exported TEEY files
@pytest.mark.parametrize(
    "vaughan_parameters,vaughan_implementation,energy,theta,expected",
    [
        pytest.param(  # Aluminium (ECSS)
            {
                "E_c1": 23.3,
                "E_max": 150,
                "teey_low": 0.5,
                "teey_max": 2.98,
            },
            "SPARK3D",
            np.linspace(0, 1000, 501),
            np.zeros(1),
            # fmt: off
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0.17285, 0.530618, 0.746461, 0.916546, 1.06053, 1.18678, 1.29981, 1.40243, 1.49652, 1.58343, 1.66415, 1.73947, 1.81, 1.87623, 1.93859, 1.99741, 2.053, 2.1056, 2.15543, 2.20269, 2.24755, 2.29016, 2.33065, 2.36916, 2.40578, 2.44062, 2.47378, 2.50533, 2.53536, 2.56393, 2.59112, 2.61698, 2.64157, 2.66495, 2.68717, 2.70827, 2.7283, 2.7473, 2.76531, 2.78237, 2.79851, 2.81376, 2.82817, 2.84175, 2.85454, 2.86656, 2.87784, 2.8884, 2.89828, 2.90749, 2.91604, 2.92398, 2.9313, 2.93804, 2.94422, 2.94984, 2.95493, 2.9595, 2.96357, 2.96715, 2.97027, 2.97292, 2.97514, 2.97692, 2.97828, 2.97924, 2.97981, 2.98, 2.97992, 2.97968, 2.97928, 2.97873, 2.97803, 2.97719, 2.97622, 2.9751, 2.97386, 2.97249, 2.97099, 2.96938, 2.96764, 2.96579, 2.96383, 2.96176, 2.95959, 2.95731, 2.95494, 2.95246, 2.94989, 2.94723, 2.94448, 2.94164, 2.93871, 2.9357, 2.93261, 2.92944, 2.92619, 2.92287, 2.91948, 2.91601, 2.91247, 2.90886, 2.90519, 2.90145, 2.89765, 2.89379, 2.88986, 2.88588, 2.88184, 2.87775, 2.8736, 2.8694, 2.86514, 2.86084, 2.85648, 2.85208, 2.84763, 2.84314, 2.8386, 2.83402, 2.82939, 2.82472, 2.82002, 2.81527, 2.81049, 2.80566, 2.8008, 2.79591, 2.79098, 2.78602, 2.78102, 2.776, 2.77094, 2.76585, 2.76073, 2.75558, 2.75041, 2.74521, 2.73998, 2.73472, 2.72944, 2.72414, 2.71881, 2.71346, 2.70808, 2.70269, 2.69727, 2.69183, 2.68637, 2.6809, 2.6754, 2.66988, 2.66435, 2.6588, 2.65324, 2.64765, 2.64205, 2.63644, 2.63081, 2.62517, 2.61951, 2.61385, 2.60816, 2.60247, 2.59676, 2.59104, 2.58531, 2.57957, 2.57382, 2.56806, 2.56229, 2.55651, 2.55073, 2.54493, 2.53913, 2.53332, 2.5275, 2.52167, 2.51584, 2.51, 2.50416, 2.49831, 2.49245, 2.48659, 2.48072, 2.47485, 2.46898, 2.4631, 2.45722, 2.45134, 2.44545, 2.43956, 2.43367, 2.42777, 2.42188, 2.41598, 2.41008, 2.40418, 2.39827, 2.39237, 2.38647, 2.38056, 2.37466, 2.36876, 2.36285, 2.35695, 2.35105, 2.34515, 2.33925, 2.33335, 2.32745, 2.32156, 2.31566, 2.30977, 2.30388, 2.298, 2.29212, 2.28623, 2.28036, 2.27448, 2.26861, 2.26274, 2.25688, 2.25102, 2.24516, 2.23931, 2.23346, 2.22762, 2.22178, 2.21595, 2.21012, 2.20429, 2.19847, 2.19266, 2.18685, 2.18104, 2.17525, 2.16945, 2.16367, 2.15789, 2.15211, 2.14634, 2.13999, 2.1369, 2.13383, 2.13078, 2.12775, 2.12473, 2.12173, 2.11875, 2.11578, 2.11283, 2.10989, 2.10697, 2.10406, 2.10117, 2.0983, 2.09544, 2.0926, 2.08977, 2.08695, 2.08415, 2.08136, 2.07859, 2.07583, 2.07309, 2.07036, 2.06765, 2.06494, 2.06226, 2.05958, 2.05692, 2.05427, 2.05164, 2.04901, 2.0464, 2.04381, 2.04122, 2.03865, 2.03609, 2.03355, 2.03101, 2.02849, 2.02598, 2.02348, 2.02099, 2.01852, 2.01606, 2.0136, 2.01116, 2.00874, 2.00632, 2.00391, 2.00152, 1.99913, 1.99676, 1.9944, 1.99205, 1.9897, 1.98737, 1.98505, 1.98274, 1.98045, 1.97816, 1.97588, 1.97361, 1.97135, 1.9691, 1.96686, 1.96463, 1.96241, 1.9602, 1.958, 1.95581, 1.95363, 1.95146, 1.9493, 1.94714, 1.945, 1.94287, 1.94074, 1.93862, 1.93651, 1.93441, 1.93232, 1.93024, 1.92817, 1.9261, 1.92405, 1.922, 1.91996, 1.91793, 1.9159, 1.91389, 1.91188, 1.90988, 1.90789, 1.90591, 1.90394, 1.90197, 1.90001, 1.89806, 1.89612, 1.89418, 1.89225, 1.89033, 1.88842, 1.88651, 1.88462, 1.88272, 1.88084, 1.87896, 1.8771, 1.87523, 1.87338, 1.87153, 1.86969, 1.86786, 1.86603, 1.86421, 1.8624, 1.86059, 1.85879, 1.857, 1.85521, 1.85343, 1.85166, 1.84989, 1.84813, 1.84638, 1.84463, 1.84289, 1.84115, 1.83942, 1.8377, 1.83599, 1.83428, 1.83257, 1.83087, 1.82918, 1.8275, 1.82582, 1.82414, 1.82248, 1.82082, 1.81916, 1.81751, 1.81586, 1.81423, 1.81259, 1.81097, 1.80934, 1.80773, 1.80612, 1.80451, 1.80291, 1.80132, 1.79973, 1.79815, 1.79657, 1.79499, 1.79343, 1.79187, 1.79031, 1.78876, 1.78721, 1.78567, 1.78413, 1.7826, 1.78108, 1.77955, 1.77804, 1.77653, 1.77502, 1.77352, 1.77202, 1.77053, 1.76905, 1.76756, 1.76609, 1.76461, 1.76315, 1.76168, 1.76023, 1.75877, 1.75732, 1.75588, 1.75444, 1.753, 1.75157, 1.75015, 1.74872, 1.74731, 1.74589, 1.74449, 1.74308, 1.74168, 1.74029, 1.73889, 1.73751, 1.73613, 1.73475, 1.73337, 1.732, 1.73064, 1.72928, 1.72792, 1.72656, 1.72521, 1.72387, 1.72253, 1.72119, 1.71986, 1.71853, 1.7172, 1.71588, 1.71456, 1.71325, 1.71194, 1.71063, 1.70933, 1.70803, 1.70674, 1.70545, 1.70416, 1.70288, 1.7016, 1.70032, 1.69905, 1.69778, 1.69652, 1.69526, 1.694, 1.69275, 1.6915, 1.69025, 1.68901, 1.68777, 1.68653, 1.6853, 1.68407, 1.68284, 1.68162, 1.6804, 1.67918, 1.67797, 1.67676, 1.67556, 1.67436, 1.67316, 1.67196, 1.67077, 1.66958]]),
            # fmt: on
            marks=pytest.mark.implementation,
            id="Compare EEmiLib with manual SPARK3D export on Aluminium (ECSS)",
        ),
        pytest.param(  # Copper (ECSS)
            {"E_c1": 35.0, "E_max": 165, "teey_low": 0.5, "teey_max": 2.3},
            "SPARK3D",
            np.linspace(0, 1000, 501),
            np.zeros(1),
            # fmt: off
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0.11807, 0.391084, 0.553218, 0.680864, 0.788978, 0.883867, 0.96893, 1.04626, 1.11728, 1.18297, 1.24409, 1.30122, 1.35481, 1.40522, 1.45278, 1.49773, 1.54029, 1.58064, 1.61896, 1.65538, 1.69003, 1.72301, 1.75444, 1.7844, 1.81297, 1.84022, 1.86623, 1.89105, 1.91474, 1.93736, 1.95895, 1.97956, 1.99923, 2.018, 2.0359, 2.05298, 2.06926, 2.08478, 2.09956, 2.11363, 2.12702, 2.13974, 2.15183, 2.16331, 2.17419, 2.1845, 2.19425, 2.20347, 2.21217, 2.22036, 2.22807, 2.23531, 2.24209, 2.24842, 2.25433, 2.25982, 2.26491, 2.26961, 2.27392, 2.27787, 2.28145, 2.28469, 2.28759, 2.29017, 2.29242, 2.29436, 2.296, 2.29735, 2.29841, 2.2992, 2.29971, 2.29997, 2.29999, 2.29988, 2.29966, 2.29934, 2.29891, 2.29839, 2.29777, 2.29705, 2.29625, 2.29535, 2.29437, 2.29331, 2.29216, 2.29093, 2.28962, 2.28824, 2.28678, 2.28525, 2.28365, 2.28198, 2.28024, 2.27844, 2.27657, 2.27464, 2.27265, 2.2706, 2.26849, 2.26633, 2.2641, 2.26183, 2.2595, 2.25712, 2.25469, 2.25221, 2.24968, 2.2471, 2.24448, 2.24181, 2.2391, 2.23635, 2.23356, 2.23072, 2.22784, 2.22493, 2.22198, 2.21899, 2.21596, 2.2129, 2.2098, 2.20667, 2.20351, 2.20031, 2.19708, 2.19383, 2.19054, 2.18722, 2.18387, 2.1805, 2.1771, 2.17367, 2.17021, 2.16673, 2.16323, 2.1597, 2.15614, 2.15256, 2.14896, 2.14534, 2.1417, 2.13804, 2.13435, 2.13065, 2.12692, 2.12318, 2.11942, 2.11564, 2.11184, 2.10802, 2.10419, 2.10034, 2.09648, 2.0926, 2.08871, 2.0848, 2.08087, 2.07694, 2.07299, 2.06902, 2.06504, 2.06105, 2.05705, 2.05304, 2.04902, 2.04498, 2.04093, 2.03688, 2.03281, 2.02873, 2.02465, 2.02055, 2.01645, 2.01233, 2.00821, 2.00408, 1.99994, 1.9958, 1.99165, 1.98749, 1.98332, 1.97915, 1.97497, 1.97078, 1.96659, 1.9624, 1.9582, 1.95399, 1.94978, 1.94556, 1.94134, 1.93712, 1.93289, 1.92865, 1.92442, 1.92018, 1.91594, 1.91169, 1.90744, 1.90319, 1.89893, 1.89468, 1.89042, 1.88616, 1.8819, 1.87763, 1.87337, 1.8691, 1.86483, 1.86056, 1.85629, 1.85202, 1.84775, 1.84348, 1.83921, 1.83494, 1.83067, 1.82639, 1.82212, 1.81785, 1.81358, 1.80931, 1.80504, 1.80078, 1.79651, 1.79224, 1.78798, 1.78372, 1.77946, 1.7752, 1.77094, 1.76668, 1.76243, 1.75818, 1.75393, 1.74968, 1.74543, 1.74119, 1.73695, 1.73271, 1.72848, 1.72425, 1.72002, 1.71579, 1.71157, 1.70735, 1.70314, 1.69892, 1.69472, 1.69051, 1.68631, 1.68211, 1.67792, 1.67373, 1.66954, 1.66536, 1.66118, 1.657, 1.65205, 1.64981, 1.64759, 1.64538, 1.64318, 1.64099, 1.63881, 1.63665, 1.63449, 1.63235, 1.63022, 1.62809, 1.62598, 1.62388, 1.62179, 1.61971, 1.61764, 1.61558, 1.61353, 1.61149, 1.60946, 1.60744, 1.60542, 1.60342, 1.60143, 1.59945, 1.59748, 1.59551, 1.59356, 1.59162, 1.58968, 1.58775, 1.58584, 1.58393, 1.58203, 1.58014, 1.57825, 1.57638, 1.57452, 1.57266, 1.57081, 1.56897, 1.56714, 1.56532, 1.5635, 1.56169, 1.55989, 1.5581, 1.55632, 1.55454, 1.55278, 1.55102, 1.54926, 1.54752, 1.54578, 1.54405, 1.54233, 1.54062, 1.53891, 1.53721, 1.53552, 1.53383, 1.53215, 1.53048, 1.52882, 1.52716, 1.52551, 1.52386, 1.52223, 1.5206, 1.51897, 1.51736, 1.51575, 1.51414, 1.51254, 1.51095, 1.50937, 1.50779, 1.50622, 1.50465, 1.5031, 1.50154, 1.5, 1.49846, 1.49692, 1.49539, 1.49387, 1.49235, 1.49084, 1.48934, 1.48784, 1.48635, 1.48486, 1.48338, 1.4819, 1.48043, 1.47897, 1.47751, 1.47606, 1.47461, 1.47317, 1.47173, 1.4703, 1.46887, 1.46745, 1.46603, 1.46462, 1.46322, 1.46182, 1.46042, 1.45903, 1.45765, 1.45627, 1.4549, 1.45353, 1.45216, 1.4508, 1.44945, 1.4481, 1.44675, 1.44541, 1.44408, 1.44275, 1.44142, 1.4401, 1.43878, 1.43747, 1.43616, 1.43486, 1.43356, 1.43227, 1.43098, 1.42969, 1.42841, 1.42714, 1.42587, 1.4246, 1.42333, 1.42208, 1.42082, 1.41957, 1.41833, 1.41708, 1.41585, 1.41461, 1.41338, 1.41216, 1.41094, 1.40972, 1.40851, 1.4073, 1.4061, 1.40489, 1.4037, 1.4025, 1.40132, 1.40013, 1.39895, 1.39777, 1.3966, 1.39543, 1.39426, 1.3931, 1.39194, 1.39078, 1.38963, 1.38849, 1.38734, 1.3862, 1.38506, 1.38393, 1.3828, 1.38168, 1.38055, 1.37943, 1.37832, 1.37721, 1.3761, 1.37499, 1.37389, 1.37279, 1.3717, 1.37061, 1.36952, 1.36843, 1.36735, 1.36627, 1.3652, 1.36413, 1.36306, 1.36199, 1.36093, 1.35987, 1.35882, 1.35776, 1.35671, 1.35567, 1.35462, 1.35358, 1.35255, 1.35151, 1.35048, 1.34945, 1.34843, 1.34741, 1.34639, 1.34537, 1.34436, 1.34335, 1.34234, 1.34134, 1.34034, 1.33934, 1.33834, 1.33735, 1.33636, 1.33537, 1.33439, 1.33341, 1.33243, 1.33145, 1.33048, 1.32951, 1.32854, 1.32757, 1.32661, 1.32565, 1.32469, 1.32374, 1.32279, 1.32184, 1.32089]]),
            # fmt: on
            marks=pytest.mark.implementation,
            id="Compare EEmiLib with manual SPARK3D export on Copper (ECSS)",
        ),
        pytest.param(  # Silver (ECSS)
            {"E_c1": 30.0, "E_max": 165, "teey_low": 0.5, "teey_max": 2.22},
            "SPARK3D",
            np.linspace(0, 1000, 501),
            np.zeros(1),
            # fmt: off
            np.array([[0, 0, 0, 0, 0, 0, 0, 0, 0.146345, 0.3835, 0.532843, 0.651587, 0.752647, 0.841622, 0.921574, 0.994405, 1.0614, 1.12347, 1.18131, 1.23545, 1.2863, 1.33421, 1.37947, 1.4223, 1.46291, 1.50147, 1.53814, 1.57303, 1.60628, 1.63798, 1.66823, 1.69711, 1.7247, 1.75105, 1.77625, 1.80033, 1.82337, 1.8454, 1.86647, 1.88662, 1.90589, 1.92432, 1.94194, 1.95879, 1.97489, 1.99027, 2.00496, 2.01899, 2.03237, 2.04513, 2.05729, 2.06888, 2.07991, 2.09039, 2.10036, 2.10981, 2.11878, 2.12728, 2.13531, 2.1429, 2.15005, 2.15679, 2.16312, 2.16906, 2.17461, 2.17979, 2.18461, 2.18907, 2.1932, 2.19699, 2.20047, 2.20362, 2.20648, 2.20904, 2.2113, 2.21329, 2.21501, 2.21646, 2.21765, 2.21859, 2.21929, 2.21975, 2.21997, 2.21999, 2.21989, 2.2197, 2.21941, 2.21903, 2.21857, 2.21801, 2.21738, 2.21666, 2.21586, 2.21499, 2.21404, 2.21301, 2.21192, 2.21075, 2.20951, 2.20821, 2.20684, 2.20541, 2.20391, 2.20236, 2.20074, 2.19906, 2.19733, 2.19555, 2.19371, 2.19181, 2.18987, 2.18787, 2.18582, 2.18373, 2.18159, 2.1794, 2.17717, 2.17489, 2.17257, 2.17021, 2.1678, 2.16536, 2.16288, 2.16035, 2.15779, 2.1552, 2.15256, 2.1499, 2.14719, 2.14446, 2.14169, 2.13889, 2.13605, 2.13319, 2.1303, 2.12737, 2.12442, 2.12144, 2.11843, 2.1154, 2.11234, 2.10925, 2.10614, 2.103, 2.09984, 2.09666, 2.09345, 2.09022, 2.08697, 2.0837, 2.08041, 2.07709, 2.07376, 2.0704, 2.06703, 2.06364, 2.06023, 2.0568, 2.05336, 2.0499, 2.04642, 2.04292, 2.03941, 2.03589, 2.03235, 2.02879, 2.02522, 2.02164, 2.01804, 2.01443, 2.01081, 2.00717, 2.00353, 1.99987, 1.9962, 1.99251, 1.98882, 1.98511, 1.9814, 1.97768, 1.97394, 1.9702, 1.96644, 1.96268, 1.95891, 1.95513, 1.95134, 1.94755, 1.94374, 1.93993, 1.93611, 1.93229, 1.92846, 1.92462, 1.92077, 1.91692, 1.91306, 1.9092, 1.90533, 1.90146, 1.89758, 1.89369, 1.88981, 1.88591, 1.88202, 1.87811, 1.87421, 1.8703, 1.86639, 1.86247, 1.85855, 1.85463, 1.8507, 1.84677, 1.84284, 1.83891, 1.83497, 1.83104, 1.8271, 1.82316, 1.81921, 1.81527, 1.81132, 1.80737, 1.80342, 1.79948, 1.79552, 1.79157, 1.78762, 1.78367, 1.77972, 1.77576, 1.77181, 1.76786, 1.7639, 1.75995, 1.756, 1.75205, 1.7481, 1.74415, 1.7402, 1.73625, 1.7323, 1.72835, 1.72441, 1.72046, 1.71652, 1.71258, 1.70864, 1.7047, 1.70076, 1.69683, 1.6929, 1.68897, 1.68504, 1.68111, 1.67719, 1.67327, 1.66935, 1.66543, 1.66152, 1.65761, 1.6537, 1.64979, 1.64589, 1.64199, 1.63809, 1.6342, 1.63031, 1.62642, 1.62254, 1.61866, 1.61478, 1.61091, 1.60704, 1.60317, 1.59931, 1.59464, 1.59257, 1.59051, 1.58847, 1.58643, 1.5844, 1.58239, 1.58038, 1.57838, 1.57639, 1.57441, 1.57245, 1.57049, 1.56854, 1.5666, 1.56466, 1.56274, 1.56083, 1.55892, 1.55703, 1.55514, 1.55327, 1.5514, 1.54954, 1.54768, 1.54584, 1.54401, 1.54218, 1.54036, 1.53855, 1.53675, 1.53496, 1.53317, 1.53139, 1.52962, 1.52786, 1.52611, 1.52436, 1.52262, 1.52089, 1.51917, 1.51745, 1.51575, 1.51404, 1.51235, 1.51066, 1.50899, 1.50731, 1.50565, 1.50399, 1.50234, 1.5007, 1.49906, 1.49743, 1.49581, 1.49419, 1.49258, 1.49098, 1.48938, 1.48779, 1.48621, 1.48463, 1.48306, 1.4815, 1.47994, 1.47839, 1.47684, 1.4753, 1.47377, 1.47224, 1.47072, 1.46921, 1.4677, 1.4662, 1.4647, 1.46321, 1.46173, 1.46025, 1.45877, 1.45731, 1.45584, 1.45439, 1.45294, 1.45149, 1.45005, 1.44862, 1.44719, 1.44577, 1.44435, 1.44294, 1.44153, 1.44013, 1.43873, 1.43734, 1.43595, 1.43457, 1.4332, 1.43182, 1.43046, 1.4291, 1.42774, 1.42639, 1.42504, 1.4237, 1.42237, 1.42104, 1.41971, 1.41839, 1.41707, 1.41576, 1.41445, 1.41315, 1.41185, 1.41055, 1.40926, 1.40798, 1.4067, 1.40542, 1.40415, 1.40289, 1.40162, 1.40036, 1.39911, 1.39786, 1.39662, 1.39537, 1.39414, 1.39291, 1.39168, 1.39045, 1.38923, 1.38802, 1.38681, 1.3856, 1.38439, 1.38319, 1.382, 1.38081, 1.37962, 1.37844, 1.37726, 1.37608, 1.37491, 1.37374, 1.37257, 1.37141, 1.37026, 1.3691, 1.36795, 1.36681, 1.36567, 1.36453, 1.36339, 1.36226, 1.36113, 1.36001, 1.35889, 1.35777, 1.35666, 1.35555, 1.35444, 1.35334, 1.35224, 1.35115, 1.35005, 1.34897, 1.34788, 1.3468, 1.34572, 1.34464, 1.34357, 1.3425, 1.34144, 1.34037, 1.33931, 1.33826, 1.33721, 1.33616, 1.33511, 1.33407, 1.33303, 1.33199, 1.33095, 1.32992, 1.3289, 1.32787, 1.32685, 1.32583, 1.32482, 1.3238, 1.32279, 1.32179, 1.32078, 1.31978, 1.31878, 1.31779, 1.3168, 1.31581, 1.31482, 1.31384, 1.31286, 1.31188, 1.3109, 1.30993, 1.30896, 1.30799, 1.30703, 1.30607, 1.30511, 1.30416, 1.3032, 1.30225, 1.3013, 1.30036, 1.29942, 1.29848, 1.29754, 1.2966, 1.29567, 1.29474, 1.29382, 1.29289, 1.29197, 1.29105]]),
            # fmt: on
            marks=pytest.mark.implementation,
            id="Compare EEmiLib with manual SPARK3D export on Silver (ECSS)",
        ),
    ],
)
def test_teey(
    vaughan_parameters: dict[str, float],
    vaughan_implementation: VaughanImplementation,
    energy: np.ndarray,
    theta: np.ndarray,
    expected: np.ndarray,
) -> None:
    """Check the returned values of the TEEY function."""
    model = Vaughan(
        implementation=vaughan_implementation,
        parameters_values=vaughan_parameters,
    )

    calculated = model.teey(energy, theta).to_numpy().transpose()[:-1]
    assert calculated == approx(expected)
