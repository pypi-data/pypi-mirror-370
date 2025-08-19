from statistics import stdev, mean

import numpy as np
from jax.numpy import array
from more_itertools import grouper
from pytest import approx

from streamfitter.ExponentialDecay3Parameter import ExponentialDecay3ParameterFitter
from streamfitter.fitter import fit
from nef_pipelines.lib.interface import NoiseInfo, NoiseInfoSource

TIME_CONSTANT_1_3 = 1.3
AMPLITUDE_1_5 = 1.5
OFFSET = 1.0

TIME_CONSTANT_1_3_ESTIMATE_EXPECTED = 1.3097823

EXPONENTIAL_A_1_5_O_1_LAST = 1.008274846631141157
TIME_CONSTANT_ESTIMATE_1_3_INV_EXPECTED = -TIME_CONSTANT_1_3_ESTIMATE_EXPECTED
AMPLITUDE_1_5_INV_EXPECTED = -AMPLITUDE_1_5 + OFFSET
OFFSET_INV_EXPECTED = (EXPONENTIAL_A_1_5_O_1_LAST - OFFSET) * -1 + OFFSET

EXPECTED_AMPLITUDE_MC_STDEV_10ND100 = 0.085022036
EXPECTED_RATE_CONSTANT_MC_STDEV_10ND100 = 0.15636467221030487
EXPECTED_OFFSET_MC_STDEV_10ND100 = 0.06057173360160101

# 100 normally distributed values around zero with a std of 1.0
NORMALS_100 = [
    0.4967141530112327,
    -0.13826430117118466,
    0.6476885381006925,
    1.5230298564080254,
    -0.23415337472333597,
    -0.23413695694918055,
    1.5792128155073915,
    0.7674347291529088,
    -0.4694743859349521,
    0.5425600435859647,
    -0.46341769281246226,
    -0.46572975357025687,
    0.24196227156603412,
    -1.913280244657798,
    -1.7249178325130328,
    -0.5622875292409727,
    -1.0128311203344238,
    0.3142473325952739,
    -0.9080240755212109,
    -1.4123037013352915,
    1.465648768921554,
    -0.22577630048653566,
    0.06752820468792384,
    -1.4247481862134568,
    -0.5443827245251827,
    0.11092258970986608,
    -1.1509935774223028,
    0.37569801834567196,
    -0.600638689918805,
    -0.2916937497932768,
    -0.6017066122293969,
    1.8522781845089378,
    -0.013497224737933921,
    -1.0577109289559004,
    0.822544912103189,
    -1.2208436499710222,
    0.2088635950047554,
    -1.9596701238797756,
    -1.3281860488984305,
    0.19686123586912352,
    0.7384665799954104,
    0.1713682811899705,
    -0.11564828238824053,
    -0.3011036955892888,
    -1.4785219903674274,
    -0.7198442083947086,
    -0.4606387709597875,
    1.0571222262189157,
    0.3436182895684614,
    -1.763040155362734,
    0.324083969394795,
    -0.38508228041631654,
    -0.6769220003059587,
    0.6116762888408679,
    1.030999522495951,
    0.9312801191161986,
    -0.8392175232226385,
    -0.3092123758512146,
    0.33126343140356396,
    0.9755451271223592,
    -0.47917423784528995,
    -0.18565897666381712,
    -1.1063349740060282,
    -1.1962066240806708,
    0.812525822394198,
    1.356240028570823,
    -0.07201012158033385,
    1.0035328978920242,
    0.36163602504763415,
    -0.6451197546051243,
    0.36139560550841393,
    1.5380365664659692,
    -0.03582603910995154,
    1.5646436558140062,
    -2.6197451040897444,
    0.8219025043752238,
    0.08704706823817121,
    -0.2990073504658674,
    0.0917607765355023,
    -1.9875689146008928,
    -0.21967188783751193,
    0.3571125715117464,
    1.477894044741516,
    -0.5182702182736474,
    -0.8084936028931876,
    -0.5017570435845365,
    0.9154021177020741,
    0.32875110965968446,
    -0.5297602037670388,
    0.5132674331133561,
    0.09707754934804039,
    0.9686449905328892,
    -0.7020530938773524,
    -0.3276621465977682,
    -0.39210815313215763,
    -1.4635149481321186,
    0.29612027706457605,
    0.26105527217988933,
    0.00511345664246089,
    -0.23458713337514692,
]


