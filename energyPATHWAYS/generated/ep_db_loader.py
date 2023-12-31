from csvdb import CsvMetadata, CsvDatabase
from energyPATHWAYS.generated.text_mappings import MappedCols

_Metadata = [
    CsvMetadata('BlendNodeBlendMeasures',
                key_col='name',
                df_cols=['gau', 'demand_sector', 'value', 'year']),
    CsvMetadata('BlendNodeInputsData',
                data_table=True),
    CsvMetadata('CO2PriceMeasures',
                key_col='name',
                drop_cols=['source', 'notes'],
                lowcase_cols=['sensitivity'],
                df_cols=['gau', 'sensitivity', 'value', 'year']),
    CsvMetadata('CurrenciesConversion',
                data_table=True),
    CsvMetadata('DemandDrivers',
                key_col='name',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['gau', 'value', 'oth_2', 'oth_1', 'year', 'sensitivity']),
    CsvMetadata('DemandEnergyDemands',
                key_col='subsector',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['unit','gau', 'demand_technology', 'value', 'oth_2', 'oth_1', 'year', 'final_energy', 'sensitivity']),
    CsvMetadata('DemandEnergyEfficiencyMeasures',
                key_col='name',
                drop_cols=['source', 'notes'],
                df_cols=['unit','gau', 'value', 'oth_2', 'oth_1', 'year', 'final_energy']),
    CsvMetadata('DemandEnergyEfficiencyMeasuresCost',
                key_col='parent',
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'final_energy']),
    CsvMetadata('DemandFuelSwitchingMeasures',
                key_col='name'),
    CsvMetadata('DemandFuelSwitchingMeasuresCost',
                key_col='parent',
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1']),
    CsvMetadata('DemandFuelSwitchingMeasuresEnergyIntensity',
                key_col='parent',
                drop_cols=['source', 'notes'],
                df_cols=['gau', 'value', 'oth_2', 'oth_1', 'year']),
    CsvMetadata('DemandFuelSwitchingMeasuresImpact',
                key_col='parent',
                drop_cols=['source', 'notes'],
                df_cols=['unit','gau', 'value', 'oth_2', 'oth_1', 'year']),
    CsvMetadata('DemandSales',
                key_col='demand_technology',
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1','sensitivity']),
    CsvMetadata('DemandSalesShareMeasures',
                key_col='name',
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'oth_1', 'value']),
    CsvMetadata('DemandSectors',
                key_col='name'),
    CsvMetadata('DemandServiceDemandMeasures',
                key_col='name',
                drop_cols=['source', 'notes'],
                df_cols=['gau', 'value', 'oth_2', 'oth_1', 'year']),
    CsvMetadata('DemandServiceDemandMeasuresCost',
                key_col='parent',
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1']),
    CsvMetadata('DemandServiceDemands',
                key_col='subsector',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['gau', 'demand_technology', 'value', 'oth_2', 'oth_1', 'year', 'final_energy', 'sensitivity']),
    CsvMetadata('DemandServiceEfficiency',
                key_col='subsector',
                drop_cols=['source', 'notes'],
                df_cols=['gau', 'value', 'oth_2', 'oth_1', 'year', 'final_energy']),
    CsvMetadata('DemandServiceLink',
                key_col='name'),
    CsvMetadata('DemandStock',
                key_col='subsector',
                drop_cols=['source', 'notes'],
                df_cols=['gau', 'demand_technology', 'value', 'oth_2', 'oth_1', 'year', 'sensitivity']),
    CsvMetadata('DemandStockMeasures',
                key_col='name',
                drop_cols=['source', 'notes'],
                df_cols=['gau', 'oth_1', 'value', 'year']),
    CsvMetadata('DemandSubsectors',
                key_col='name'),
    CsvMetadata('DemandTechs',
                key_col='name'),
    CsvMetadata('DemandTechsAuxEfficiency',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsCapitalCost',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_filters=['new_or_replacement'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsFixedMaintenanceCost',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsFuelSwitchCost',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsInstallationCost',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_filters=['new_or_replacement'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsIncentive',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_filters=['incentive_type'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsMainEfficiency',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsParasiticEnergy',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'value', 'oth_2', 'oth_1', 'final_energy', 'sensitivity']),
    CsvMetadata('DemandTechsServiceDemandModifier',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'year', 'gau', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsAirPollution',
                key_col='demand_technology',
                lowcase_cols=['sensitivity'],
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'year','gau', 'final_energy', 'value', 'oth_2', 'oth_1', 'sensitivity']),
    CsvMetadata('DemandTechsServiceLink',
                key_col='name',
                drop_cols=['source', 'notes'],
                df_cols=['vintage', 'gau', 'oth_1', 'oth_2', 'value']),
    CsvMetadata('DispatchFeedersAllocation',
                key_col='subsector',
                drop_cols=['source', 'notes'],
                df_cols=['gau', 'year', 'value', 'dispatch_feeder', 'sensitivity']),
    CsvMetadata('FinalEnergy',
                data_table=True),
    CsvMetadata('Geographies',
                data_table=True),
    CsvMetadata('GeographiesSpatialJoin',
                data_table=True),
    CsvMetadata('GeographyMapKeys',
                data_table=True),
    CsvMetadata('InflationConversion',
                data_table=True),
    CsvMetadata('OtherIndexes',
                data_table=True),
    CsvMetadata('Shapes',
                data_table=True),
    CsvMetadata('TimeZones',
                data_table=True),
    CsvMetadata('foreign_keys',
                data_table=True),
]

class EnergyPathwaysDatabase(CsvDatabase):
    def __init__(self, pathname=None, load=True, output_tables=False, compile_sensitivities=False, tables_to_not_load=None):
        super(EnergyPathwaysDatabase, self).__init__(
            metadata=_Metadata,
            pathname=pathname,
            load=load,
            mapped_cols=None,
            output_tables=output_tables,
            compile_sensitivities=compile_sensitivities,
            tables_to_not_load=tables_to_not_load,
            tables_without_classes=['CurrenciesConversion', 'GeographyMap', 'IDMap', 'InflationConversion', 'Version', 'foreign_keys'],
            tables_to_ignore=['CurrencyYears', 'DispatchConfig', 'GeographyIntersection', 'GeographyIntersectionData', 'GeographyMap', 'GeographiesSpatialJoin'])
