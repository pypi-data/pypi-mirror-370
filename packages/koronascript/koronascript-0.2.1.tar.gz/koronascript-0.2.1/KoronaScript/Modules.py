# Auto-generated, do not edit directly
# see genmodule.py

from .KoronaModule import KoronaModule

class AngleDeletion(KoronaModule):
    """Converts split beam data to single beam data"""
    def __init__(self, **parameters):
        super().__init__('AngleDeletion', **parameters)

class BroadbandNotchFilter(KoronaModule):
    """Applies notch filter(s) to broadband data"""
    def __init__(self, **parameters):
        super().__init__('BroadbandNotchFilter', **parameters)

class BroadbandSplitter(KoronaModule):
    """Splits broadband data into multiple single frequency channels"""
    def __init__(self, **parameters):
        super().__init__('BroadbandSplitter', **parameters)

class BubblSpikeFilter(KoronaModule):
    """Filters bubble spikes"""
    def __init__(self, **parameters):
        super().__init__('BubblSpikeFilter', **parameters)

class Categorization(KoronaModule):
    """Module for categorization"""
    def __init__(self, **parameters):
        super().__init__('Categorization', **parameters)

class CdsViewer(KoronaModule):
    """For viewing the module configuration stored in a processed file"""
    def __init__(self, **parameters):
        super().__init__('CdsViewer', **parameters)

class ChannelDataRemoval(KoronaModule):
    """Removes data on specified channels"""
    def __init__(self, **parameters):
        super().__init__('ChannelDataRemoval', **parameters)

class ChannelRemoval(KoronaModule):
    """Removes specified channels"""
    def __init__(self, **parameters):
        super().__init__('ChannelRemoval', **parameters)

class Combination(KoronaModule):
    """Module for generating combination echograms"""
    def __init__(self, **parameters):
        super().__init__('Combination', **parameters)

class Comment(KoronaModule):
    """For writing a comment"""
    def __init__(self, **parameters):
        super().__init__('Comment', **parameters)

class ComplexToReal(KoronaModule):
    """Converts complex data to real data. (Many modules require real data as input.)"""
    def __init__(self, **parameters):
        super().__init__('ComplexToReal', **parameters)

class DataReduction(KoronaModule):
    """Removes data below configured transducer range"""
    def __init__(self, **parameters):
        super().__init__('DataReduction', **parameters)

class DepthDependentResampling(KoronaModule):
    """Depth dependent resampling"""
    def __init__(self, **parameters):
        super().__init__('DepthDependentResampling', **parameters)

class Depth(KoronaModule):
    """Bottom depth detection module"""
    def __init__(self, **parameters):
        super().__init__('Depth', **parameters)

class Dilate(KoronaModule):
    """A dilation filter.<br>Each pixel gets the value of the max value of its neighbors"""
    def __init__(self, **parameters):
        super().__init__('Dilate', **parameters)

class Downsampling(KoronaModule):
    """Downsampling to reduce vertical resolution"""
    def __init__(self, **parameters):
        super().__init__('Downsampling', **parameters)

class ES60Correction(KoronaModule):
    """Removes the ES60 triangle noise"""
    def __init__(self, **parameters):
        super().__init__('ES60Correction', **parameters)

class EdgeDetection(KoronaModule):
    """Detects edges by using Sobel horizontal and vertical filter"""
    def __init__(self, **parameters):
        super().__init__('EdgeDetection', **parameters)

class EmptyPingRemoval(KoronaModule):
    """Deletes empty pings"""
    def __init__(self, **parameters):
        super().__init__('EmptyPingRemoval', **parameters)

class ErodeLowValues(KoronaModule):
    """Erode values in a spatial surrounding (given by vertical extent) - often used after top thresholding by means of Thresholding module"""
    def __init__(self, **parameters):
        super().__init__('ErodeLowValues', **parameters)

class Erode(KoronaModule):
    """An erode filter.<br>Each pixel gets the value of the min value of its neighbors"""
    def __init__(self, **parameters):
        super().__init__('Erode', **parameters)

class Expression(KoronaModule):
    """Module for generating combination echograms by an expression"""
    def __init__(self, **parameters):
        super().__init__('Expression', **parameters)

class FillMissingData(KoronaModule):
    """Creates missing pingdata"""
    def __init__(self, **parameters):
        super().__init__('FillMissingData', **parameters)

class Filter3X3(KoronaModule):
    """Class implementing a 3�3 filter"""
    def __init__(self, **parameters):
        super().__init__('Filter3X3', **parameters)

class FiskViewDisplay(KoronaModule):
    """Display module"""
    def __init__(self, **parameters):
        super().__init__('FiskViewDisplay', **parameters)

class GroupEnd(KoronaModule):
    """End of a module group"""
    def __init__(self, **parameters):
        super().__init__('GroupEnd', **parameters)

class HorizontalOffsetCorrection(KoronaModule):
    """Performs horizontal offset correction"""
    def __init__(self, **parameters):
        super().__init__('HorizontalOffsetCorrection', **parameters)

class Isolation(KoronaModule):
    """Isolates one category by zeroing out all pixels of different categories"""
    def __init__(self, **parameters):
        super().__init__('Isolation', **parameters)

