# -*- coding: utf-8 -*-
"""
Created on Mon Sep 28 10:01:16 2015

@author: Ben
"""

from energyPATHWAYS import config as cfg
from energyPATHWAYS import util
import numpy as np
import numpy_financial as npf
import copy
import inspect
from energyPATHWAYS.shared_classes import StockItem, DemandSalesShareMeasure, DemandSales, DemandStockMeasure
import logging
import pdb
from energyPATHWAYS.generated import schema
from energyPATHWAYS.unit_converter import UnitConverter
from energyPATHWAYS.geomapper import GeoMapper
from energyPATHWAYS import shapes2

class DemandTechCost():
    def __init__(self, tech):
        self.book_life = tech.book_life
        self.demand_tech_unit_type = tech.demand_tech_unit_type
        self.unit = tech.unit
        self.tech_time_unit = tech.time_unit
        self.service_demand_unit = tech.service_demand_unit
        self.stock_time_unit = tech.stock_time_unit
        self.cost_of_capital = tech.cost_of_capital
        self.input_type = 'intensity'

    def calculate(self, vintages, years):
        self.vintages = vintages
        self.years = years
        if self._has_data and self.raw_values is not None:
            self.convert_cost()
            self.remap(map_from='values', map_to='values', time_index_name='vintage', converted_geography=GeoMapper.demand_primary_geography)
            self.values = util.remove_df_levels(self.values, cfg.removed_demand_levels, agg_function='mean')
            self.levelize_costs()
        if not self._has_data:
            self.absolute = False
        if self.raw_values is None:
            # if the class is empty, then there is no data for conversion, so the class is considered converted
            self.absolute = True

    def convert_cost(self):
        """
        convert raw_values to model currency and capacity (energy_unit/time_step)
        """
        if self.demand_tech_unit_type == 'service demand' and self.definition == 'absolute':
            if self.tech_time_unit is None:
                self.time_unit = 'year'
            self.values = UnitConverter.unit_convert(self.raw_values, unit_from_num=self.tech_time_unit,
                                            unit_from_den=self.unit,
                                            unit_to_num=self.stock_time_unit, unit_to_den=self.service_demand_unit)
        else:
            self.values = copy.deepcopy(self.raw_values)

        if self.definition == 'absolute':
            self.values = UnitConverter.currency_convert(self.values, self.currency, self.currency_year)
            self.absolute = True
        else:
            self.absolute = False

    def levelize_costs(self):
        if hasattr(self, 'is_levelized') and (self.definition=='absolute' or (self.definition=='relative' and self.reference_tech_operation=='add')):
            inflation = cfg.getParamAsFloat('inflation_rate', section='UNITS')
            rate = self.cost_of_capital - inflation
            if self.is_levelized == 0:
                self.values_level = - npf.pmt(rate, self.book_life, 1, 0, 'end') * self.values
                util.convert_age(self, attr_from='values_level', attr_to='values_level', reverse=False,
                                 vintages=self.vintages, years=self.years)
            else:
                self.values_level = self.values.copy()
                util.convert_age(self, attr_from='values_level', attr_to='value_level', reverse=False,
                                 vintages=self.vintages, years=self.years)
                self.values = npf.pv(rate, self.book_life, -1, 0, 'end') * self.values
        else:
            util.convert_age(self, attr_from='values', attr_to='values_level', reverse=False, vintages=self.vintages, years=self.years)

class DemandTechsCapitalCostObj(schema.DemandTechsCapitalCost, DemandTechCost):
    def __init__(self, tech, scenario=None, new_or_replacement=None):
        schema.DemandTechsCapitalCost.__init__(self, demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario, new_or_replacement=new_or_replacement)
        self.scenario = scenario
        DemandTechCost.__init__(self, tech=tech)

