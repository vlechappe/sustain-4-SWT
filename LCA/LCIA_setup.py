import numpy as np

# LCIA_setup
# this list of tuples can be used to call LCIA methods in brightway
methods_recommended=[
            ('EF v3.0','material resources: metals/minerals','abiotic depletion potential (ADP): elements (ultimate reserves)'),
            ('EF v3.0','ecotoxicity: freshwater', 'comparative toxic unit for ecosystems (CTUe) '),
            ('EF v3.0','climate change', 'global warming potential (GWP100)'),
            ('EF v3.0','energy resources: non-renewable','abiotic depletion potential (ADP): fossil fuels'),
            ('EF v3.0','particulate matter formation', 'impact on human health')
            ]
# this list of tuples contains the EF 3.0 methods 

methods_EF=[('EF v3.0','acidification', 'accumulated exceedance (ae)'),
            ('EF v3.0','climate change', 'global warming potential (GWP100)'),
            ('EF v3.0','ecotoxicity: freshwater', 'comparative toxic unit for ecosystems (CTUe) '),
            ('EF v3.0','energy resources: non-renewable', 'abiotic depletion potential (ADP): fossil fuels'),
            ('EF v3.0','eutrophication: freshwater', 'fraction of nutrients reaching freshwater end compartment (P)'),
            ('EF v3.0','eutrophication: marine', 'fraction of nutrients reaching marine end compartment (N)'),
            ('EF v3.0','eutrophication: terrestrial', 'accumulated exceedance (AE) '),
            ('EF v3.0','human toxicity: carcinogenic', 'comparative toxic unit for human (CTUh) '),
            ('EF v3.0','human toxicity: non-carcinogenic', 'comparative toxic unit for human (CTUh) '),
            ('EF v3.0','ionising radiation: human health', 'human exposure efficiency relative to u235'),
            ('EF v3.0','land use', 'soil quality index'),
            ('EF v3.0','material resources: metals/minerals', 'abiotic depletion potential (ADP): elements (ultimate reserves)'),
            ('EF v3.0','ozone depletion', 'ozone depletion potential (ODP) '),
            ('EF v3.0','particulate matter formation', 'impact on human health'),
            ('EF v3.0','photochemical ozone formation: human health', 'tropospheric ozone concentration increase'),
            ('EF v3.0','water use', 'user deprivation potential (deprivation-weighted water consumption)')
                      
           ]
# EF3.0 normalisation factors 
EF_NF={
    methods_EF[0][1]:5.56E+01,
    methods_EF[1][1]:8.10E+03,
    methods_EF[2][1]:4.27E+04,
    methods_EF[3][1]:6.50E+04,
    methods_EF[4][1]:1.61E+00,
    methods_EF[5][1]:1.95E+01,
    methods_EF[6][1]:1.77E+02,
    methods_EF[7][1]:1.69E-05,
    methods_EF[8][1]:2.30E-04,
    methods_EF[9][1]:4.22E+03,
    methods_EF[10][1]:8.19E+05,
    methods_EF[11][1]:6.36E-02,
    methods_EF[12][1]:5.36E-02,
    methods_EF[13][1]:5.95E-04,
    methods_EF[14][1]:4.06E+01,
    methods_EF[15][1]:1.15E+04,
        }
# EF3.0 Weighing factors 
EF_WF={
    methods_EF[0][1]:6.20E-02,
    methods_EF[1][1]:21.06E-02,
    methods_EF[2][1]:1.92E-02,
    methods_EF[3][1]:8.32E-02,
    methods_EF[4][1]:2.80E-02,
    methods_EF[5][1]:2.96E-02,
    methods_EF[6][1]:3.71E-02,
    methods_EF[7][1]:2.13E-02,
    methods_EF[8][1]:1.84E-02,
    methods_EF[9][1]:5.01E-02,
    methods_EF[10][1]:7.94E-02,
    methods_EF[11][1]:7.55E-02,
    methods_EF[12][1]:6.31E-02,
    methods_EF[13][1]:8.96E-02,
    methods_EF[14][1]:4.78E-02,
    methods_EF[15][1]:8.51E-02,
        }


