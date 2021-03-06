# 
#         turku
#                   www.fabiocrameri.ch/visualisation
from matplotlib.colors import LinearSegmentedColormap      
      
cm_data = [[0.00013469, 1.3089e-05, 0],      
           [0.007304, 0.0071474, 0.0069296],      
           [0.014669, 0.014477, 0.014097],      
           [0.021841, 0.021609, 0.021059],      
           [0.029015, 0.028742, 0.028016],      
           [0.03638, 0.036075, 0.035155],      
           [0.043349, 0.043006, 0.042092],      
           [0.049942, 0.049613, 0.048439],      
           [0.055937, 0.055539, 0.054279],      
           [0.061441, 0.061057, 0.059847],      
           [0.066729, 0.066308, 0.064895],      
           [0.071687, 0.071262, 0.069753],      
           [0.076301, 0.075847, 0.074281],      
           [0.080798, 0.080296, 0.078552],      
           [0.085057, 0.08458, 0.082728],      
           [0.089172, 0.088623, 0.086691],      
           [0.09306, 0.092508, 0.090478],      
           [0.096976, 0.096335, 0.094139],      
           [0.10093, 0.10024, 0.097793],      
           [0.10487, 0.10413, 0.1014],      
           [0.10889, 0.10803, 0.10502],      
           [0.11293, 0.112, 0.10868],      
           [0.11691, 0.11594, 0.11236],      
           [0.12093, 0.11986, 0.11599],      
           [0.12502, 0.12382, 0.11959],      
           [0.1291, 0.12783, 0.12318],      
           [0.13322, 0.13183, 0.1268],      
           [0.13736, 0.1358, 0.13045],      
           [0.1415, 0.13982, 0.13401],      
           [0.14567, 0.14389, 0.13759],      
           [0.14984, 0.14792, 0.14114],      
           [0.154, 0.15196, 0.14466],      
           [0.15823, 0.15605, 0.14815],      
           [0.16246, 0.16007, 0.15164],      
           [0.1667, 0.16419, 0.15511],      
           [0.17094, 0.16824, 0.15858],      
           [0.17522, 0.17233, 0.162],      
           [0.17949, 0.17641, 0.16535],      
           [0.18378, 0.18052, 0.16876],      
           [0.18812, 0.18464, 0.17208],      
           [0.19241, 0.18874, 0.17539],      
           [0.19676, 0.19284, 0.17869],      
           [0.20106, 0.19697, 0.18191],      
           [0.20543, 0.20104, 0.18517],      
           [0.20979, 0.20517, 0.18836],      
           [0.21416, 0.20928, 0.19148],      
           [0.21853, 0.21339, 0.19464],      
           [0.22292, 0.21751, 0.1977],      
           [0.2273, 0.22161, 0.20074],      
           [0.2317, 0.22573, 0.2038],      
           [0.23609, 0.22981, 0.2068],      
           [0.24046, 0.23392, 0.20973],      
           [0.24487, 0.23803, 0.21266],      
           [0.24929, 0.24213, 0.21556],      
           [0.25371, 0.24621, 0.21842],      
           [0.25811, 0.2503, 0.22126],      
           [0.26255, 0.25441, 0.22403],      
           [0.26696, 0.25848, 0.22682],      
           [0.27139, 0.26257, 0.22954],      
           [0.27584, 0.26665, 0.23227],      
           [0.28025, 0.27074, 0.23497],      
           [0.28468, 0.2748, 0.23762],      
           [0.28913, 0.27888, 0.24022],      
           [0.29356, 0.28295, 0.24283],      
           [0.298, 0.287, 0.24541],      
           [0.30244, 0.29108, 0.248],      
           [0.3069, 0.29514, 0.25051],      
           [0.31135, 0.29922, 0.25304],      
           [0.31582, 0.30326, 0.25554],      
           [0.32028, 0.30733, 0.25801],      
           [0.32472, 0.3114, 0.26049],      
           [0.32921, 0.31547, 0.26294],      
           [0.33368, 0.31954, 0.26537],      
           [0.33814, 0.3236, 0.26777],      
           [0.34264, 0.32766, 0.27021],      
           [0.34713, 0.33174, 0.27259],      
           [0.3516, 0.33581, 0.27498],      
           [0.35611, 0.3399, 0.27737],      
           [0.3606, 0.34396, 0.27974],      
           [0.36512, 0.34805, 0.28211],      
           [0.36964, 0.35213, 0.28445],      
           [0.37418, 0.35623, 0.28679],      
           [0.37871, 0.36032, 0.28916],      
           [0.38326, 0.36442, 0.2915],      
           [0.3878, 0.36853, 0.29383],      
           [0.39237, 0.37263, 0.29617],      
           [0.39693, 0.37676, 0.29851],      
           [0.40152, 0.38089, 0.30084],      
           [0.40613, 0.385, 0.30318],      
           [0.41073, 0.38914, 0.30554],      
           [0.41534, 0.39328, 0.30786],      
           [0.41998, 0.39743, 0.31022],      
           [0.42462, 0.40158, 0.31255],      
           [0.42928, 0.40575, 0.3149],      
           [0.43395, 0.40992, 0.31726],      
           [0.43864, 0.41408, 0.31963],      
           [0.44335, 0.41826, 0.32199],      
           [0.44807, 0.42245, 0.32436],      
           [0.45283, 0.42665, 0.32674],      
           [0.45758, 0.43086, 0.32915],      
           [0.46237, 0.43507, 0.33153],      
           [0.46719, 0.43927, 0.33395],      
           [0.47202, 0.4435, 0.33635],      
           [0.47688, 0.44772, 0.33879],      
           [0.48177, 0.45197, 0.34124],      
           [0.48668, 0.4562, 0.34369],      
           [0.49164, 0.46044, 0.34615],      
           [0.4966, 0.4647, 0.34865],      
           [0.50163, 0.46895, 0.35116],      
           [0.50667, 0.4732, 0.35366],      
           [0.51175, 0.47746, 0.35621],      
           [0.51689, 0.48172, 0.35875],      
           [0.52205, 0.48598, 0.36134],      
           [0.52727, 0.49024, 0.36393],      
           [0.53253, 0.4945, 0.36656],      
           [0.53784, 0.49875, 0.3692],      
           [0.54319, 0.50299, 0.37186],      
           [0.5486, 0.50723, 0.37456],      
           [0.55405, 0.51145, 0.37727],      
           [0.55956, 0.51566, 0.38001],      
           [0.56512, 0.51986, 0.38278],      
           [0.57074, 0.52404, 0.38556],      
           [0.57642, 0.52819, 0.38839],      
           [0.58213, 0.53231, 0.39124],      
           [0.5879, 0.53641, 0.3941],      
           [0.59373, 0.54046, 0.39699],      
           [0.5996, 0.54447, 0.39991],      
           [0.60551, 0.54844, 0.40285],      
           [0.61148, 0.55235, 0.40582],      
           [0.61748, 0.5562, 0.40879],      
           [0.62352, 0.56001, 0.41179],      
           [0.62957, 0.56374, 0.4148],      
           [0.63566, 0.56738, 0.41782],      
           [0.64177, 0.57095, 0.42085],      
           [0.64789, 0.57443, 0.42389],      
           [0.65402, 0.57782, 0.42694],      
           [0.66015, 0.58112, 0.42998],      
           [0.66626, 0.58431, 0.43302],      
           [0.67237, 0.5874, 0.43606],      
           [0.67845, 0.59037, 0.43907],      
           [0.6845, 0.59323, 0.44209],      
           [0.69051, 0.59596, 0.44508],      
           [0.69648, 0.59857, 0.44804],      
           [0.7024, 0.60106, 0.451],      
           [0.70826, 0.60343, 0.45392],      
           [0.71406, 0.60565, 0.45681],      
           [0.71979, 0.60777, 0.45967],      
           [0.72545, 0.60974, 0.46249],      
           [0.73102, 0.61159, 0.46529],      
           [0.73652, 0.61331, 0.46805],      
           [0.74194, 0.61491, 0.47077],      
           [0.74728, 0.61639, 0.47345],      
           [0.75252, 0.61775, 0.4761],      
           [0.75768, 0.619, 0.47871],      
           [0.76275, 0.62014, 0.48128],      
           [0.76774, 0.62117, 0.48381],      
           [0.77265, 0.62209, 0.48632],      
           [0.77748, 0.62294, 0.4888],      
           [0.78222, 0.62369, 0.49126],      
           [0.78689, 0.62435, 0.49367],      
           [0.79148, 0.62494, 0.49606],      
           [0.79601, 0.62545, 0.49846],      
           [0.80048, 0.62591, 0.50082],      
           [0.80488, 0.6263, 0.50317],      
           [0.80923, 0.62665, 0.50552],      
           [0.81352, 0.62695, 0.50789],      
           [0.81777, 0.62722, 0.51024],      
           [0.82198, 0.62746, 0.5126],      
           [0.82615, 0.62767, 0.51499],      
           [0.8303, 0.62788, 0.51741],      
           [0.83442, 0.62807, 0.51984],      
           [0.83851, 0.62827, 0.52232],      
           [0.8426, 0.62848, 0.52485],      
           [0.84667, 0.6287, 0.52743],      
           [0.85073, 0.62895, 0.53006],      
           [0.8548, 0.62924, 0.53277],      
           [0.85887, 0.62956, 0.53555],      
           [0.86295, 0.62995, 0.53844],      
           [0.86702, 0.6304, 0.54139],      
           [0.87112, 0.63092, 0.54447],      
           [0.87523, 0.63152, 0.54765],      
           [0.87935, 0.63221, 0.55095],      
           [0.8835, 0.633, 0.55438],      
           [0.88765, 0.6339, 0.55794],      
           [0.89183, 0.63492, 0.56165],      
           [0.89602, 0.63607, 0.5655],      
           [0.90021, 0.63735, 0.5695],      
           [0.90441, 0.63877, 0.57367],      
           [0.90862, 0.64035, 0.57798],      
           [0.91281, 0.64209, 0.58246],      
           [0.917, 0.64398, 0.58709],      
           [0.92115, 0.64604, 0.59188],      
           [0.92528, 0.64827, 0.59681],      
           [0.92937, 0.65068, 0.60188],      
           [0.9334, 0.65324, 0.60709],      
           [0.93738, 0.65598, 0.61241],      
           [0.94127, 0.65887, 0.61786],      
           [0.94508, 0.66194, 0.62341],      
           [0.94879, 0.66514, 0.62903],      
           [0.95239, 0.66849, 0.63473],      
           [0.95587, 0.67198, 0.64049],      
           [0.95923, 0.67559, 0.64628],      
           [0.96244, 0.67931, 0.6521],      
           [0.96551, 0.68315, 0.65794],      
           [0.96844, 0.68707, 0.66376],      
           [0.97121, 0.69107, 0.66956],      
           [0.97383, 0.69515, 0.67534],      
           [0.97628, 0.69928, 0.68107],      
           [0.97859, 0.70347, 0.68675],      
           [0.98074, 0.70769, 0.69238],      
           [0.98273, 0.71194, 0.69793],      
           [0.98458, 0.71622, 0.70341],      
           [0.98628, 0.7205, 0.70882],      
           [0.98784, 0.72481, 0.71414],      
           [0.98927, 0.7291, 0.71939],      
           [0.99057, 0.73341, 0.72456],      
           [0.99175, 0.7377, 0.72965],      
           [0.99282, 0.74199, 0.73466],      
           [0.99379, 0.74626, 0.73959],      
           [0.99465, 0.75053, 0.74445],      
           [0.99542, 0.75479, 0.74923],      
           [0.99611, 0.75902, 0.75396],      
           [0.99672, 0.76324, 0.75863],      
           [0.99726, 0.76746, 0.76323],      
           [0.99774, 0.77166, 0.76779],      
           [0.99816, 0.77584, 0.7723],      
           [0.99852, 0.78002, 0.77677],      
           [0.99883, 0.78419, 0.78119],      
           [0.9991, 0.78834, 0.78558],      
           [0.99933, 0.79249, 0.78993],      
           [0.99952, 0.79663, 0.79427],      
           [0.99969, 0.80077, 0.79857],      
           [0.99982, 0.80491, 0.80285],      
           [0.99993, 0.80904, 0.80713],      
           [1, 0.81316, 0.81138],      
           [1, 0.8173, 0.81562],      
           [1, 0.82143, 0.81985],      
           [1, 0.82556, 0.82408],      
           [1, 0.8297, 0.82831],      
           [1, 0.83384, 0.83253],      
           [1, 0.83798, 0.83675],      
           [1, 0.84214, 0.84097],      
           [1, 0.84629, 0.8452],      
           [1, 0.85045, 0.84943],      
           [1, 0.85462, 0.85365],      
           [1, 0.8588, 0.85789],      
           [1, 0.86298, 0.86214],      
           [1, 0.86717, 0.86639],      
           [1, 0.87137, 0.87064],      
           [1, 0.87557, 0.87491],      
           [1, 0.87978, 0.87918],      
           [1, 0.884, 0.88346],      
           [1, 0.88822, 0.88774],      
           [1, 0.89244, 0.89204],      
           [1, 0.89667, 0.89633],      
           [1, 0.90091, 0.90064]]      
      
turku_map = LinearSegmentedColormap.from_list('turku', cm_data)      
# For use of "viscm view"      
test_cm = turku_map      
      
if __name__ == "__main__":      
    import matplotlib.pyplot as plt      
    import numpy as np      
      
    try:      
        from viscm import viscm      
        viscm(turku_map)      
    except ImportError:      
        print("viscm not found, falling back on simple display")      
        plt.imshow(np.linspace(0, 100, 256)[None, :], aspect='auto',      
                   cmap=turku_map)      
    plt.show()      