class DemandTechsInstallationCostObj(schema.DemandTechsInstallationCost, DemandTechCost):
    def __init__(self, tech, scenario=None, new_or_replacement=None):
        schema.DemandTechsInstallationCost.__init__(self, demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario, new_or_replacement=new_or_replacement)
        self.scenario = scenario
        DemandTechCost.__init__(self, tech=tech)

class DemandTechsIncentiveObj(schema.DemandTechsIncentive, DemandTechCost):
    def __init__(self, tech, scenario=None, incentive_type=None):
        schema.DemandTechsIncentive.__init__(self, demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario, incentive_type=incentive_type)
        self.scenario = scenario
        self.reference_tech_operation = None
        if incentive_type=='capital_cost_fraction':
            self.definition = 'relative'
        elif incentive_type=='absolute':
            self.definition = 'absolute'
        else:
            raise ValueError('Unrecognized incentive_type {} for technology {}'.format(incentive_type, tech.name))
        DemandTechCost.__init__(self, tech=tech)

    def reverse_sign(self):
        if hasattr(self, 'values'):
            if any(self.values.values < 0):
                logging.warning('Negative input values detected for the incentive for technology {}. By convention, input values should be positive.'.format(self.demand_technology))
            self.values *= -1
            self.values_level *= -1

class DemandTechsFuelSwitchCostObj(schema.DemandTechsFuelSwitchCost, DemandTechCost):
    def __init__(self, tech, scenario=None):
        schema.DemandTechsFuelSwitchCost.__init__(self, demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario)
        self.scenario = scenario
        DemandTechCost.__init__(self, tech=tech)

class DemandTechsFixedMaintenanceCostObj(schema.DemandTechsFixedMaintenanceCost, DemandTechCost):
    def __init__(self, tech, scenario=None):
        schema.DemandTechsFixedMaintenanceCost.__init__(self, demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario)
        self.scenario = scenario
        DemandTechCost.__init__(self, tech=tech)


class ParasiticEnergy(schema.DemandTechsParasiticEnergy):
    def __init__(self, tech, scenario=None):
        super(ParasiticEnergy, self).__init__(demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario)
        self.scenario = scenario
        self.input_type = 'intensity'
        self.tech_unit = tech.unit
        self.demand_tech_unit_type = tech.demand_tech_unit_type
        self.service_demand_unit = tech.service_demand_unit


    def calculate(self, vintages, years):
        self.vintages = vintages
        self.years = years
        if self._has_data and self.raw_values is not None:
            self.convert()
            self.remap(map_from='values', map_to='values', time_index_name='vintage', converted_geography=GeoMapper.demand_primary_geography)
            util.convert_age(self, reverse=True, vintages=self.vintages, years=self.years)
            self.values = util.remove_df_levels(self.values, cfg.removed_demand_levels, agg_function='mean')
        if not self._has_data:
            self.absolute = False
        if self.raw_values is None:
            # if the class is empty, then there is no data for conversion, so the class is considered absolute
            self.absolute = True

    def convert(self):
        """
        return values from raw_values that are converted to units consistent with output units - energy and annual
        """
        if self.definition == 'absolute':
            if self.time_unit is None:
                self.time_unit = 'year'
            self.values = UnitConverter.unit_convert(self.raw_values, unit_from_num=self.energy_unit,
                                            unit_from_den=self.time_unit,
                                            unit_to_num=cfg.calculation_energy_unit,
                                            unit_to_den='year')
            self.values = util.remove_df_levels(self.values, cfg.removed_demand_levels, agg_function='mean')
            if self.demand_tech_unit_type == 'service demand':
                self.values = UnitConverter.unit_convert(self.values, unit_from_num=self.unit,
                                                unit_to_num=self.service_demand_unit)
            self.absolute = True


        else:
            self.values = self.raw_values.copy()
            self.absolute = False


