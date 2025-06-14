"""
Module to initialize parameter tuning.
"""

from strategy_analyzer.models.parameter_tuning.parameter_tuning_processor import ParameterTuningProcessor
from strategy_analyzer.models.parameter_tuning.ma_parameter_tuning import MovingAverageParameterTuning
from strategy_analyzer.models.parameter_tuning.momentum_parameter_tuning import MomentumParameterTuning
from strategy_analyzer.models.parameter_tuning.in_and_out_momentum_parameter_tuning import InAndOutMomentumParameterTuning
from strategy_analyzer.models.parameter_tuning.hierarchal_clustering_parametertuning import HierarchalClusteringParameterTuning
from strategy_analyzer.models.parameter_tuning.ma_crossover_parameter_tuning import MaCrossoverParameterTuning
