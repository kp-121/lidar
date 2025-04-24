from DataExtractor import DataExtractor
from Visualization import Visualization
from LMOG import LiDARMOG


if __name__ == '__main__':
    extractor = DataExtractor(port='COM6', baudrate=230400, timeout=0.1)
    mog = LiDARMOG(num_bins=360, num_gaussians=1, learning_rate=0.05, threshold=2.5)
    viz = Visualization(extractor, mog, radius=15.0)
    viz.run(debug=True, use_reloader=False)