class DemandTechEfficiency(object):
    def __init__(self, tech):
        self.service_demand_unit = tech.service_demand_unit
        self.input_type = 'intensity'

    def calculate(self, vintages, years):
        self.vintages = vintages
        self.years = years
        if self.raw_values is not None:
            self.convert()
            self.remap(map_from='values', map_to='values', time_index_name='vintage', converted_geography=GeoMapper.demand_primary_geography)
            util.convert_age(self, reverse=True, vintages=self.vintages, years=self.years)
            self.values = util.remove_df_levels(self.values, cfg.removed_demand_levels, agg_function='mean')
        if not self._has_data:
            self.absolute = False
        if self.raw_values is None:
            # if the class is empty, then there is no data for conversion, so the class is considered converted
            self.absolute = True

    def convert(self):
        """
        return values from raw_values that are converted to units consistent with output units
        """
        if self.definition == 'absolute':
            if self.is_numerator_service:
                # if the numerator is service, definition has to be flipped in order to make the numerator an energy unit
                self.values = 1 / self.raw_values
                numerator_unit = self.denominator_unit
                denominator_unit = self.numerator_unit
                self.flipped = True
            else:
                self.values = self.raw_values
                numerator_unit = self.numerator_unit
                denominator_unit = self.denominator_unit
                self.flipped = False
            self.values = UnitConverter.unit_convert(self.values, unit_from_num=numerator_unit,
                                            unit_from_den=denominator_unit,
                                            unit_to_num=cfg.calculation_energy_unit,
                                            unit_to_den=self.service_demand_unit)
            self.absolute = True
        else:
            self.values = self.raw_values.copy()
            self.absolute = False

class DemandTechsMainEfficiencyObj(schema.DemandTechsMainEfficiency, DemandTechEfficiency):
    def __init__(self, tech, scenario=None):
        schema.DemandTechsMainEfficiency.__init__(self, demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario)
        self.scenario = scenario
        DemandTechEfficiency.__init__(self, tech=tech)

class DemandTechsAuxEfficiencyObj(schema.DemandTechsAuxEfficiency, DemandTechEfficiency):
    def __init__(self, tech, scenario=None):
        schema.DemandTechsAuxEfficiency.__init__(self, demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario)
        self.scenario = scenario
        DemandTechEfficiency.__init__(self, tech=tech)


class DemandTechServiceLink(schema.DemandTechsServiceLink):
    """ service link efficiency
    ex. clothes washer hot water efficiency
    """

    def __init__(self, name, scenario=None):
        super(DemandTechServiceLink, self).__init__(name=name, scenario=scenario)
        self.init_from_db(name, scenario)
        self.scenario = scenario
        self.input_type = 'intensity'

    def calculate(self, vintages, years):
        self.vintages = vintages
        self.years = years
        if self._has_data and self.raw_values is not None:
            self.remap(map_from='raw_values', map_to='values', time_index_name='vintage', converted_geography=GeoMapper.demand_primary_geography)
            util.convert_age(self, reverse=True, vintages=self.vintages, years=self.years)
            self.values = util.remove_df_levels(self.values, cfg.removed_demand_levels, agg_function='mean')
        if not self._has_data:
           self.absolute = False
        if self.raw_values is None:
            # if the class is empty, then there is no data for conversion, so the class is considered converted
            self.absolute = True