# amplitude = 1.5 time_constant = 1.3
EXPONENTIAL_A_1_5_O_1 = array(
    [
        2.5,
        1.8417159529712340,
        1.47232383032418200,
        1.2650416686348950,
        1.14872653379473800,
        1.08345699741676420,
        1.046831390741846400,
        1.026279152458161000,
        1.014746387903064900,
        1.008274846631141157,
    ]
)

EXPONENTIAL_A_1_5_O_1_inv = array(
    [
        -0.5,
        0.158284047,
        0.52767617,
        0.734958331,
        0.851273466,
        0.916543003,
        0.953168609,
        0.973720848,
        0.985253612,
        0.991725153,
    ]
)

XS = np.linspace(0, 4, 10)


def test_exponential_estimator():
    instance = ExponentialDecay3ParameterFitter()
    result = instance.estimate(XS, EXPONENTIAL_A_1_5_O_1)

    assert approx(AMPLITUDE_1_5 + OFFSET - EXPONENTIAL_A_1_5_O_1_LAST) == result['amplitude']
    assert approx(EXPONENTIAL_A_1_5_O_1[-1]) == result['offset']
    assert approx(TIME_CONSTANT_1_3_ESTIMATE_EXPECTED) == result['time_constant']


def test_exponential_function():
    instance = ExponentialDecay3ParameterFitter()
    result = instance.function(AMPLITUDE_1_5, TIME_CONSTANT_1_3, OFFSET, XS)

    assert approx(EXPONENTIAL_A_1_5_O_1) == result


def test_fitter_with_exponential():
    key = 1

    # this forces the fitter to do some work as the guess
    # of the initial amplitude will be off as it just uses the largest
    # values in the ys
    ys = EXPONENTIAL_A_1_5_O_1[1:]
    xs = XS[1:]

    id_xy_data = {key: [xs, ys]}

    fitter = ExponentialDecay3ParameterFitter()
    result = fit(fitter, id_xy_data, None, None, 42)

    estimates = result['estimates'][key]

    # this proves that the fitter is doing the work and not the stimator
    estimated_amplitude = estimates['amplitude']
    estimated_time_constant = estimates['time_constant']
    estimated_offset = estimates['offset']

    assert approx(AMPLITUDE_1_5) != estimated_time_constant
    assert approx(TIME_CONSTANT_1_3) != estimated_amplitude
    assert approx(OFFSET) != estimated_offset

    fits = result['fits'][key]
    amplitude = fits.params['amplitude']
    time_constant = fits.params['time_constant']
    offset = fits.params['offset']

    assert approx(AMPLITUDE_1_5) == amplitude
    assert approx(TIME_CONSTANT_1_3) == time_constant
    assert approx(OFFSET) == offset


def test_exponential_estimator_inv():
    instance = ExponentialDecay3ParameterFitter()
    result = instance.estimate(XS, EXPONENTIAL_A_1_5_O_1_inv)

    assert approx(-(AMPLITUDE_1_5 + OFFSET - EXPONENTIAL_A_1_5_O_1_LAST)) == result['amplitude']
    assert approx(OFFSET_INV_EXPECTED) == result['offset']
    assert approx(TIME_CONSTANT_1_3_ESTIMATE_EXPECTED) == result['time_constant']


def test_exponential_function_inv():
    instance = ExponentialDecay3ParameterFitter()
    result = instance.function(-AMPLITUDE_1_5, TIME_CONSTANT_1_3, OFFSET, XS)

    assert approx(EXPONENTIAL_A_1_5_O_1_inv) == result


def test_fitter_with_exponential_inv():
    key = 1

    # this forces the fitter to do some work as the guess
    # of the initial amplitude will be off as it just uses the largest
    # values in the ys
    ys = EXPONENTIAL_A_1_5_O_1_inv[1:]
    xs = XS[1:]

    id_xy_data = {key: [xs, ys]}

    fitter = ExponentialDecay3ParameterFitter()
    result = fit(fitter, id_xy_data, None, None, 42)

    estimates = result['estimates'][key]

    # this proves that the fitter is doing the work and not the stimator
    estimated_amplitude = estimates['amplitude']
    estimated_time_constant = estimates['time_constant']
    estimated_offset = estimates['offset']

    assert approx(AMPLITUDE_1_5) != estimated_amplitude
    assert approx(TIME_CONSTANT_1_3) != estimated_time_constant
    assert approx(OFFSET) != estimated_offset

    fits = result['fits'][key]
    amplitude = fits.params['amplitude']
    time_constant = fits.params['time_constant']
    offset = fits.params['offset']

    assert approx(AMPLITUDE_1_5) == -amplitude
    assert approx(TIME_CONSTANT_1_3) == time_constant
    assert approx(OFFSET) == offset