NF=np.zeros(16)
WF=np.zeros(16)

for i in range(0,len(WF)):
    NF[i]=EF_NF[methods_EF[i][1]]
    WF[i]=EF_WF[methods_EF[i][1]]
    


####DATA FOR GRAPH####

# this list and the dictionary contains the names of the impacts and the units for the plots
impacts_order_grid=['Material resources',
                    'Climate change',
                    'Energy non-renewable',
                    'Human toxicity, non-carcinogenic',
                    'Ecotoxicity, freshwater',
                    'Acidification'
               ]

impacts_order=['Material resources',
               'Ecotoxicity, freshwater',
               'Climate change',
               'Energy non-renewable',
               'Particulate matter'
               ]

correspondances_kwh = {impacts_order[0]:'kg Sb-eq/kWh',
                    impacts_order[1]:'CTUe/kWh',
                   impacts_order[2]:'kg CO2-eq/kWh',
                   impacts_order[3]:'MJ/kWh', 
                   impacts_order[4]:'disease incidence/kWh',
                   impacts_order_grid[5]:'mol H+ eq./kWh',
                   impacts_order_grid[3]:'CTUh/kWh'}

correspondances = {
                    impacts_order[0]:'kg Sb-eq',
                    impacts_order[1]:'CTUe',
                   impacts_order[2]:'kg CO2-eq',
                   impacts_order[3]:'MJ', 
                   impacts_order[4]:'disease incidence',
                   impacts_order_grid[5]:'mol H+ eq.',
                   impacts_order_grid[3]:'CTUh'
                   }


#### This step requires extra carefulness, here 'order' and 'activities' contain only activities from the mast and turbine
#### so the lcia using these variables will only take impacts from the mast and turbine


order_wt={'wood':'production of wind turbine wood only',
          'steel':'production of wind turbine steel only',
          'resin':'production of wind turbine resin only',
          'magnet':'production of wind turbine magnet only',
          'copper':'production of wind turbine copper only',
          'other':'production of wind turbine other materials only',
          'transport':'transport of wind turbine'}

order_18m={'18m steel no zinc':'production of 18m structure steel no zinc',
          '18m concrete':'production of 18m structure concrete only',
          '18m zinc':'production of 18m zinc coat',
          '18m cable':'production of mast cable 48V',
          '18m transport concrete':'transport of 18m concrete structure',
          '18m transport steel':'transport of 18m steel structure'}

order_12m={'12m steel no zinc':'production of 12m structure steel no zinc',
          '12m concrete':'production of 12m structure concrete only',
          '12m zinc':'production of 12m zinc coat',
          '12m cable':'production of mast cable 48V',
          '12m transport concrete':'transport of 12m concrete structure',
          '12m transport steel':'transport of 12m steel structure'}

order_electronics={ 'electronics rectifier': 'rectifier final',
                    'electronics charge controller' : 'charge controller final',
                    'electronics dump load':'dump load final',
                    'electronics batteries':'batteries final',
                    'electronics inverter': 'inverter final',
                    'electronics cables': 'cable final',
                    'electronics transport':'transport final',
                    }

order_electronics_grid={ 'electronics rectifier': 'rectifier final',
                    'electronics charge controller' : 'charge controller final',
                    'electronics dump load':'dump load final',
                    'electronics electricity':'grid_electricity',
                    'electronics inverter': 'inverter final',
                    'electronics cables': 'cable final',
                    'electronics transport':'transport final',
                    }

    
#### This step requires extra carefulness, here 'order_18' and 'activities_18' contain activities from the mast, turbine and electronics
#### so the lcia using these variables will take into account impacts from mast turbine and electronics
### for 12 m lcia, change 18 to 12