class ServiceDemandModifier(schema.DemandTechsServiceDemandModifier):
    """ technology specified service demand modifier. Replaces calculated modifiers
    based on stock and service/energy demand inputs."""

    def __init__(self, tech, scenario=None):
        super(ServiceDemandModifier, self).__init__(demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario)
        self.scenario = scenario
        self.input_type = 'intensity'

    def calculate(self, vintages, years):
        self.vintages = vintages
        self.years = years
        if self._has_data and self.raw_values is not None:
            self.values = copy.deepcopy(self.raw_values)
            self.values['age'] = self.values.index.get_level_values('year') - self.values.index.get_level_values('vintage')
            self.values = self.values.set_index('age',append=True)
            self.values = util.remove_df_levels(self.values,'year')
            self.remap(map_from='values', map_to='values', time_index_name='vintage', converted_geography=GeoMapper.demand_primary_geography)
            self.values['year'] = self.values.index.get_level_values('vintage') + self.values.index.get_level_values('age')
            self.values = self.values.set_index('year',append=True)
            self.values = util.remove_df_levels(self.values,'age')
            self.remap(map_from='values', map_to='values', time_index_name='year', current_geography=GeoMapper.demand_primary_geography,
                       converted_geography=GeoMapper.demand_primary_geography)
            self.values = self.values.unstack('year')
            self.values.columns = self.values.columns.droplevel()
            #util.convert_age(self, attr_from='values', attr_to='values', reverse=False, vintages=self.vintages, years=self.years)
            self.values = util.remove_df_levels(self.values, cfg.removed_demand_levels, agg_function='mean')
        if not self._has_data:
            self.absolute = False
        if self.raw_values is None:
            # if the class is empty, then there is no data for conversion, so the class is considered converted
            self.absolute = True


class AirPollution(schema.DemandTechsAirPollution):
    """ technology specified service demand modifier. Replaces calculated modifiers
    based on stock and service/energy demand inputs."""

    def __init__(self, tech, scenario=None):
        super(AirPollution, self).__init__(demand_technology=tech.name, scenario=scenario)
        self.init_from_db(tech.name, scenario)
        self.scenario = scenario
        self.input_type = 'intensity'

    def calculate(self, vintages, years):
        self.vintages = vintages
        self.years = years
        if self._has_data and self.raw_values is not None:
            self.convert()
            self.remap(map_from='values', map_to='values', time_index_name='year', converted_geography=GeoMapper.demand_primary_geography)
            self.remap(map_from='values', map_to='values', time_index_name='vintage', current_geography=GeoMapper.demand_primary_geography, converted_geography=GeoMapper.demand_primary_geography)
            #self.remap(map_from='values', map_to='values', time_index_name='year',current_geography=GeoMapper.demand_primary_geography,converted_geography=GeoMapper.demand_primary_geography)
            self.values = self.values.unstack('year')
            self.values.columns = self.values.columns.droplevel()
        if not self._has_data:
            self.absolute = False
        if self.raw_values is None:
            # if the class is empty, then there is no data for conversion, so the class is considered converted
            self.absolute = True


    def convert(self):
        """
        return values from raw_values that are converted to units consistent with output units - energy and annual
        """
        if self.definition == 'absolute':
            self.values = UnitConverter.unit_convert(self.raw_values, unit_from_den=self.energy_unit,
                                            unit_from_num=self.mass_unit,
                                                     unit_to_den=cfg.calculation_energy_unit,
                                            unit_to_num=cfg.getParam('mass_unit', section='UNITS'))
            self.absolute = True
        else:
            self.values = self.raw_values.copy()
            self.absolute = False