def test_fitter_with_montecarlo_10_cycles():
    """Test ExponentialDecay3ParameterFitter with 10 Monte Carlo cycles using patched random values."""
    key = 1

    # Use subset of data to force fitter to work
    ys = EXPONENTIAL_A_1_5_O_1
    xs = XS

    id_xy_data = {key: [xs, ys]}

    # # Create a side_effect function that returns the pre-computed NORMALS_10 values
    # def mock_normal_side_effect(*args, **kwargs):
    #     mock_result = np.array(NORMALS_100[:args[1]])  # Return the requested size
    #     print(mock_result)
    #     return mock_result

    np.random.seed(24)

    fitter = ExponentialDecay3ParameterFitter()

    noise_info = NoiseInfo(NoiseInfoSource.CLI, 1.0 / 10.0)

    # with patch('numpy.random.normal', side_effect=mock_normal_side_effect):
    result = fit(fitter, id_xy_data, 10, noise_info)

    # Verify Monte Carlo results are present
    assert 'monte_carlo_errors' in result
    assert 'monte_carlo_value_stats' in result
    assert 'monte_carlo_param_values' in result

    # Verify the fit still works correctly
    fits = result['fits'][key]
    amplitude = fits.params['amplitude']
    time_constant = fits.params['time_constant']
    offset = fits.params['offset']

    assert approx(AMPLITUDE_1_5, rel=0.1) == amplitude
    assert approx(TIME_CONSTANT_1_3, rel=0.1) == time_constant
    assert approx(OFFSET, rel=0.1) == offset

    mc_error_amplitude = result['monte_carlo_errors'][1]['amplitude_mc_error']
    mc_error_rate_constant = result['monte_carlo_errors'][1]['time_constant_mc_error']
    mc_error_offset = result['monte_carlo_errors'][1]['offset_mc_error']

    assert mc_error_amplitude == approx(EXPECTED_AMPLITUDE_MC_STDEV_10ND100)
    assert mc_error_rate_constant == approx(EXPECTED_RATE_CONSTANT_MC_STDEV_10ND100)
    assert mc_error_offset == approx(EXPECTED_OFFSET_MC_STDEV_10ND100)


def setup_exponentials():
    NORMALS_100_D10 = list(array(NORMALS_100) / 10.0)

    amplitudes = []
    rate_constants = []
    offsets = []
    for i, normals in enumerate(grouper(NORMALS_100_D10, 10)):
        xs = XS

        ys = EXPONENTIAL_A_1_5_O_1 + array(normals)

        key = 1

        id_xy_data = {key: [xs, ys]}

        fitter = ExponentialDecay3ParameterFitter()
        result = fit(fitter, id_xy_data, None, None, 42)

        fits = result['fits'][key]
        amplitude = fits.params['amplitude'].value
        time_constant = fits.params['time_constant'].value
        offset = fits.params['offset'].value

        amplitudes.append(amplitude)
        rate_constants.append(time_constant)
        offsets.append(offset)

        print(f'round: {i+1}')
        out_normals = [float(value) for value in normals]
        print(f'normals: {out_normals}')
        out_ys = [float(value) for value in ys]
        print(f'ys: {out_ys}')
        print(f'fit round {i+1}: amplitude: {amplitude} rate: {time_constant} offset: {offset}')
        print()
    print(
        f'overall mean: {mean(amplitudes)} ± {stdev(amplitudes)}  rate: {mean(rate_constants)} ± {stdev(rate_constants)} offset: {mean(offsets)} ± {stdev(offsets)}'
    )