class Median(KoronaModule):
    """Sets the pixel value to median of its 8 neighbors and itself"""
    def __init__(self, **parameters):
        super().__init__('Median', **parameters)

class NoiseAcceptance(KoronaModule):
    """Median noise acceptance"""
    def __init__(self, **parameters):
        super().__init__('NoiseAcceptance', **parameters)

class NoiseMedianQuantification(KoronaModule):
    """Median noise quantification"""
    def __init__(self, **parameters):
        super().__init__('NoiseMedianQuantification', **parameters)

class NoiseQuantification(KoronaModule):
    """Produces noise quantification datagrams"""
    def __init__(self, **parameters):
        super().__init__('NoiseQuantification', **parameters)

class NoiseRemover(KoronaModule):
    """Removes noise based on parameters in noise quantification datagrams"""
    def __init__(self, **parameters):
        super().__init__('NoiseRemover', **parameters)

class NoiseVisualization(KoronaModule):
    """Visualizes noise parameters in a separate window"""
    def __init__(self, **parameters):
        super().__init__('NoiseVisualization', **parameters)

class PingCollapsing(KoronaModule):
    """Collapses sequential pinging"""
    def __init__(self, **parameters):
        super().__init__('PingCollapsing', **parameters)

class PingThinning(KoronaModule):
    """Deletes pings"""
    def __init__(self, **parameters):
        super().__init__('PingThinning', **parameters)

class PlanktonInversion(KoronaModule):
    """Performs plankton inversion"""
    def __init__(self, **parameters):
        super().__init__('PlanktonInversion', **parameters)

class Plugin(KoronaModule):
    """Plugin (beta)"""
    def __init__(self, **parameters):
        super().__init__('Plugin', **parameters)

class PulseCompressionFilter(KoronaModule):
    """Applies pulse compression filter(s) to broadband data"""
    def __init__(self, **parameters):
        super().__init__('PulseCompressionFilter', **parameters)

class RemoveBottom(KoronaModule):
    """Removes bottom data"""
    def __init__(self, **parameters):
        super().__init__('RemoveBottom', **parameters)

class Rescale(KoronaModule):
    """Rescales some channels to fit into the logarithmic Sv range"""
    def __init__(self, **parameters):
        super().__init__('Rescale', **parameters)

class SchoolCategorization(KoronaModule):
    """Determines whether a school consists of one or more species, and categorizes the whole school<br>if the schools is a single species school"""
    def __init__(self, **parameters):
        super().__init__('SchoolCategorization', **parameters)

class SchoolDetection(KoronaModule):
    """Detects schools on a specified channel"""
    def __init__(self, **parameters):
        super().__init__('SchoolDetection', **parameters)

class Smoother(KoronaModule):
    """Performs smoothing by convolution"""
    def __init__(self, **parameters):
        super().__init__('Smoother', **parameters)

class SpikeFilter(KoronaModule):
    """Filters spikes"""
    def __init__(self, **parameters):
        super().__init__('SpikeFilter', **parameters)

class SpotNoise(KoronaModule):
    """Sets the pixel value to median of its 14 neighbors and itself provided original value is large compared to most neighbours"""
    def __init__(self, **parameters):
        super().__init__('SpotNoise', **parameters)

class TemporaryComputationsBegin(KoronaModule):
    """Start of temporary computations"""
    def __init__(self, **parameters):
        super().__init__('TemporaryComputationsBegin', **parameters)

class TemporaryComputationsEnd(KoronaModule):
    """End of temporary computations"""
    def __init__(self, **parameters):
        super().__init__('TemporaryComputationsEnd', **parameters)

class ThresholdAllChannels(KoronaModule):
    """Masks out values on all channels if some channels are too weak or too strong"""
    def __init__(self, **parameters):
        super().__init__('ThresholdAllChannels', **parameters)

class Threshold(KoronaModule):
    """Masks out values in specific range on individual channels"""
    def __init__(self, **parameters):
        super().__init__('Threshold', **parameters)

class TimeInterval(KoronaModule):
    """Module for processing only the pings in a specified time interval"""
    def __init__(self, **parameters):
        super().__init__('TimeInterval', **parameters)

class Towfish(KoronaModule):
    """Merges towfish data with main echosounder data"""
    def __init__(self, **parameters):
        super().__init__('Towfish', **parameters)

class TrackFilter(KoronaModule):
    """Filters rejected tracks"""
    def __init__(self, **parameters):
        super().__init__('TrackFilter', **parameters)

class Tracking(KoronaModule):
    """Tracks single targets"""
    def __init__(self, **parameters):
        super().__init__('Tracking', **parameters)

class TsDetection(KoronaModule):
    """Detects single targets"""
    def __init__(self, **parameters):
        super().__init__('TsDetection', **parameters)

class VerticalOffsetCorrection(KoronaModule):
    """Performs vertical offset correction"""
    def __init__(self, **parameters):
        super().__init__('VerticalOffsetCorrection', **parameters)

class Writer(KoronaModule):
    """Writes to a .raw file"""
    def __init__(self, **parameters):
        super().__init__('Writer', **parameters)

class NetcdfWriter(KoronaModule):
    """Writes to a .nc file"""
    def __init__(self, **parameters):
        super().__init__('NetcdfWriter', **parameters)
