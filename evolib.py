from besos import eppy_funcs as ef
import sampling
from evaluator import EvaluatorEP
from objectives import MeterReader
from optimizer import NSGAII, SPEA2
from parameters import expand_plist
from problem import EPProblem
import platypus
import pandas as pd
import matplotlib.pyplot as plt
from platypus.evaluator import MapEvaluator


def insertVar(fname,classEP,objEP,fieldEP,minEP,maxEP):
	building = ef.get_building(fname) # Carregando o modelo do E+;
	parameters = []
	parameters.append( 
				Parameter(
                	selector=FieldSelector(
                    class_name=classEP,            			   # Classe do E+;
                    object_name=objEP,                          # Nome do objeto;
                    field_name=fiedlEP, 						   # Campo do objeto;
                ),
                	value_descriptor=RangeParameter(min_val=minEP, max_val=maxEP)      # limites;
                )
            )
	print (parameters)