# fits
#
# round: 1
# normals: [0.049671415239572525, -0.013826429843902588, 0.06476885825395584, 0.15230298042297363, -0.02341533824801445, -0.02341369539499283, 0.15792128443717957, 0.0767434686422348, -0.04694743826985359, 0.054256003350019455]
# fit round 1: amplitude: 1.488873677460864 rate: 1.2696248225244402 offset: 1.0415063419800414
#
# round: 2
# normals: [-0.04634176939725876, -0.0465729758143425, 0.02419622614979744, -0.1913280189037323, -0.17249178886413574, -0.056228749454021454, -0.10128311067819595, 0.031424734741449356, -0.09080240875482559, -0.14123037457466125]
# fit round 2: amplitude: 1.5599852943867025 rate: 1.308721700407779 offset: 0.9090115461245496
#
# round: 3
# normals: [0.14656487107276917, -0.02257763035595417, 0.00675282021984458, -0.14247481524944305, -0.0544382743537426, 0.011092258617281914, -0.11509935557842255, 0.0375698022544384, -0.06006386876106262, -0.029169375076889992]
# fit round 3: amplitude: 1.670928149531788 rate: 1.4982564484322234 offset: 0.9753146014085936
#
# round: 4
# normals: [-0.06017066165804863, 0.18522782623767853, -0.0013497225008904934, -0.10577108711004257, 0.08225449174642563, -0.1220843642950058, 0.020886359736323357, -0.19596700370311737, -0.13281860947608948, 0.019686123356223106]
# fit round 4: amplitude: 1.6051151854391288 rate: 1.0563695784179525 offset: 0.8852528719695714
#
# round: 5
# normals: [0.07384665310382843, 0.01713682897388935, -0.01156482845544815, -0.030110368505120277, -0.14785219728946686, -0.0719844251871109, -0.046063877642154694, 0.10571222007274628, 0.034361831843853, -0.17630401253700256]
# fit round 5: amplitude: 1.6220289450424172 rate: 1.3726649639266961 offset: 0.9610820637300653
#
# round: 6
# normals: [0.032408397644758224, -0.038508228957653046, -0.06769220530986786, 0.061167627573013306, 0.10309995710849762, 0.0931280106306076, -0.08392175287008286, -0.030921239405870438, 0.0331263430416584, 0.097554512321949]
# fit round 6: amplitude: 1.4699192961723344 rate: 1.4178846393894948 offset: 1.0468384996207267
#
# round: 7
# normals: [-0.04791742190718651, -0.018565896898508072, -0.1106334924697876, -0.1196206584572792, 0.0812525823712349, 0.1356240063905716, -0.007201012223958969, 0.10035328567028046, 0.03616360202431679, -0.0645119696855545]
# fit round 7: amplitude: 1.4089209264258449 rate: 1.5140999806816675 offset: 1.051917683201568
#
# round: 8
# normals: [0.036139559000730515, 0.15380366146564484, -0.0035826037637889385, 0.1564643681049347, -0.2619745135307312, 0.08219025284051895, 0.008704707026481628, -0.02990073524415493, 0.00917607732117176, -0.1987568885087967]
# fit round 8: amplitude: 1.6499791975203777 rate: 1.081673631928029 offset: 0.9071998015443377
#
# round: 9
# normals: [-0.021967189386487007, 0.03571125492453575, 0.14778940379619598, -0.051827020943164825, -0.08084936439990997, -0.050175704061985016, 0.09154020994901657, 0.03287511318922043, -0.05297601968050003, 0.05132674425840378]
# fit round 9: amplitude: 1.5045777359800385 rate: 1.2184175748391917 offset: 0.9926555604835278
#
# round: 10
# normals: [0.009707754477858543, 0.0968644991517067, -0.07020530849695206, -0.03276621550321579, -0.039210814982652664, -0.14635148644447327, 0.02961202897131443, 0.026105526834726334, 0.000511345686390996, -0.02345871366560459]
# fit round 10: amplitude: 1.5638919394683453 rate: 1.3412620256591399 offset: 0.9784534338317467
#
# overall mean: 1.5544220347427842 ± 0.08502175639954061  rate: 1.3078975366206613 ± 0.15637449602000494 offset: 0.9749232403894728 ± 0.06057454315921634


def build_normals():
    import numpy as np

    np.random.seed(42)

    results = []

    for i in range(100):
        results.append(np.random.normal(0.0, 1.0))

    print(results)