class DemandTechnology(schema.DemandTechs, StockItem):
    def __init__(self, name, service_demand_unit, stock_time_unit, cost_of_capital, scenario=None):
        schema.DemandTechs.__init__(self, name=name, scenario=scenario)
        self.init_from_db(name, scenario)
        StockItem.__init__(self)
        self.scenario = scenario
        self.service_demand_unit = service_demand_unit
        self.stock_time_unit = stock_time_unit
        # if cost_of_capital at the technology level is None, it uses subsector defaults
        self.cost_of_capital = self.cost_of_capital or cost_of_capital
        # we can have multiple sales shares because sales share may be specific
        # to the transition between two technologies
        self.reference_sales_shares = {}
        if self.name in util.csv_read_table('DemandSales', column_names='demand_technology', return_iterable=True):
            self.reference_sales_shares[1] = DemandSales(demand_technology=self.name, scenario=scenario)
            if self.reference_sales_shares[1].raw_values is None:
                del self.reference_sales_shares[1]
        self.book_life()
        self.add_class()
        self.min_year()
        # self.shape = shape.shapes.data[self.shape_id] if self.shape_id is not None else None

    def set_geography_map_key(self, geography_map_key):
        # specified stock measures do not have their own map keys but instead need to use the same map key as StockData else we can have a mismatch in stock totals
        # by passing it in here, we can grab it when we geomap the specified stock
        self.geography_map_key = geography_map_key

    def get_shape(self, default_shape):
        return shapes2.ShapeContainer.get_values(default_shape) if self.shape is None else shapes2.ShapeContainer.get_values(self.shape)

    def get_max_lead_hours(self):
        return self.max_lead_hours if self.max_lead_hours else None

    def get_max_lag_hours(self):
        return self.max_lag_hours if self.max_lag_hours else None

    def add_sales_share_measures(self):
        self.sales_shares = {}
        sales_share_names = self.scenario.get_measures('DemandSalesShareMeasures', self.subsector, self.name)
        for sales_share_name in sales_share_names:
            self.sales_shares[sales_share_name] = DemandSalesShareMeasure(name=sales_share_name, subsector=self.subsector, scenario=self.scenario)

    def add_specified_stock_measures(self):
        self.specified_stocks = {}
        measure_names = self.scenario.get_measures('DemandStockMeasures', self.subsector, self.name)
        for measure_name in measure_names:
            self.specified_stocks[measure_name] = DemandStockMeasure(name=measure_name, subsector=self.subsector, scenario=self.scenario)
            self.specified_stocks[measure_name].set_geography_map_key(self.geography_map_key)

    def add_service_links(self):
        """adds all technology service links"""
        self.service_links = {}
        service_links = util.csv_read_table('DemandTechsServiceLink', 'service_link', return_unique=True, demand_technology=self.name)
        if service_links:
            for service_link in util.ensure_iterable(service_links):
                name = util.csv_read_table('DemandTechsServiceLink', 'name', return_unique=True, demand_technology=self.name, service_link=service_link)
                self.service_links[service_link] = DemandTechServiceLink(name, scenario=self.scenario)

    def min_year(self):
        """calculates the minimum or start year of data in the technology specification.
        Used to determine start year of subsector for analysis."""
        attributes = vars(self)
        self.min_year = cfg.getParamAsInt('current_year', section='TIME')
        for att in attributes:
            obj = getattr(self, att)
            if inspect.isclass(type(obj)) and hasattr(obj, '__dict__') and hasattr(obj, 'raw_values'):
                try:
                    att_min_year = min(obj.raw_values.index.levels[util.position_in_index(obj.raw_values, 'vintage')])
                except:
                    att_min_year = self.min_year
                if att_min_year < self.min_year:
                    self.min_year = att_min_year
                else:
                    pass

    def calculate(self, vintages, years):
        self.vintages = vintages
        self.years = years
        attributes = vars(self)
        for att in attributes:
            obj = getattr(self, att)
            if inspect.isclass(type(obj)) and hasattr(obj, '__dict__') and hasattr(obj, 'calculate'):
                obj.calculate(self.vintages, self.years)
        for links in self.service_links.values():
            links.calculate(self.vintages, self.years)

    def book_life(self):
        """
        determines book life for measures based on input mean or max/min lifetimes.
        Used for cost levelization
        """
        if self.mean_lifetime is not None:
            self.book_life = getattr(self, 'mean_lifetime')
        elif self.max_lifetime is not None and self.min_lifetime is not None:
            self.book_life = (getattr(self, 'min_lifetime') + getattr(self, 'max_lifetime')) / 2
        else:
            logging.debug("incomplete lifetime information entered for technology %s" % self.name)


    def add_class(self):
        """
        Adds all demand technology classes and uses replace_costs function on
        equivalent costs.

        """
        # todo revisit new vs existing
        self.capital_cost_new = DemandTechsCapitalCostObj(self, scenario=self.scenario, new_or_replacement='new')
        self.capital_cost_replacement = DemandTechsCapitalCostObj(self, scenario=self.scenario, new_or_replacement='replacement')
        self.installation_cost_new = DemandTechsInstallationCostObj(self, scenario=self.scenario, new_or_replacement='new')
        self.installation_cost_replacement = DemandTechsInstallationCostObj(self, scenario=self.scenario, new_or_replacement='replacement')
        self.incentive_fraction = DemandTechsIncentiveObj(self, scenario=self.scenario, incentive_type='capital_cost_fraction')
        self.incentive_absolute = DemandTechsIncentiveObj(self, scenario=self.scenario, incentive_type='absolute')
        self.incentive_new = None # we create this later
        self.incentive_replacement = None  # we create this later
        if self.incentive_fraction._has_data and self.incentive_absolute._has_data:
            assert self.incentive_fraction.apply_lesser_of_incentives == self.incentive_absolute.apply_lesser_of_incentives
        self.fuel_switch_cost = DemandTechsFuelSwitchCostObj(self, scenario=self.scenario)
        self.fixed_om = DemandTechsFixedMaintenanceCostObj(self, scenario=self.scenario)
        self.efficiency_main = DemandTechsMainEfficiencyObj(self, scenario=self.scenario)
        self.efficiency_aux = DemandTechsAuxEfficiencyObj(self, scenario=self.scenario)
        if hasattr(self.efficiency_main,'definition') and self.efficiency_main.definition == 'absolute':
            self.efficiency_aux.utility_factor = 1 - self.efficiency_main.utility_factor
        self.service_demand_modifier = ServiceDemandModifier(self, scenario=self.scenario)
        self.parasitic_energy = ParasiticEnergy(self, scenario=self.scenario)
        self.air_pollution = AirPollution(self,scenario=self.scenario)
        # add service links to service links dictionary
        self.add_service_links()
        self.replace_class('capital_cost_new', 'capital_cost_replacement')
        self.replace_class('installation_cost_new', 'installation_cost_replacement')
        self.replace_class('fuel_switch_cost')
        self.replace_class('fixed_om')


    def replace_class(self, class_a, class_b=None):
        """
        Adds all available cost data to classes. Removes classes with no data and replaces
        them with cost classes containing equivalent data.

        Ex. If capital costs for new installations are input but capital costs for replacement are not,
        it copies capital costs for new to the replacement capital cost class
        """
        # if no class_b is specified, there is no equivalent cost for class_a
        if class_b is None:
            class_a_instance = getattr(self, class_a)
            if class_a_instance._has_data is False and hasattr(class_a_instance, 'reference_tech_id') is False:
                logging.debug("demand technology %s has no %s cost data" % (self.name, class_a))
        else:
            class_a_instance = getattr(self, class_a)
            class_b_instance = getattr(self, class_b)
            if class_a_instance._has_data is True and class_a_instance.raw_values is not None and class_b_instance._has_data is True and class_b_instance.raw_values is not None:
                pass
            elif class_a_instance._has_data is False and class_b_instance._has_data is False and \
                            hasattr(class_a_instance, 'reference_tech_id') is False and \
                            hasattr(class_b_instance, 'reference_tech_id') is False:
                logging.debug("demand technology %s has no input data for %s or %s" % (self.name, class_a, class_b))
            elif class_a_instance._has_data is True and class_a_instance.raw_values is not None and (class_b_instance._has_data is False or (class_b_instance._has_data is True and class_b_instance.raw_values is None)):
                setattr(self, class_b, copy.deepcopy(class_a_instance))
            elif (class_a_instance._has_data is False or (class_a_instance._has_data is True and class_a_instance.raw_values is None))and class_b_instance._has_data is True and class_b_instance.raw_values is not None:
                setattr(self, class_a, copy.deepcopy(class_b_instance))
