#!/usr/bin/env python
# coding: utf-8

# This code was used to generate the results presented in our article ("Finding the Optimal Tower Height for Small Wind Turbine Systems: A Technico-Environmental Approach")[https://papers.ssrn.com/sol3/papers.cfm?abstract_id=4743041] by Prévost et al. 2024.  It is provided in open access under the license creative commons to allow the scientific community to build up on the methodology and result outcomes of this work. 

# In this study investigates the compromise between energy harvest and environmental impacts of a SWT system, taking into account the system design, the site characteristics, and the user behavior aspects. Using the LCA methodology, the impact assessment of the SWT system is compared for several tower heights. Then, the tower is used as a leverage to optimize the environmental footprint of the system functional electricity (i.e. the electricity meeting the user energy need). We show that there exists an optimal tower height that minimizes the environmental footprint of the SWT electricity.

# ## Setup

# At first we import the necessary packages (brightway for LCA, pandas for data, numpy for computations, matplotlib for graphs) and we select the proper project.

# # Technico-environmental analysis and recommendations for small wind turbine systems

# In[4]:


####INITIAL SETUP####

#from brightway2 import *

#bw.Database('biosphere3').delete()
#bw.Database('biosphere3').deregister()
#all_method_tuples = list(bw.methods)
#for m in all_method_tuples:
#    bw.Method(m).deregister()
#bw.bw2setup()


# ## System modelling

# In[5]:


####IMPORTING####

from brightway2 import *
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import math
import mylib


from copy import deepcopy
from matplotlib import cbook
from matplotlib import cm
from matplotlib.colors import LightSource
from matplotlib.ticker import ScalarFormatter
from mylib import *
from variables import powercurve
from LCIA_setup import *


##PLT settings##
plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Serif"
})
plt.rcParams['font.size'] = 17
projects.set_current('ACV_eol')
n=200 #number of points between 12 and 24 m mast height
print (databases)


# The energy production of the wind turbine depends on the caracteristics of the wind turbine itself but also the wind distribution on site. The European standard  EN 61400-12-1 has a standardized method to compute the Annual Energy Production $AEP$ of the wind turbine.
# The power curve $P$ of the wind turbine gives us the power generated for values of the wind speed. For the wind distribution on site we use the Rayleigh cumulative probability distribution $F(V)$.

# <p style="text-align: center;">$F(V) = 1-e^{-\frac{\pi}{4}\left(\frac{V}{V_{avg}}\right)^2}$</p>

# where
# 
# $V$ is the wind speed
# 
# $V_{avg}$ is the average wind speed at hub height

# The $AEP$ is computed using $N$ bins $i$, each containing a wind speed $V_i$ and its associated power $P_i$

# <p style="text-align: center;">$AEP = N_h \sum_{i=1}^N[F(V_i)-F(V_{i-1})]\left(\frac{P_{i-1}+P_i}{2}\right)$</p>

# $N_h$ is the number of hours in a year.

# $V_{avg}$ has to be computed from models and values measured on site. For a given site we can get an average wind speed $V_{ref}$ at a given height $h_{ref}$. There are several models to get the wind speed at given height knowing the wind speed at an other height.

#  The power law uses the wind shear exponent $\alpha$ measured empirically on several types terrain, it depends on the roughness of terrain which changes the distrbution of wind at different heights.

# <p style="text-align: center;">$V = V_{ref} \left(\frac{h}{h_{ref}}\right)^\alpha$</p>

# The logarithmic law uses the surface roughness length $z_0$ which plays a role similar to $\alpha$ but has a dimension homogeneous to a length.

# <p style="text-align: center;">$V = V_{ref}\frac{\ln\left(\frac{h}{z_0}\right)}{\ln\left(\frac{h_{ref}}{z_0}\right)}$</p>

# In[6]:


v_mu=np.arange(3,11,0.1)# vector of average wind speed at hub height
aep=np.zeros(len(v_mu))
for i in range(len(v_mu)):
    aep[i]=aep_rayleigh(v_mu[i],powercurve)/1000
aep_poly=np.polyfit(v_mu,aep,4)  
print(aep_poly)
## Plot aep=f(v_mu)
fig, ax = plt.subplots()
ax.set_ylabel('AEP (kwh)')
ax.set_xlabel('$V_h$ (m/s)')
ax.plot(v_mu,aep,linewidth = 1)
#ax.plot(v_mu,np.polyval(aep_poly,v_mu),label='fit')
ax.grid(True)
plt.show()
fig.savefig("figures/aep.svg")


# In[ ]:





# In[7]:


v_ref=4
h_ref=12
h_max=30
h=np.linspace(h_ref,h_max,200)
z_0=np.array([0.01, 0.1,0.3, 0.5])
v=np.ones((len(h),len(z_0)))
aep=np.ones((len(h),len(z_0)))

for i in range(len(h)):
    for j in range(len(z_0)):
        v[i,j]=wind_shear_log(v_ref,h_ref,h[i],z_0[j])
        aep[i,j]=aep_rayleigh(v[i,j],powercurve)/1000

fig, ax = plt.subplots()
ax.set_xlabel('Hub height (m)')
ax.set_ylabel('$V_\mu$ (m/s)')
for j in range(len(z_0)):
    ax.plot(h,v[:,j],label='$z_0=$'+ str(z_0[j]),linewidth = 1)

ax.legend()
ax.grid(True)
plt.show() 


# In[8]:


# plot wind turbine power curve
fig, ax = plt.subplots()
ax.set_xlabel('Wind speed (m/s)')
ax.set_ylabel('Power (W)')
ax.plot(powercurve.Vw,powercurve.Pdc,linewidth = 1,label="Standalone DC 48V NTUA")
ax.grid(True)
fig.savefig("figures/powercurve.svg")
plt.show() 


# In[9]:


fig, ax = plt.subplots()
ax.set_ylabel('AEP (kwh)')
ax.set_xlabel('Hub height (m)')

for j in range(len(z_0)):
    ax.plot(h,aep[:,j],label='$z_0=$'+ str(z_0[j]),linewidth = 1)

ax.legend()
ax.set_xticks(np.arange(12, 33, 3))
ax.grid(True)
plt.show() 
fig.savefig("figures/aep_z0.svg")


# ## Energy modelling for scenario A and B

# In[10]:


h_sc=np.linspace(12,18,2)
h_indexes=np.ones(len(h_sc))
z_0_sc=0.5
for i in range(len(h_sc)):
    h_indexes[i] = int(np.abs(h - h_sc[i]).argmin())
z_0_indexes = np.abs(z_0 - z_0_sc).argmin()


# In[11]:


## off-grid
lep_sc=20*np.array([aep[int(h_indexes[0]),int(z_0_indexes)],aep[int(h_indexes[1]),int(z_0_indexes)]])
dep_sc=lep_sc/365/20

#System parameters
inverter_efficiency=0.9
battery_efficiency=0.8

oversizing_factor=0.15 # Average proportion of energy being lost in dump load
load_shifting_factor=0.2 
grid_injection_factor=0
storage_factor=1-oversizing_factor-load_shifting_factor-grid_injection_factor

N_d=2 # Number of days of autonomy
SoC_min=0.5 # Minimum acceptable battery SoC
system_lifetime=20

#lifetime useful energy (from article, eq. 5)
lue_sc=lep_sc*inverter_efficiency*(grid_injection_factor+storage_factor*battery_efficiency+load_shifting_factor)
print('LEP',lep_sc)
print('LUE',lue_sc)

#daily energy needs (DEN)
den_kwh=lue_sc/365/20
print ('DEN',den_kwh)


# In[12]:


## grid tied

oversizing_factor=0 
load_shifting_factor=0.2 
storage_factor=0
grid_injection_factor=1-oversizing_factor-load_shifting_factor-storage_factor

E_g=dep_sc*grid_injection_factor*inverter_efficiency # daily withdrawn grid energy
den_grid=dep_sc*inverter_efficiency
lue_grid=den_grid*365*20
leg=E_g*365*20 # lifetime grid energy


# In[13]:


leg


# In[14]:


# Battery sizing

bat_cap_kwh=den_kwh*N_d/(SoC_min*inverter_efficiency)
bat_cap_kwh


# In[15]:


bat_specific_energy=30.58 # Kebede et al. 2021
kg_kwh=1000/bat_specific_energy # wh/kg to kg/kwh
bat_fit=np.array([kg_kwh, 0])
bat_weight_kg=kg_kwh*bat_cap_kwh
bat_weight_kg


# In[16]:


print(h_sc[0],'m tower -','Average wind speed at hub height',v[int(h_indexes[0]),int(z_0_indexes)],': Daily Energy Needs (kwh) : ',den_kwh[0],' Battery capacity (kwh) : ',bat_cap_kwh[0], ' Battery weight (kg) : ',bat_weight_kg[0])

print(h_sc[1],'m tower -','Average wind speed at hub height',v[int(h_indexes[1]),int(z_0_indexes)],': Daily Energy Needs (kwh) : ',den_kwh[1],' Battery capacity (kwh) : ',bat_cap_kwh[1], ' Battery weight (kg) : ',bat_weight_kg[1])


# # LCA of complete wind turbine

# In[17]:


####SET LCIA METHODS####

from LCIA_setup import *

activities_wt=[Database('12m_wind_turbine').search(j)[0] for (i,j) in order_wt.items()]
activities_18m=[Database('18m_mast').search(j)[0] for (i,j) in order_18m.items()]
activities_12m=[Database('12m_mast').search(j)[0] for (i,j) in order_12m.items()]
activities_electronics = [Database('electronics_wind_turbine_oswacc').search(j)[0] for (i,j) in order_electronics.items()]
activities_electronics_grid = [Database('electronics_wind_turbine_oswacc').search(j)[0] for (i,j) in order_electronics_grid.items()]

#### This step requires extra carefulness, here 'order_18' and 'activities_18' contain activities from the mast, turbine and electronics
#### so the lcia using these variables will take into account impacts from mast turbine and electronics
### for 12 m lcia, change 18 to 12


# # Off-grid

# ## For a 18 m mast

# In[18]:


# Scale battery for 18 m energy yield

act_batteries=activities_electronics[3]# activites are concatenated
batteries_key = Database('electronics_wind_turbine_oswacc').search('market for battery, lead acid, rechargeable, stationary', filter={'location':'GLO'})[0].key
batteries_exc = [i for i in act_batteries.exchanges() if i['input'] == batteries_key][0]

batteries_exc.as_dict()['amount'] =  bat_weight_kg[1] 
batteries_exc.save()

activities_18=activities_wt+activities_18m+activities_electronics
order_18 = order_wt | order_18m | order_electronics

activities_18


# In[19]:


batteries_exc


# In[20]:


####COMPUTE LCIA RESULTS FOR ALL METHODS####
score={}
for i in range(len(order_18)): #Cycle through activities
    array_score=np.zeros(len(methods_EF)) #Results are in a np array
    for j in range(len(methods_EF)): # Cycle through methods
        lca = LCA(demand={activities_18[i]:1},
                 method=methods_EF[j])
        lca.lci()
        lca.lcia()
        #score.append(lca.score)
        array_score[j]=lca.score #store result
    score[list(order_18.keys())[i]]=array_score # Store the np.array in the score dictionary for easier handling 



# In[21]:


store_score_18 = pd.DataFrame.from_dict(score,orient='index')
store_score_18
store_score_18.to_csv("lca_12_18/score_18_full_impacts.csv")


# In[22]:


contributions_18={}

for i in range(len(order_18)):
    contributions_18[list(score.keys())[i]]=EF_single_score(score[list(score.keys())[i]],NF,WF)
contributions_18_df=pd.DataFrame.from_dict(contributions_18,orient='index')
contributions_18_df.to_csv("lca_12_18/contributions_18.csv",decimal=",")


# In[23]:


# compute EF 3.0 single score
score_18=np.zeros((len(methods_EF),2))
for i in range(len(methods_EF)): # iterate in categories
   score_18[i,0]=i
   score_18[i,1]=np.sum(store_score_18[i])  # sum of scores for all activities 
score_18


# In[24]:


single_score=EF_single_score(score_18[:,1],NF,WF)
single_score


# In[25]:


scorenorm=np.column_stack((score_18,score_18[:,1]/NF*WF))
scorenorm


# In[26]:


scorenorm=np.column_stack((scorenorm,scorenorm[:,2]/single_score))
scorenorm


# In[27]:


scorenorm_df=pd.DataFrame(scorenorm,columns=['Category number', 'Raw score', 'Normalized_Weighted', 'Score_ratio'])


# In[28]:


I=np.argsort(-scorenorm_df.Score_ratio) #sort descending
score_sort=scorenorm[I,:]


# In[29]:


score_sort=np.column_stack((score_sort,np.zeros(len(methods_EF))))
sum_ratio=0
methods_80=[]
m=0
for i in range(len(methods_EF)):
    sum_ratio+=score_sort[i,3]
    score_sort[i,4]=sum_ratio
    if sum_ratio<0.8:
        m+=1
for i in range(m):
    methods_80.append(methods_EF[int(score_sort[i,0])][1])
print('The methods cumulating at least 80% of impacts are',methods_80)


# In[30]:


score_sort_df=pd.DataFrame(score_sort,columns=['Category_number', 'Raw score', 'Normalized_Weighted', 'Score_ratio', 'Cumulative'])
print(score_sort_df)


# In[31]:


for i in range(len(I)):
    score_sort_df.Category_number[i]=methods_EF[int(I[i])][1]
print(score_sort_df)
score_sort_df.to_csv("lca_12_18/score_18_methods_choice.csv",decimal=",")


# In[32]:


####Select LCIA RESULTS FOR MOST RELEVANT METHODS####

categories_shortlist=5
store_score_18_rec=store_score_18[I[0:categories_shortlist]]


# In[33]:


store_score_18_rec.to_csv("lca_12_18/score_18_V2.csv")

store_score_18_rec


# ## For 12m mast

# In[34]:


# scale battery for energy needs
batteries_exc.as_dict()['amount'] =  bat_weight_kg[0]
batteries_exc.save()


activities_12=activities_wt+activities_12m+activities_electronics
order_12 = order_wt | order_12m | order_electronics

activities_12


# In[35]:


score={}
for i in range(len(order_12)): #Cycle through activities
    array_score=np.zeros(len(methods_EF)) #Results are in a np array
    for j in range(len(methods_EF)): # Cycle through methods
        lca = LCA(demand={activities_12[i]:1},
                 method=methods_EF[j])
        lca.lci()
        lca.lcia()
        #score.append(lca.score)
        array_score[j]=lca.score #store result
    score[list(order_12.keys())[i]]=array_score # Store the np.array in the score dictionary for easier handling 



# In[36]:


store_score_12 = pd.DataFrame.from_dict(score,orient='index')
store_score_12
store_score_12.to_csv("lca_12_18/score_12_full_impacts_v2.csv")


# In[37]:


contributions_12={}
for i in range(len(order_12)):
    contributions_12[list(score.keys())[i]]=EF_single_score(score[list(score.keys())[i]],NF,WF)
contributions_12_df=pd.DataFrame.from_dict(contributions_12,orient='index')
contributions_12_df.to_csv("lca_12_18/contributions_12_V2.csv",decimal=",")


# In[38]:


# compute EF 3.0 single score
score_12=np.zeros((len(methods_EF),2))
for i in range(len(methods_EF)):
   score_12[i,0]=i
   score_12[i,1]=np.sum(store_score_12[i])  
score_12


# In[39]:


single_score=EF_single_score(score_12[:,1],NF,WF)
print('Single score : ', single_score, 'ENF :', single_score/den_kwh[0]/20/365)


# In[40]:


scorenorm=np.column_stack((score_12,score_12[:,1]/NF*WF))
scorenorm


# In[41]:


scorenorm=np.column_stack((scorenorm,scorenorm[:,2]/single_score))
scorenorm


# In[42]:


scorenorm_df=pd.DataFrame(scorenorm,columns=['Category number', 'Raw score', 'Normalized_Weighted', 'Score_ratio'])


# In[43]:


#I=np.argsort(-scorenorm_df.Score_ratio) #sort descending
score_sort=scorenorm[I,:]


# In[44]:


score_sort=np.column_stack((score_sort,np.zeros(len(methods_EF))))
sum_ratio=0
methods_80=[]
m=1
for i in range(len(methods_EF)):
    sum_ratio+=score_sort[i,3]
    score_sort[i,4]=sum_ratio
    if sum_ratio<0.8:
        m+=1
for i in range(m):
    methods_80.append(methods_EF[int(score_sort[i,0])][1])

print('The methods cumulating at least 80% of impacts are',methods_80)


# In[45]:


score_sort_df=pd.DataFrame(score_sort,columns=['Category_number', 'Raw score', 'Normalized_Weighted', 'Score_ratio', 'Cumulative'])


# In[46]:


for i in range(len(I)):
    score_sort_df.Category_number[i]=methods_EF[int(I[i])][1]
print(score_sort_df)
score_sort_df.to_csv("lca_12_18/score_12_methods_choice_V2.csv",decimal=",")


# In[47]:


range(categories_shortlist)


# In[48]:


####Select LCIA RESULTS FOR MOST RELEVANT METHODS####
categories_shortlist=5
store_score_12_rec=store_score_12[I[0:categories_shortlist]]
store_score_12_rec.to_csv("lca_12_18/score_12_V2.csv")


# In[49]:


store_score_12_rec


# In[50]:


score_12=pd.read_csv("lca_12_18/score_12_V2.csv",index_col='Unnamed: 0')
score_12


# In[51]:


score_18=pd.read_csv("lca_12_18/score_18_V2.csv",index_col='Unnamed: 0')
score_18


# In[52]:


####MATPLOTLIB SCRIPT####

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Serif"
})
plt.rcParams['font.size'] = 15


score_12=pd.read_csv("lca_12_18/score_12_V2.csv",index_col='Unnamed: 0')
score_18=pd.read_csv("lca_12_18/score_18_V2.csv",index_col='Unnamed: 0')

fig, ax = plt.subplots(nrows=1,ncols=categories_shortlist, figsize=(42, 6), sharey=False) 

fig.subplots_adjust(wspace=1)  # Adjust the space between subplots
for n in range(categories_shortlist):
    width = 1
    bottom_12 = np.zeros(n+1) ## it just works
    bottom_18 = np.zeros(n+1) ## it just works
    i=0 #index for color and hatch
    hatch=['o','x', '+', '/','O','.','|','o','x','+','/','O','.','o','x', '+', '/','O','.','|' ]

    face_color=['coral','coral','coral','coral','coral','coral','coral','gold','gold','gold','gold','gold','gold','limegreen','limegreen','limegreen','limegreen','limegreen','limegreen','limegreen']
    for (part_12, impacts_12),(part_18, impacts_18) in zip(score_12.iterrows(),score_18.iterrows()):
        impact_12=impacts_12[n]
        impact_18=impacts_18[n]
        p_12 = ax[n].bar('A',impact_12, width, label=part_12, bottom=bottom_12,facecolor=face_color[i],hatch=hatch[i],edgecolor='w')
        p_18 = ax[n].bar('B',impact_18, width, label=part_18, bottom=bottom_18,facecolor=face_color[i],hatch=hatch[i],edgecolor='w')
        bottom_12 += impact_12
        bottom_18+= impact_18
       
        i+=1
    
    plt.subplots_adjust(left=0.45,right=0.65) ## brute force way of craming charts together

    
    ax[n].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax[n].ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))  

    ax[n].set_ylabel(impacts_order[n]+' ('+correspondances[impacts_order[n]]+')')
    
fig.savefig("figures/impacts_12_18_offgrid.svg")
    
plt.show()


# In[53]:


## compute impacts per kwh ##
score_12=pd.read_csv("lca_12_18/score_12_V2.csv",index_col='Unnamed: 0')
score_18=pd.read_csv("lca_12_18/score_18_V2.csv",index_col='Unnamed: 0')
score_kwh_12=score_12.sum(axis=0)
score_kwh_12=score_kwh_12/lue_sc[0].item()
score_kwh_18=score_18.sum(axis=0)
score_kwh_18=score_kwh_18/lue_sc[1].item()

scores_kwh={
    'Categories':impacts_order,
    '12m':score_kwh_12,
    '18m':score_kwh_18
}
scores_kwh_df=pd.DataFrame(scores_kwh)
scores_kwh_df


# In[54]:


# Contribution analysis
score_18.to_csv("lca_12_18/score_18_decimal_V2.csv",decimal=',')


# In[55]:


# generate legend
i=0
fig, ax = plt.subplots(nrows=1,ncols=1, figsize=(2.5, 6), sharey=False) # Creates figure and axis
bottom = 0 ## it just works
for boolean, d in score.items():
    p = ax.bar(' ',1, width, label=boolean, bottom=bottom,facecolor=face_color[i],hatch=hatch[i],edgecolor='w')
   # p2 = ax[1].bar(' ',boolean, width, label=boolean, bottom=bottom,facecolor=face_color[i],hatch=hatch[i],edgecolor='w')
    plt.subplots_adjust(left=0.45,right=0.65) ## brute force way of craming charts together  
    i+=1
    bottom+=1.2
plt.show()
fig.savefig("figures/legend.svg")


# In[56]:


####PLOT IMPACTS/KWH####

df=scores_kwh_df
bar_width = 0.2
index = range(len(df['Categories']))

fig, axes = plt.subplots(nrows=1, ncols=len(df), figsize=(9,4))

for i, (index, row) in enumerate(df.iterrows()):
    ax = axes[i]
    ax.bar(['A', 'B'], [row['12m'], row['18m']])
    ax.set_ylabel(' ('+correspondances_kwh[impacts_order[i]]+')')
    ax.set_ylim(0, 1.05*max(row['12m'], row['18m']))  
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
plt.tight_layout() 
plt.show() 

fig.savefig("figures/impacts_kwh_V2.svg")


# # Grid tied

# ## For a 18 m mast

# In[57]:


activities_electronics_grid[3]


# In[58]:


# Scale grid electricity for 18 m energy yield

act_grid=activities_electronics_grid[3]# activites are concatenated
grid_key = Database('electronics_wind_turbine_oswacc').search('market group for electricity, low voltage')[0].key
grid_exc = [i for i in act_grid.exchanges() if i['input'] == grid_key][0]

grid_exc.as_dict()['amount'] =  leg[1] 
grid_exc.save()

activities_18_grid=activities_wt+activities_18m+activities_electronics_grid
order_18_grid = order_wt | order_18m | order_electronics_grid

activities_18_grid


# In[59]:


grid_exc


# In[60]:


####COMPUTE LCIA RESULTS FOR ALL METHODS####
score={}
for i in range(len(order_18_grid)): #Cycle through activities
    array_score=np.zeros(len(methods_EF)) #Results are in a np array
    for j in range(len(methods_EF)): # Cycle through methods
        lca = LCA(demand={activities_18_grid[i]:1},
                 method=methods_EF[j])
        lca.lci()
        lca.lcia()
        #score.append(lca.score)
        array_score[j]=lca.score #store result
    score[list(order_18_grid.keys())[i]]=array_score # Store the np.array in the score dictionary for easier handling 



# In[61]:


store_score_18_grid = pd.DataFrame.from_dict(score,orient='index')
store_score_18_grid
store_score_18_grid.to_csv("lca_12_18/score_18_grid_full_impacts.csv")


# In[62]:


contributions_18_grid={}

for i in range(len(order_18_grid)):
    contributions_18_grid[list(score.keys())[i]]=EF_single_score(score[list(score.keys())[i]],NF,WF)
contributions_18_grid_df=pd.DataFrame.from_dict(contributions_18_grid,orient='index')
contributions_18_grid_df.to_csv("lca_12_18/contributions_18_grid.csv",decimal=",")


# In[63]:


# compute EF 3.0 single score
score_18_grid=np.zeros((len(methods_EF),2))
for i in range(len(methods_EF)): # iterate in categories
   score_18_grid[i,0]=i
   score_18_grid[i,1]=np.sum(store_score_18_grid[i])  # sum of scores for all activities 
score_18_grid


# In[64]:


single_score=EF_single_score(score_18_grid[:,1],NF,WF)
scorenorm=np.column_stack((score_18_grid,score_18_grid[:,1]/NF*WF))
scorenorm


# In[65]:


scorenorm=np.column_stack((scorenorm,scorenorm[:,2]/single_score))
scorenorm


# In[66]:


scorenorm_df=pd.DataFrame(scorenorm,columns=['Category number', 'Raw score', 'Normalized_Weighted', 'Score_ratio'])


# In[67]:


I=np.argsort(-scorenorm_df.Score_ratio) #sort descending
score_sort=scorenorm[I,:]


# In[68]:


score_sort=np.column_stack((score_sort,np.zeros(len(methods_EF))))
sum_ratio=0
methods_80=[]
m=0
for i in range(len(methods_EF)):
    sum_ratio+=score_sort[i,3]
    score_sort[i,4]=sum_ratio
    if sum_ratio<0.8:
        m+=1
for i in range(m):
    methods_80.append(methods_EF[int(score_sort[i,0])][1])
print('The methods cumulating at least 80% of impacts are',methods_80)


# In[69]:


score_sort_df=pd.DataFrame(score_sort,columns=['Category_number', 'Raw score', 'Normalized_Weighted', 'Score_ratio', 'Cumulative'])
print(score_sort_df)


# In[70]:


for i in range(len(I)):
    score_sort_df.Category_number[i]=methods_EF[int(I[i])][1]
print(score_sort_df)
score_sort_df.to_csv("lca_12_18/score_18_grid_methods_choice.csv",decimal=",")


# In[71]:


####Select LCIA RESULTS FOR MOST RELEVANT METHODS####

categories_shortlist=5
store_score_18_grid_rec=store_score_18_grid[I[0:categories_shortlist]]


# In[72]:


store_score_18_grid_rec.to_csv("lca_12_18/score_18_grid_V2.csv")

store_score_18_grid_rec


# ## For 12m mast

# In[73]:


# scale grid energy for energy needs
grid_exc.as_dict()['amount'] =  leg[0] 
grid_exc.save()


activities_12_grid =activities_wt+activities_12m+activities_electronics_grid
order_12_grid = order_wt | order_12m | order_electronics_grid

activities_12_grid


# In[74]:


score={}
for i in range(len(order_12_grid)): #Cycle through activities
    array_score=np.zeros(len(methods_EF)) #Results are in a np array
    for j in range(len(methods_EF)): # Cycle through methods
        lca = LCA(demand={activities_12_grid[i]:1},
                 method=methods_EF[j])
        lca.lci()
        lca.lcia()
        #score.append(lca.score)
        array_score[j]=lca.score #store result
    score[list(order_12_grid.keys())[i]]=array_score # Store the np.array in the score dictionary for easier handling 



# In[75]:


store_score_12_grid = pd.DataFrame.from_dict(score,orient='index')
store_score_12_grid
store_score_12_grid.to_csv("lca_12_18/score_12_grid_full_impacts_v2.csv")


# In[76]:


contributions_12_grid={}
for i in range(len(order_12_grid)):
    contributions_12_grid[list(score.keys())[i]]=EF_single_score(score[list(score.keys())[i]],NF,WF)
contributions_12_grid_df=pd.DataFrame.from_dict(contributions_12_grid,orient='index')
contributions_12_grid_df.to_csv("lca_12_18/contributions_12_grid_V2.csv",decimal=",")


# In[77]:


# compute EF 3.0 single score
score_12_grid=np.zeros((len(methods_EF),2))
for i in range(len(methods_EF)):
   score_12_grid[i,0]=i
   score_12_grid[i,1]=np.sum(store_score_12_grid[i])  
score_12_grid


# In[78]:


single_score=EF_single_score(score_12_grid[:,1],NF,WF)
scorenorm=np.column_stack((score_12_grid,score_12_grid[:,1]/NF*WF))
scorenorm


# In[79]:


scorenorm=np.column_stack((scorenorm,scorenorm[:,2]/single_score))
scorenorm


# In[80]:


scorenorm_df=pd.DataFrame(scorenorm,columns=['Category number', 'Raw score', 'Normalized_Weighted', 'Score_ratio'])


# In[81]:


#I=np.argsort(-scorenorm_df.Score_ratio) #sort descending
score_sort=scorenorm[I,:]


# In[82]:


score_sort=np.column_stack((score_sort,np.zeros(len(methods_EF))))
sum_ratio=0
methods_80=[]
m=1
for i in range(len(methods_EF)):
    sum_ratio+=score_sort[i,3]
    score_sort[i,4]=sum_ratio
    if sum_ratio<0.8:
        m+=1
for i in range(m):
    methods_80.append(methods_EF[int(score_sort[i,0])][1])

print('The methods cumulating at least 80% of impacts are',methods_80)


# In[83]:


score_sort_df=pd.DataFrame(score_sort,columns=['Category_number', 'Raw score', 'Normalized_Weighted', 'Score_ratio', 'Cumulative'])


# In[84]:


for i in range(len(I)):
    score_sort_df.Category_number[i]=methods_EF[int(I[i])][1]
print(score_sort_df)
score_sort_df.to_csv("lca_12_18/score_12_grid_methods_choice_V2.csv",decimal=",")


# In[85]:


####Select LCIA RESULTS FOR MOST RELEVANT METHODS####
categories_shortlist=5
store_score_12_grid_rec=store_score_12_grid[I[0:categories_shortlist]]
store_score_12_grid_rec.to_csv("lca_12_18/score_12_grid_V2.csv")


# In[86]:


store_score_12_grid_rec


# In[87]:


score_12_grid=pd.read_csv("lca_12_18/score_12_grid_V2.csv",index_col='Unnamed: 0')
score_12_grid


# In[88]:


score_18_grid=pd.read_csv("lca_12_18/score_18_grid_V2.csv",index_col='Unnamed: 0')
score_18_grid


# In[89]:


####MATPLOTLIB SCRIPT####

plt.rcParams.update({
    "text.usetex": True,
    "font.family": "Serif"
})
plt.rcParams['font.size'] = 15


score_12=pd.read_csv("lca_12_18/score_12_grid_V2.csv",index_col='Unnamed: 0')
score_18=pd.read_csv("lca_12_18/score_18_grid_V2.csv",index_col='Unnamed: 0')

fig, ax = plt.subplots(nrows=1,ncols=categories_shortlist, figsize=(42, 6), sharey=False) # Creates figure and axis

fig.subplots_adjust(wspace=1)  
for n in range(categories_shortlist):
    width = 1
    bottom_12 = np.zeros(n+1) ## it just works
    bottom_18 = np.zeros(n+1) ## it just works
    i=0 #index for color and hatch
    hatch=['o','x', '+', '/','O','.','|','o','x','+','/','O','.','o','x', '+', '/','O','.','|' ]

    face_color=['coral','coral','coral','coral','coral','coral','coral','gold','gold','gold','gold','gold','gold','limegreen','limegreen','limegreen','limegreen','limegreen','limegreen','limegreen']
    for (part_12, impacts_12),(part_18, impacts_18) in zip(score_12.iterrows(),score_18.iterrows()):
        impact_12=impacts_12[n]
        impact_18=impacts_18[n]
        p_12 = ax[n].bar('A',impact_12, width, label=part_12, bottom=bottom_12,facecolor=face_color[i],hatch=hatch[i],edgecolor='w')
        p_18 = ax[n].bar('B',impact_18, width, label=part_18, bottom=bottom_18,facecolor=face_color[i],hatch=hatch[i],edgecolor='w')
        bottom_12 += impact_12
        bottom_18+= impact_18

        i+=1
    

    plt.subplots_adjust(left=0.45,right=0.65) ## brute force way of craming charts together


    ax[n].yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax[n].ticklabel_format(axis='y', style='sci', scilimits=(-2, 2)) 

    ax[n].set_ylabel(impacts_order_grid[n]+' ('+correspondances[impacts_order_grid[n]]+')')
    
fig.savefig("figures/impacts_12_18_grid.svg")
plt.show()


# In[90]:


## compute impacts per kwh ##
score_12=pd.read_csv("lca_12_18/score_12_grid_V2.csv",index_col='Unnamed: 0')
score_18=pd.read_csv("lca_12_18/score_18_grid_V2.csv",index_col='Unnamed: 0')
score_kwh_12=score_12.sum(axis=0)
score_kwh_12=score_kwh_12/lue_grid[0].item()
score_kwh_18=score_18.sum(axis=0)
score_kwh_18=score_kwh_18/lue_grid[1].item()

scores_kwh={
    'Categories':impacts_order_grid[0:5],
    '12m':score_kwh_12,
    '18m':score_kwh_18
}
scores_kwh_df=pd.DataFrame(scores_kwh)
scores_kwh_df


# In[91]:


# Contribution analysis
score_18.to_csv("lca_12_18/score_18_grid_decimal_V2.csv",decimal=',')


# In[92]:


# generate legend
i=0
fig, ax = plt.subplots(nrows=1,ncols=1, figsize=(2.5, 6), sharey=False) # Creates figure and axis
bottom = 0 ## it just works
for boolean, d in score.items():
    p = ax.bar(' ',1, width, label=boolean, bottom=bottom,facecolor=face_color[i],hatch=hatch[i],edgecolor='w')
   # p2 = ax[1].bar(' ',boolean, width, label=boolean, bottom=bottom,facecolor=face_color[i],hatch=hatch[i],edgecolor='w')
    plt.subplots_adjust(left=0.45,right=0.65) ## brute force way of craming charts together  
    i+=1
    bottom+=1.2
plt.show()
fig.savefig("figures/legend.svg")


# In[93]:


####PLOT IMPACTS/KWH####

df=scores_kwh_df
bar_width = 0.2
index = range(len(df['Categories']))

# Creating subplots for each category
fig, axes = plt.subplots(nrows=1, ncols=len(df), figsize=(9,4))

# Plotting each category with different y-axis limits
for i, (index, row) in enumerate(df.iterrows()):
    ax = axes[i]
    ax.bar(['A', 'B'], [row['12m'], row['18m']])
    ax.set_ylabel(' ('+correspondances_kwh[impacts_order_grid[i]]+')')
    ax.set_ylim(0, 1.05*max(row['12m'], row['18m']))  # Setting different y-axis limits for each category
    ax.yaxis.set_major_formatter(ScalarFormatter(useMathText=True))
    ax.ticklabel_format(axis='y', style='sci', scilimits=(-2, 2))
plt.tight_layout()  # To ensure the subplots are properly arranged
plt.show()  # Display the plot

fig.savefig("figures/impacts_kwh_grid.svg")


# # Sizing of the mast

# Until now the LCIA results were growing linearly with respect to the mast length. We now want to take into account the real dimensions of the mast. The three dimensions modified are the outer diameter of the steel tube, the diameter of the the steel guys and the area of wire to coat in zinc. 

# ## Guy wire

# ### Cable section

# To verify the cable diameter, we first need the Force exerted by the wind on the wind turbine hub $F_{wind}$. We can then compute the force exerted on the cable $F_\alpha$.
# 
# $F_{wind}=\cos(\alpha)F_\alpha$
# 
# with : 
# 
# $\alpha = 60°$ the angle formed between the cable and the ground.

# This part of the code displays the relationship between the cable section and the maximum break force according to the datasheet. It also defines the number of samples $n$ used throughout our code for the LCA.

# In[94]:


import numpy as np

import matplotlib as mpl

import matplotlib.pyplot as plt

#plt.rcParams['text.usetex'] = True
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.size'] = 15
####From datasheet####

#Diameters included in the datasheet
Diameter = np.array([3,3.5,4,5,6,8,9,10,12])
Diameter = Diameter/1000
Section = np.pi*(Diameter/2)**2

# number of samples n
n = 12


# $S_{real}=S_{eq}\times k$
# 
# with $k$ the fill factor in our case $ k = 0,51$

# For the LCA we will need the Section of cable and its length depending on the mast length
# 
# $S_{real}=\frac{k c_{sec}}{a}\left(\frac{F_{wind}(L)}{\cos(\alpha)}-b\right)$

# with : 
# 
# $c_{sec}$ the safety coefficient
# 
# $k$ the fill factor
# 
# $L$ the mast length

# ### Cable length

# For the length of the top guy wires $L_c$, we have : 
# 
# $L_c = \frac{4L}{\sin(\alpha)} = \frac{8L}{\sqrt3}$

# Smaller cable are used to strengthen the mast tube with a diameter considered constant of 6 mm. They are connected to the same anchorage as the top cable but they are connected to the mast at 6 m, 12 m and 18 m with a length of $\lambda_1$, $\lambda_2$ and $\lambda_3$.

# $\lambda_1 = 4\sqrt{\left(\frac{L}{2}\right)^2+6^2}$

# $\lambda_2 = 4\sqrt{\left(\frac{L}{2}\right)^2+12^2}$
# 

# $\lambda_3 = 4\sqrt{\left(\frac{L}{2}\right)^2+18^2}$
# 

# The smaller cables have a Section of 6 mm noted $S_{6mm}$

# $S_{6mm} = k \pi \left(\frac{0,006}{2}\right)^2 = 1,44\times10^{-5} $ m²

# We can now compute the mass of steel used for the cables

# $m_{cable}= \rho_{steel} \left(L_c S+\lambda_1 S_{6mm}+\lambda_2 S_{6mm}+\lambda_3 S_{6mm}\right)$

# $m_{cable}= \rho_{steel} \left(\frac{8L}{\sqrt3} \frac{k c_{sec}}{a}\left(\frac{F_{wind}(L)}{\cos(\alpha)}-b\right)+4\sqrt{\left(\frac{L}{2}\right)^2+6^2} \times S_{6mm}+4\sqrt{\left(\frac{L}{2}\right)^2+12^2} \times S_{6mm}  +4\sqrt{\left(\frac{L}{2}\right)^2+18^2} \times S_{6mm}\right)$

# In this code we compute the mass of cable twice because we do it once analytically with continuous diameters and once for the actual build with discrete diameters. The discrete version takes into account the third layer of wire.

# In[95]:


#fill factor
k = 0.51
#section of wire in mm^2
S_6 = k*np.pi * (0.006/2)**2
#This coefficient between 0 an 1 defines at which point between 12 and 18 do we add a third layer of cable
coef_add_cable = 0.5

Length = np.array([12, 18, 24])
l_wire=np.zeros(3)
m_wire=np.zeros(3)

#mild steel density
rho = 7850

lambda_6=4 * np.sqrt((12/2)**2+(6)**2)

for i,L in enumerate(Length):
    lambda_12=4 * np.sqrt((L/2)**2+(12)**2)
    if L>12 : 
        lambda_18=4 * np.sqrt((L/2)**2+(18)**2) 
    else:
        lambda_18=0
    if L>18 : 
        lambda_24=4 * np.sqrt((L/2)**2+(24)**2) 
    else:
        lambda_24=0  
    l_wire[i]=(lambda_6+lambda_12+lambda_18+lambda_24)
    m_wire[i] =rho * S_6 * l_wire[i]

m_wire_fit=np.polyfit(Length,m_wire,1)


# In[96]:


l_wire


# In[97]:


fig, ax = plt.subplots()


ax.set_xlabel('Tower height (m)')
ax.set_ylabel('Cable mass (kg)')


ax.scatter(Length,m_wire)
ax.plot(Length,np.polyval(m_wire_fit,Length))
ax.grid(True)


# ### Cable area

# We also need to compute the surface area coated in zinc. Our cables are manufactured using 6 thread of 19 steel wires therefore for our model of the coationg process we decided that all wires were coated as individual cables. Each single wire is 15 times smaller than the nominal diameter of the cable.
# 
# The coated area per meter of cable $A_m$ is therefore
# 
# $A_m = \frac{19\times 6\times \pi D}{15}$

# In[98]:


D = 0.006
A = ((19*6*np.pi*D)/(15))*l_wire
area_coat_fit=np.polyfit(Length,A,1)


# In[99]:


fig, ax = plt.subplots()


ax.set_xlabel('Tower height (m)')
ax.set_ylabel('Zinc coating area (m²)')

ax.scatter(Length,A,label='Discrete')
ax.plot(Length,np.polyval(area_coat_fit,Length))
ax.legend()
ax.grid(True)


# ## Mast pipe

# In[100]:


from sympy import *
init_printing(use_unicode=True)
e,rho,L,a,b = symbols('e,rho,L,a,b')
mu,D,m = symbols ('mu,D,m',cls=Function)
D=a*L+b
mu = rho* pi*((D/2)**2-((D-2*e)/2)**2)
m=L*mu

print(latex(factor(m)))
factor(m)


# $m(L)=\pi L e \rho \left(L a + b - e\right)=KL(AL+B)$ with $K=\pi e \rho$, $A=a$ and $B=b-e$

# In[101]:


del(e,rho,L,a,b,mu,D,m)


# ### Mast

# In[102]:


rho = 7850
D = np.array([88.9,114.3,114.3])*1e-3
e = 3.2e-3
mu = rho* np.pi*((D/2)**2-((D-2*e)/2)**2)
L=np.linspace(12,24,200)


# In[103]:


D_fit=np.polyfit(Length,D,1)
m_fit=np.polyfit(Length,mu*Length,2)
mu_fit_lin = rho* np.pi*((np.polyval(D_fit,L)/2)**2-((np.polyval(D_fit,L)-2*e)/2)**2)
m_fit_mu=np.pi*e*rho*L*(np.polyval(D_fit,L)-e)


# In[104]:


fig, ax = plt.subplots()
ax.set_title('Tube diameter per length of tube')
ax.set_xlabel('L (m)')
ax.set_ylabel('Diameter (m)')

ax.scatter(Length,D, label='Diameter real')
ax.plot(Length,np.polyval(D_fit,Length), label='Diameter fit')
ax.legend()
plt.show()


# In[105]:


fig, ax = plt.subplots()
ax.set_title('Tube mass per length of tube')
ax.set_xlabel('L (m)')
ax.set_ylabel('Mass (kg)')
ax.scatter(Length,mu*Length, label='mass real')
ax.plot(L,np.polyval(m_fit,L),label='mass fit')
ax.plot(L,L*mu_fit_lin,label='diameter fit')
ax.plot(L,m_fit_mu,label='diameter fit2')
ax.legend()
ax.grid(True)
plt.show()


# The mass fit is more representative of what is done on the field with the manual. However, it is obvious that the 18m mast diameter is over dimensionned since it is the same that for the 24 m mast. It is more physically realistic to choose the mass obtained from the linear interpolation of tube diameters for the present study.

# ### Yaw pipe

# The yaw pipe helps raising the tower when it is lowered. In the handbook it is narrower than the mast and it measures half of its length. For the 12m tower the yaw pipe has an outter diameter of $D = 60,3$ $ mm $ and a thickness $ e = 2,9$ $mm$. For the 18m tower $D = 88,9$ $ mm $ and $ e = 3,2$ $mm$.

# $ \frac{\rho_{acier} L}{2}   \times \pi\left(\left(\frac{D}{2}\right)^2-\left(\frac{D-2e}{2}\right)^2\right)$

# In[106]:


e_yaw2 = 0.0032
D_yaw2 = 0.0889

e_yaw1 = 0.0029
D_yaw1 = 0.0603

e_yaw=np.array([e_yaw1, e_yaw2, e_yaw2])
D_yaw=np.array([D_yaw1, D_yaw2, D_yaw2])

D_yaw_fit=np.polyfit(Length,D_yaw,1)
e_yaw_fit=np.polyfit(Length,e_yaw,1)

m_yaw_fit=np.pi*np.polyval(e_yaw_fit,L)*rho*L/2*(np.polyval(D_yaw_fit,L)-np.polyval(e_yaw_fit,L))
m_yaw_real=Length/2*rho*np.pi*((D_yaw/2)**2-((D_yaw-2*e_yaw)/2)**2)


# In[107]:


fig, ax = plt.subplots()

ax.set_xlabel(r'Tower height (m)')
ax.set_ylabel(r'Yaw pipe mass (kg)')

ax.scatter(Length,m_yaw_real,label='real')
ax.plot(L,m_yaw_fit,label='fit')

ax.grid(True)
ax.legend()


# In[108]:


def tower_steel_tube_mass(L):
    e_yaw2 = 0.0032
    D_yaw2 = 0.0889

    e_yaw1 = 0.0029
    D_yaw1 = 0.0603

    e_yaw=np.array([e_yaw1, e_yaw2, e_yaw2])
    D_yaw=np.array([D_yaw1, D_yaw2, D_yaw2])

    D_yaw_fit=np.polyfit(Length,D_yaw,1)
    e_yaw_fit=np.polyfit(Length,e_yaw,1)
    
    rho = 7850
    D = np.array([88.9,114.3,114.3])*1e-3
    e = 3.2e-3
    mu = rho* np.pi*((D/2)**2-((D-2*e)/2)**2)

    m_yaw=np.pi*np.polyval(e_yaw_fit,L)*rho*L/2*(np.polyval(D_yaw_fit,L)-np.polyval(e_yaw_fit,L))
    m_mast=np.pi*e*rho*L*(np.polyval(D_fit,L)-e)
    return m_yaw+m_mast


# In[109]:


fig, ax = plt.subplots()
#ax.set_title('Yaw pipe mass for length of mast tube')
ax.set_xlabel(r'Tower height (m)')
ax.set_ylabel(r'Tower steel mass (kg)')
#ax.plot(L_corrected,m_tube,label='analytic')
ax.plot(L,tower_steel_tube_mass(L)+np.polyval(m_wire_fit,L))
ax.grid(True)
fig.savefig("figures/tow_steel.svg")


# ## Conclusion

# From these we gathered three information, the mass of cable, the mass of tube and the area of cable.

# # Back to LCIA

# In[110]:


# Separate constant actitivities from scalable activities

order_cst_tower= dict(order_12m)
order_cst_tower.pop("12m steel no zinc")
order_cst_tower.pop("12m zinc")
order_cst_tower.pop("12m cable")
order_cst_tower.pop("12m transport steel")
order_cst_elec=dict(order_electronics)
order_cst_elec.pop("electronics batteries")

order_cst=order_wt|order_cst_tower|order_cst_elec
print(order_cst)

order_tower=dict(order_12m)
order_tower.pop("12m concrete")
order_tower.pop("12m transport concrete")
print(order_tower)

activities_cst=[Database('12m_wind_turbine').search(j)[0] for (i,j) in order_wt.items()]+[Database('12m_mast').search(j)[0] for (i,j) in order_cst_tower.items()]+[Database('electronics_wind_turbine_oswacc').search(j)[0] for (i,j) in order_cst_elec.items()]
print(activities_cst)
activities_batteries = [act_batteries]
print(activities_batteries)
activities_tower = [Database('12m_mast').search(j)[0] for (i,j) in order_tower.items()]
print(activities_tower)
activities_tow_cst=[Database('12m_mast').search(j)[0] for (i,j) in order_cst_tower.items()]
print(activities_tow_cst)


# In[111]:


#### Calculate constant single score ####
 
cst_score=lca_single_score(activities_cst,methods_EF,NF,WF)


# In[112]:


#### Calculate batteries single score ####
bat_score=lca_single_score(activities_batteries,methods_EF,NF,WF)


# In[113]:


tow_score=lca_single_score(activities_tower,methods_EF,NF,WF)


# In[114]:


tow_score_cst=lca_single_score(activities_tow_cst,methods_EF,NF,WF)


# In[115]:


# check single score
print(cst_score+bat_score+tow_score)
print(tow_score_cst)


# In[116]:


####SETTING VARIABLE HEIGHT####
# this defines the variable for our analysis it can also be an np.linspace

height=np.linspace(12,24,n)
tow_score=np.zeros(n)
tow_score_dict={'mast_length':height,'tower_score':tow_score}
# this dataframe contains all the scenarios, one for each height
tow_score_df = pd.DataFrame(tow_score_dict)


# In[117]:


####SETTING QUANTITIES TO CHANGE####

# this process allows to update the value of each exchange when our height increases
act_steel=activities_12[7] # storing the activity name

# identifying in the ecoinvent DB the key corresponding to the exchange
pipe_key = Database('ecoinvent3.8-cut-off').search('drawing of pipe, steel', filter={'location':'RER'})[0].key 
# storing the exchange in a new variable
pipe_exc = [i for i in act_steel.exchanges() if i['input'] == pipe_key][0]

steel_ua_key = Database('ecoinvent3.8-cut-off').search('steel production, converter, unalloyed', filter={'location':'RER'})[0].key
steel_ua_exc =[i for i in act_steel.exchanges() if i['input'] == steel_ua_key][0]

wire_steel_key = Database('ecoinvent3.8-cut-off').search('wire drawing, steel', filter={'location':'RER'})[0].key
wire_steel_exc = [i for i in act_steel.exchanges() if i['input'] == wire_steel_key][0]


# We repeat for  zinc and cable activities
act_zinc=activities_12[9]

zinc_key = Database('ecoinvent3.8-cut-off').search('zinc coating, coils', filter={'location':'RER'})[0].key
zinc_exc = [i for i in act_zinc.exchanges() if i['input'] == zinc_key][0]

act_cable=activities_12[10]

copper_key=Database('ecoinvent3.8-cut-off').search('market for copper, cathode', filter={'location':'GLO'})[0].key
copper_exc = [i for i in act_cable.exchanges() if i['input'] == copper_key][0]

wire_key=Database('ecoinvent3.8-cut-off').search('wire drawing, copper', filter={'location':'RER'})[0].key
wire_exc = [i for i in act_cable.exchanges() if i['input'] == wire_key][0]

polyethylene_key=Database('ecoinvent3.8-cut-off').search('polyethylene production, high density, granulate', filter={'location':'RER'})[0].key
polyethylene_exc = [i for i in act_cable.exchanges() if i['input'] == polyethylene_key][0]

extrusion_key = Database('ecoinvent3.8-cut-off').search('extrusion, plastic pipes', filter={'location':'RER'})[0].key
extrusion_exc = [i for i in act_cable.exchanges() if i['input'] == extrusion_key][0]

act_batteries=activities_12[16]

batteries_key = Database('electronics_wind_turbine_oswacc').search('market for battery, lead acid, rechargeable, stationary', filter={'location':'GLO'})[0].key
batteries_exc = [i for i in act_batteries.exchanges() if i['input'] == batteries_key][0]

act_transport_steel=activities_12[12]

lorry_steel_key = Database('ecoinvent3.8-cut-off').search('market for transport, freight, lorry, unspecified', filter={'location':'RER'})[0].key
lorry_steel_exc = [i for i in act_transport_steel.exchanges() if i['input'] == lorry_steel_key][0]

train_steel_key = Database('ecoinvent3.8-cut-off').search('market group for transport, freight train', filter={'location':'RER'})[0].key
train_steel_exc = [i for i in act_transport_steel.exchanges() if i['input'] == train_steel_key][0]

container_steel_key = Database('ecoinvent3.8-cut-off').search('market for transport, freight, sea, container ship', filter={'location':'GLO'})[0].key
container_steel_exc = [i for i in act_transport_steel.exchanges() if i['input'] == container_steel_key][0]


# In[ ]:


##LOOP WITH INCREMENTATION OF MAST LENGTH
for i_h in tow_score_df.index: #i_h is the height index
    
    ##DEFINE NEW QUANTITIES FOR EXCHANGES
    # changes the value of the exchange
    pipe_exc.as_dict()['amount'] = 0.48*8.75483+tower_steel_tube_mass(height[i_h])
    # saves the new value
    pipe_exc.save()
    steel_ua_exc.as_dict()['amount'] = 0.48*8.75483+tower_steel_tube_mass(height[i_h])+np.polyval(m_wire_fit,height[i_h])
    steel_ua_exc.save()
    wire_steel_exc.as_dict()['amount'] = np.polyval(m_wire_fit,height[i_h])
    wire_steel_exc.save()
    
    zinc_exc.as_dict()['amount'] = np.polyval(area_coat_fit,height[i_h])
    zinc_exc.save()
    
    copper_exc.as_dict()['amount'] = tow_score_df.loc[i_h, 'mast_length']*8960*3*0.000004
    copper_exc.save()
    wire_exc.as_dict()['amount'] =tow_score_df.loc[i_h, 'mast_length']*8960*3*0.000004
    wire_exc.save()
    polyethylene_exc.as_dict()['amount'] = 0.011848*tow_score_df.loc[i_h, 'mast_length']
    polyethylene_exc.save()
    extrusion_exc.as_dict()['amount'] =  0.011848*tow_score_df.loc[i_h, 'mast_length']
    extrusion_exc.save()
    
    # scaling of transport
    lorry_steel_exc.as_dict()['amount'] =  25/12*tow_score_df.loc[i_h, 'mast_length']
    lorry_steel_exc.save()
    train_steel_exc.as_dict()['amount'] =  25.3/12*tow_score_df.loc[i_h, 'mast_length']
    train_steel_exc.save()
    container_steel_exc.as_dict()['amount'] =  56/12*tow_score_df.loc[i_h, 'mast_length']
    container_steel_exc.save()
    
    tow_score_df.loc[i_h,('tower_score')]=lca_single_score(activities_tower,methods_EF,NF,WF)
    
        
# we can restore the default value at the end
pipe_exc.as_dict()['amount'] = 0.48*8.75483+tower_steel_tube_mass(12)
pipe_exc.save()
steel_ua_exc.as_dict()['amount'] = 0.48*8.75483+tower_steel_tube_mass(12)+11.246
steel_ua_exc.save()
wire_steel_exc.as_dict()['amount'] = 11.246
wire_steel_exc.save()
    
zinc_exc.as_dict()['amount'] = 14.32
zinc_exc.save()

copper_exc.as_dict()['amount'] = 12*8960*3*0.000004
copper_exc.save()
wire_exc.as_dict()['amount'] =12*8960*3*0.000004
wire_exc.save()
polyethylene_exc.as_dict()['amount'] = 0.011848*12
polyethylene_exc.save()
extrusion_exc.as_dict()['amount'] =  0.011848*12
extrusion_exc.save()
batteries_exc.as_dict()['amount'] =  bat_weight_kg[0]
batteries_exc.save()
lorry_steel_exc.as_dict()['amount'] =  25
lorry_steel_exc.save()
train_steel_exc.as_dict()['amount'] =  25.3
train_steel_exc.save()
container_steel_exc.as_dict()['amount'] =  56
container_steel_exc.save()


# In[ ]:


tow_score_df


# In[ ]:


tow_score_df.to_csv("lca_scale/tower_score_height.csv")


# In[ ]:


tow_score_df=pd.read_csv("lca_scale/tower_score_height.csv")


# In[ ]:


tow_score_fit=np.polyfit(tow_score_df['mast_length'],tow_score_df['tower_score'],1)


# In[ ]:


tow_score_fit


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('Tower height (m)')
ax.set_ylabel('Tower score (Pt)')
ax.scatter(tow_score_df['mast_length'],tow_score_df['tower_score']+tow_score_cst,linewidth = 1,label="score")
ax.plot(tow_score_df['mast_length'],np.polyval(tow_score_fit,tow_score_df['mast_length'])+tow_score_cst,linewidth = 1,label="fit")
ax.legend()
ax.grid(True)
plt.show()
fig.savefig("figures/tow_score.svg")


# In[ ]:


#### Battery impacts array #### 
N_d=2
SoC_min=0.5

oversizing_factor=0.15 # Average proportion of energy being lost in dump load
load_shifting_factor=0.2 
grid_injection_factor=0
storage_factor=1-oversizing_factor-load_shifting_factor-grid_injection_factor

v_mu=np.arange(3.5,8,0.5)
aep=np.polyval(aep_poly,v_mu)

#lifetime useful energy (from article, eq. 5)
den_kwh_sc=aep/365*inverter_efficiency*(grid_injection_factor+storage_factor*battery_efficiency+load_shifting_factor)
bat_cap_kwh_sc=den_kwh_sc*N_d/(SoC_min*inverter_efficiency)
bat_weight_kg_sc=np.polyval(bat_fit,bat_cap_kwh_sc)

bat_score_df = pd.DataFrame({'AEP':aep, 'DEN':den_kwh_sc, 'Cap':bat_cap_kwh_sc, 'Weight':bat_weight_kg_sc, 'Score':np.zeros(len(aep))})



# In[ ]:





# In[ ]:


bat_score_df


# In[ ]:


for i,wt in enumerate(bat_score_df['Weight']):
    batteries_exc.as_dict()['amount'] = wt
    batteries_exc.save()
    bat_score_df['Score'][i]=lca_single_score(activities_batteries,methods_EF,NF,WF)
batteries_exc.as_dict()['amount'] =  bat_weight_kg[0]
batteries_exc.save()    


# In[ ]:


bat_score_df


# In[ ]:


bat_score_df.to_csv("lca_scale/battery_score.csv")


# In[ ]:


bat_score_df=pd.read_csv("lca_scale/battery_score.csv")
bat_score_fit=np.polyfit(bat_score_df['Weight'],bat_score_df['Score'],1)
bat_score_fit_cap=np.polyfit(bat_score_df['Cap'],bat_score_df['Score'],1)
bat_score_fit


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('Battery capacity (kWh)')
ax.set_ylabel('Battery score (Pt)')
ax.scatter(bat_score_df['Cap'],bat_score_df['Score'],linewidth = 0.5, label='score')
ax.plot(bat_score_df['Cap'],np.polyval(bat_score_fit_cap,bat_score_df['Cap']),label='fit')
ax.legend()
ax.grid(True)
plt.show()
fig.savefig("figures/bat_score.svg")


# ## Find score of a grid kwh
# 

# In[ ]:


act_electricity = [Database('grid').search('grid_electricity')[0]]
act_kwh = [Database('grid').search('market group for electricity, low voltage')[0]]
kwh_key = Database('grid').search('market group for electricity, low voltage')[0].key
kwh_exc = [i for i in act_kwh[0].exchanges() if i['input'] == kwh_key][0]


# In[ ]:


kwh_score=lca_single_score(act_electricity,methods_EF,NF,WF)


# In[ ]:


kwh_exc


# In[ ]:


num_kwh=np.arange(1,11,1)


# In[ ]:


score_kwh=np.zeros([10])
for i,j in enumerate(num_kwh):
    kwh_exc.as_dict()['amount'] = 1/j
    kwh_exc.save()
    score_kwh[i]=lca_single_score(act_kwh,methods_EF,NF,WF)
kwh_exc.as_dict()['amount'] = 1   
kwh_exc.save()


# In[ ]:


kwh_score_fit=np.polyfit(num_kwh,score_kwh,1)


# In[ ]:


kwh_score_fit


# In[ ]:


kwh_score_fit=np.array([ 4.62102624e-05, -3.21340547e-13])


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('(kWh)')
ax.set_ylabel('score (Pt)')
ax.scatter(num_kwh,score_kwh,linewidth = 0.5, label='score')
ax.plot(num_kwh,np.polyval(kwh_score_fit,num_kwh),label='fit')
ax.legend()
ax.grid(True)
plt.show()


# ## Height Optimization

# In[ ]:


### System modelling in sympy ###
import sympy as sp
# Wind speed
z_0, h_r, V_r, h = sp.symbols('z_0 h_r V_r h',positive=true)
V_h = V_r*sp.log(h/z_0)/sp.log(h_r/z_0)

V_h


# In[ ]:


# Annual Energy Production
np_aep_poly= np.poly1d(aep_poly)
AEP = sp.Poly(np_aep_poly.coeffs,V_h)
E_p = AEP/sp.sympify(365)


# In[ ]:


# Daily Energy Needs
eta_b, eta_i, F_s, F_ls, F_os =sp.symbols('eta_b eta_i F_s F_ls F_os',positive=true)
F_s=1-F_ls-F_os
E_n = E_p*eta_i*(F_ls+F_s*eta_b)
E_n


# In[ ]:


# Lifetime Useful Energy
E_l = sympify(20*365)*E_n

# Battery cap
N_d, SoC_min = sp.symbols('N_d SoC_min',positive=true)
C_bat = N_d*E_n/(SoC_min*eta_i)

# Battery mass
np_mbat_poly= np.poly1d(bat_fit)
m_bat = sp.Poly(np_mbat_poly.coeffs,C_bat)/1 #/1 forces symbolic expression rather than Poly expression


# In[ ]:


# Battery impacts
np_Ibat_poly= np.poly1d(bat_score_fit)
I_b = sp.Poly(np_Ibat_poly.coeffs,m_bat)/1

# Tower variable impacts
np_Itow_poly= np.poly1d(tow_score_fit)
I_t = sp.Poly(np_Itow_poly.coeffs,h)/1
I_t


# In[ ]:


# Fixed impacts
I_f = sp.symbols('I_f',positive=true)
I_f = 0.376032308415008 #cst_score

# Cost function
f_c = (I_f+I_b+I_t)/E_l # ENF
I_g = I_f+I_b+I_t


# In[ ]:


I_g


# In[ ]:


# for a specific site
#sp.simplify(f_c)


# In[ ]:


electronics_variables={eta_b:0.8,## battery cycle efficiency
             eta_i:0.9,## inverter efficiency
             F_ls:0.2,## shifted energy
             F_os:0.15,## lost energy
             N_d:2,## days of autonomy
             SoC_min:0.5,## minimum state of charge
            }

f_ce=f_c.subs(electronics_variables)
I_ge=I_g.subs(electronics_variables)
E_ne=E_n.subs(electronics_variables)


# In[ ]:





# In[ ]:


f_ce


# In[ ]:





# In[ ]:


#solve(Eq(diff(f_ce.subs(site_specs),h),0)) # this takes too long


# In[ ]:


## Plot Cost function in function of tower height for one site
n=30
site_specs_worst={V_r:4,
            h_r:12,
            z_0:0.5
            }
f_cwc=lambdify(h,f_ce.subs(site_specs_worst))
I_wc=f_cwc(12) #mPts/kWh # worst case impact scenario
h_array=np.linspace(12,30,n)
z0_array = np.array([0.01, 0.1,0.3, 0.5])
vw_array = np.array([4, 5, 6])
fhz = np.zeros([len(z0_array),n])
fhv = np.zeros([len(vw_array),n])


fig, ax = plt.subplots()
ax.set_xlabel('Tower height')
ax.set_ylabel('Normalized score/kWh')
for i,z in enumerate(z0_array):
    site_specs={V_r:4,
            h_r:12,
            z_0:z
            }
    f_ces=lambdify(h,f_ce.subs(site_specs))
    fhz[i,:]=f_ces(h_array)
    ax.plot(h_array,fhz[i,:]/I_wc,label='$z_0$='+str(z))
ax.legend()
ax.grid(True)
plt.show()    


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('Tower height')
ax.set_ylabel('Normalized score/kWh')
for i,v in enumerate(vw_array):
    site_specs={V_r:v,
            h_r:12,
            z_0:0.5
            }
    f_ces=lambdify(h,f_ce.subs(site_specs))
    fhv[i,:]=f_ces(h_array)
    ax.plot(h_array,fhv[i,:]/I_wc,label='V_r='+str(v))
ax.legend()
ax.grid(True)
plt.show() 


# In[ ]:


## Plot Impacts = f (DEN)
## for several surface roughness
fig, ax = plt.subplots()
ax.set_xlabel('Daily energy need (kWh)')
ax.set_ylabel('Score (Pt)')
ihz=np.zeros([len(z0_array),n])
color_map = plt.colormaps['tab10']
labels=[0, 0, 0, 0]
bound_max=np.zeros([len(vw_array)*len(z0_array),2])
bound_min=np.zeros([len(vw_array),2])
idx=0
for j,v in enumerate(vw_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:12,
                z_0:z
                }
        I_ges=lambdify(h,I_ge.subs(site_specs))
        den=lambdify(h,E_ne.subs(site_specs))
        ihz[i,:]=I_ges(h_array)
        labels[i]='$z_0$='+str(z)
        ax.plot(den(h_array),ihz[i,:],label='$z_0$='+str(z), color=color_map(i))
        bound_max[idx,:]=[den(np.max(h_array)),I_ges(np.max(h_array))]
        bound_min[j,:]=[den(np.min(h_array)),I_ges(np.min(h_array))]
        idx+=1
handles, labels = ax.get_legend_handles_labels()
unique_labels = list(set(labels))
p_bmin=np.polyfit(bound_min[:,0],bound_min[:,1],2)
p_bmax=np.polyfit(bound_max[:,0],bound_max[:,1],3)
d_min=np.linspace(bound_min[0,0],bound_min[-1,0],100)
d_max=np.linspace(bound_max[0,0],bound_max[-1,0],100)
ax.plot(d_min,np.polyval(p_bmin,d_min), color='grey',linestyle='dashed')
ax.plot(d_max,np.polyval(p_bmax,d_max), color='grey',linestyle='dashed')
ax.set_xlim(1, 5)
ax.legend(handles[:4], labels)
ax.grid(True)
plt.show()    
fig.savefig("figures/score_den_standalone.svg")


# In[ ]:


## Plot impacts / kWh = f(DEN)
## Plot Impacts = f (DEN)
## for several surface roughness
fig, ax = plt.subplots()
ax.set_xlabel('Daily energy need (kWh)')
ax.set_ylabel('Score/kWh (p.u.)')
ihz=np.zeros([len(z0_array),n])
color_map = plt.colormaps['tab10']
bound_max=np.zeros([len(vw_array)*len(z0_array),2])
bound_18=np.zeros([len(vw_array)*len(z0_array),2])
bound_24=np.zeros([len(vw_array)*len(z0_array),2])
bound_min=np.zeros([len(vw_array),2])
idx=0
for j,v in enumerate(vw_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:12,
                z_0:z
                }
        f_ces=lambdify(h,f_ce.subs(site_specs))
        den=lambdify(h,E_ne.subs(site_specs))
        labels[i]='$z_0$='+str(z)
        ax.plot(den(h_array),f_ces(h_array)/I_wc,label='$z_0$='+str(z), color=color_map(i))
        bound_max[idx,:]=[den(np.max(h_array)),f_ces(np.max(h_array))/I_wc]
        bound_24[idx,:]=[den(24),f_ces(24)/I_wc]
        bound_18[idx,:]=[den(18),f_ces(18)/I_wc]
        bound_min[j,:]=[den(np.min(h_array)),f_ces(np.min(h_array))/I_wc]
        idx+=1
p_bmin=np.polyfit(bound_min[:,0],bound_min[:,1],2)
p_b18=np.polyfit(bound_18[:,0],bound_18[:,1],2)
p_b24=np.polyfit(bound_24[:,0],bound_24[:,1],2)
p_bmax=np.polyfit(bound_max[:,0],bound_max[:,1],3)
d_min=np.linspace(bound_min[0,0],bound_min[-1,0],100)
d_18=np.linspace(bound_18[0,0],bound_18[-1,0],100)
d_24=np.linspace(bound_24[0,0],bound_24[-1,0],100)
d_max=np.linspace(bound_max[0,0],bound_max[-1,0],100)
ax.plot(d_min,np.polyval(p_bmin,d_min), color='grey',linestyle='dashed')
ax.plot(d_max,np.polyval(p_bmax,d_max), color='grey',linestyle='dashed')
ax.plot(d_18,np.polyval(p_b18,d_18), color='grey',linestyle='dashed')
ax.plot(d_24,np.polyval(p_b24,d_24), color='grey',linestyle='dashed')
ax.set_xlim(1, 5)  
handles, labels = ax.get_legend_handles_labels()
unique_labels = list(set(labels))
ax.legend(handles[:4], labels)
ax.grid(True)
plt.show()    
fig.savefig("figures/score_norm_den_standalone.svg")


# In[ ]:


## find optimal height
h_array=np.linspace(12,30,2000)
v_array=np.linspace(4**3,6**3,100)**(1/3) # linear space for cube of wind speed
z_names=["Z001","Z01","Z03","Z05"]
h_opt={"v_r":v_array,"Z001":np.zeros(len(v_array)),"Z01":np.zeros(len(v_array)),"Z03":np.zeros(len(v_array)),"Z05":np.zeros(len(v_array))}
h_opt_df=pd.DataFrame.from_dict(h_opt)
den_opt={"v_r":v_array,"Z001":np.zeros(len(v_array)),"Z01":np.zeros(len(v_array)),"Z03":np.zeros(len(v_array)),"Z05":np.zeros(len(v_array))}
den_opt_df=pd.DataFrame.from_dict(h_opt)
for j,v in enumerate(v_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:12,
                z_0:z
                }
        f_ces=lambdify(h,f_ce.subs(site_specs))
        h_opt_df.loc[j,z_names[i]]=h_array[np.argmin(f_ces(h_array))]


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('$V_r$ at 12 m (m/s)')
ax.set_ylabel('Optimal tower height (m)')
for i,z in enumerate(z_names):
    ax.plot(h_opt_df["v_r"],h_opt_df[z],label=labels[i])
ax.legend()
ax.grid(True)
plt.show()  
fig.savefig("figures/h_opt_standalone.svg")


# In[ ]:


## find optimal height
h_array=np.linspace(12,30,2000)
v_array=np.linspace(4**3,6**3,100)**(1/3) # linear space for cube of wind speed
z_names=["Z001","Z01","Z03","Z05"]
h_opt={"v_r":v_array,"Z001":np.zeros(len(v_array)),"Z01":np.zeros(len(v_array)),"Z03":np.zeros(len(v_array)),"Z05":np.zeros(len(v_array))}
h_opt_df=pd.DataFrame.from_dict(h_opt)
den_opt={"v_r":v_array,"Z001":np.zeros(len(v_array)),"Z01":np.zeros(len(v_array)),"Z03":np.zeros(len(v_array)),"Z05":np.zeros(len(v_array))}
den_opt_df=pd.DataFrame.from_dict(h_opt)
for j,v in enumerate(v_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:12,
                z_0:z
                }
        f_ces=lambdify(h,f_ce.subs(site_specs))
        E_nes=lambdify(h,E_ne.subs(site_specs))
        h_opt_df.loc[j,z_names[i]]=h_array[np.argmin(f_ces(h_array))]
        den_opt_df.loc[j,z_names[i]]=E_nes(h_array[np.argmin(f_ces(h_array))])


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('$V_r$ at 12 m (m/s)')
ax.set_ylabel('Optimal daily energy need (kWh)')
for i,z in enumerate(z_names):
    ax.plot(den_opt_df["v_r"],den_opt_df[z],label=labels[i])
ax.legend()
ax.set_ylim(1, 6)  
ax.grid(True)
plt.show()  
fig.savefig("figures/den_opt_standalone.svg")


# # Grid tied
# 

# In[ ]:


E_p = AEP/sp.sympify(365) 
E_n = E_p*eta_i
E_l = E_n*365*20 # lifetime energy need
electronics_variables={
             eta_i:0.9,## inverter efficiency   
            F_ls:0.2
            }

E_ne=(E_n).subs(electronics_variables)

# Energy bought to the grid over lifetime
kwh_grid=(1-F_ls)*E_n*365*20

# Grid energy impacts
np_kwh_poly= np.poly1d(kwh_score_fit)
I_kwh = sp.Poly(np_kwh_poly.coeffs,kwh_grid)/1 #/1 forces symbolic expression rather than Poly expression

I_g = I_f+I_t+I_kwh
f_c = I_g/(E_l)
f_ce = f_c.subs(electronics_variables)
I_ge = I_g.subs(electronics_variables)


# In[ ]:


I_kwh


# In[ ]:


## Plot Cost function in function of tower height for one site
n=50
h_array=np.linspace(12,30,n)


fig, ax = plt.subplots()
ax.set_xlabel('Tower height')
ax.set_ylabel('Impacts / kWh')
for i,z in enumerate(z0_array):
    site_specs={V_r:4,
            h_r:10,
            z_0:z
            }
    f_ces=lambdify(h,f_ce.subs(site_specs))
    ax.plot(h_array,f_ces(h_array),label='z_0='+str(z))
ax.legend()
ax.grid(True)
plt.show()    


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('Daily Energy need')
ax.set_ylabel('Impacts / kWh')
for i,z in enumerate(z0_array):
    site_specs={V_r:4,
            h_r:12,
            z_0:z
            }
    f_ces=lambdify(h,f_ce.subs(site_specs))
    e_grid=lambdify(h,E_ne.subs(site_specs))
    ax.plot(e_grid(h_array),f_ces(h_array),label='z_0='+str(z))
ax.legend()
ax.grid(True)
plt.show() 


# In[ ]:





# In[ ]:


## Plot Impacts = f (DEN)
## for several surface roughness
fig, ax = plt.subplots()
ax.set_xlabel('Daily energy need (kWh)')
ax.set_ylabel('Score (Pt)')
ihz=np.zeros([len(z0_array),n])
color_map = plt.colormaps['tab10']
labels=[0, 0, 0, 0]
bound_max=np.zeros([len(vw_array)*len(z0_array),2])
bound_min=np.zeros([len(vw_array),2])
idx=0
for j,v in enumerate(vw_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:12,
                z_0:z
                }
        I_ges=lambdify(h,I_ge.subs(site_specs))
        den=lambdify(h,E_ne.subs(site_specs))
        ihz[i,:]=I_ges(h_array)
        labels[i]='$z_0$='+str(z)
        ax.plot(den(h_array),ihz[i,:],label='$z_0$='+str(z), color=color_map(i))
        bound_max[idx,:]=[den(np.max(h_array)),I_ges(np.max(h_array))]
        bound_min[j,:]=[den(np.min(h_array)),I_ges(np.min(h_array))]
        idx+=1
handles, labels = ax.get_legend_handles_labels()
unique_labels = list(set(labels))
p_bmin=np.polyfit(bound_min[:,0],bound_min[:,1],2)
p_bmax=np.polyfit(bound_max[:,0],bound_max[:,1],3)
d_min=np.linspace(bound_min[0,0],bound_min[-1,0],100)
d_max=np.linspace(bound_max[0,0],bound_max[-1,0],100)
ax.plot(d_min,np.polyval(p_bmin,d_min), color='grey',linestyle='dashed')
ax.plot(d_max,np.polyval(p_bmax,d_max), color='grey',linestyle='dashed')
ax.set_xlim(1, 6)
ax.legend(handles[:4], labels)
ax.grid(True)
plt.show()    
fig.savefig("figures/score_den_grid.svg")


# In[ ]:


## Plot impacts / kWh = f(DEN)
## Plot Impacts = f (DEN)
## for several surface roughness
fig, ax = plt.subplots()
ax.set_xlabel('Daily energy need (kWh)')
ax.set_ylabel('Score/kWh (p.u.)')
ihz=np.zeros([len(z0_array),n])
color_map = plt.colormaps['tab10']
bound_max=np.zeros([len(vw_array)*len(z0_array),2])
bound_18=np.zeros([len(vw_array)*len(z0_array),2])
bound_24=np.zeros([len(vw_array)*len(z0_array),2])
bound_min=np.zeros([len(vw_array),2])
idx=0
site_specs={V_r:4,
                h_r:12,
                z_0:0.5
                }
I_grid=lambdify(h,f_ce.subs(site_specs))
I_12g=I_grid(12)
for j,v in enumerate(vw_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:12,
                z_0:z
                }
        f_ces=lambdify(h,f_ce.subs(site_specs))
        den=lambdify(h,E_ne.subs(site_specs))
        labels[i]='$z_0$='+str(z)
        ax.plot(den(h_array),f_ces(h_array)/I_wc,label='$z_0$='+str(z), color=color_map(i))
        bound_max[idx,:]=[den(np.max(h_array)),f_ces(np.max(h_array))/I_wc]
        bound_24[idx,:]=[den(24),f_ces(24)/I_wc]
        bound_18[idx,:]=[den(18),f_ces(18)/I_wc]
        bound_min[j,:]=[den(np.min(h_array)),f_ces(np.min(h_array))/I_wc]
        idx+=1
p_bmin=np.polyfit(bound_min[:,0],bound_min[:,1],2)
p_b18=np.polyfit(bound_18[:,0],bound_18[:,1],2)
p_b24=np.polyfit(bound_24[:,0],bound_24[:,1],2)
p_bmax=np.polyfit(bound_max[:,0],bound_max[:,1],3)
d_min=np.linspace(bound_min[0,0],bound_min[-1,0],100)
d_18=np.linspace(bound_18[0,0],bound_18[-1,0],100)
d_24=np.linspace(bound_24[0,0],bound_24[-1,0],100)
d_max=np.linspace(bound_max[0,0],bound_max[-1,0],100)
ax.plot(d_min,np.polyval(p_bmin,d_min), color='grey',linestyle='dashed')
ax.plot(d_max,np.polyval(p_bmax,d_max), color='grey',linestyle='dashed')
ax.plot(d_18,np.polyval(p_b18,d_18), color='grey',linestyle='dashed')
ax.plot(d_24,np.polyval(p_b24,d_24), color='grey',linestyle='dashed')
ax.set_xlim(1, 6)  
handles, labels = ax.get_legend_handles_labels()
unique_labels = list(set(labels))
ax.legend(handles[:4], labels)
ax.grid(True)
plt.show()    
fig.savefig("figures/score_norm_den_grid.svg")


# In[ ]:





# In[ ]:


## find optimal height
h_array=np.linspace(12,30,2000)
v_array=np.linspace(4**3,6**3,100)**(1/3) # linear space for cube of wind speed
z_names=["Z001","Z01","Z03","Z05"]
h_opt={"v_r":v_array,"Z001":np.zeros(len(v_array)),"Z01":np.zeros(len(v_array)),"Z03":np.zeros(len(v_array)),"Z05":np.zeros(len(v_array))}
h_opt_df=pd.DataFrame.from_dict(h_opt)
for j,v in enumerate(v_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:12,
                z_0:z
                }
        f_ces=lambdify(h,f_ce.subs(site_specs))
        h_opt_df.loc[j,z_names[i]]=h_array[np.argmin(f_ces(h_array))]


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('$V_r$ at 12 m (m/s)')
ax.set_ylabel('Optimal tower height (m)')
for i,z in enumerate(z_names):
    ax.plot(h_opt_df["v_r"],h_opt_df[z],label=labels[i])
ax.legend()
ax.grid(True)
plt.show()  
fig.savefig("figures/h_opt_grid.svg")


# In[ ]:


## find optimal height
h_array=np.linspace(12,30,2000)
v_array=np.linspace(4**3,6**3,100)**(1/3) # linear space for cube of wind speed
z_names=["Z001","Z01","Z03","Z05"]
h_opt={"v_r":v_array,"Z001":np.zeros(len(v_array)),"Z01":np.zeros(len(v_array)),"Z03":np.zeros(len(v_array)),"Z05":np.zeros(len(v_array))}
h_opt_df=pd.DataFrame.from_dict(h_opt)
den_opt={"v_r":v_array,"Z001":np.zeros(len(v_array)),"Z01":np.zeros(len(v_array)),"Z03":np.zeros(len(v_array)),"Z05":np.zeros(len(v_array))}
den_opt_df=pd.DataFrame.from_dict(h_opt)
for j,v in enumerate(v_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:12,
                z_0:z
                }
        f_ces=lambdify(h,f_ce.subs(site_specs))
        E_nes=lambdify(h,E_ne.subs(site_specs))
        h_opt_df.loc[j,z_names[i]]=h_array[np.argmin(f_ces(h_array))]
        den_opt_df.loc[j,z_names[i]]=E_nes(h_array[np.argmin(f_ces(h_array))])


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('$V_r$ at 12 m (m/s)')
ax.set_ylabel('Optimal daily energy need (kWh)')
for i,z in enumerate(z_names):
    ax.plot(den_opt_df["v_r"],den_opt_df[z],label=labels[i])
ax.legend()
ax.set_ylim(1, 6)  
ax.grid(True)
plt.show()  
fig.savefig("figures/den_opt_grid.svg")


# ## Map data

# In[ ]:


z0_df = pd.read_csv("data/z_values.csv", delimiter=';', decimal=',')


# In[ ]:


z0_df


# In[ ]:


z0_array=z0_df['Z₀']


# In[ ]:


z0_array.pop(0)


# In[ ]:


for i,z in enumerate(z0_array):
    print(i)
    print(z)


# In[ ]:


## find optimal height
h_array=np.linspace(12,30,200)
v_array=np.linspace(2.5**3,8**3,500)**(1/3) # linear space for cube of wind speed
h_opt_dict={"z=" + str(z):np.zeros([len(v_array)])  for i,z in enumerate(z0_array)}
h_opt_df=pd.DataFrame.from_dict(h_opt_dict)
den_opt_grid_df=h_opt_df.copy(deep=True)
for j,v in enumerate(v_array):
    for i,z in enumerate(z0_array):
        site_specs={V_r:v,
                h_r:10,
                z_0:z
                }
        f_ces=lambdify(h,f_ce.subs(site_specs))
        E_nes=lambdify(h,E_ne.subs(site_specs))
        h_opt_df.loc[j,"z=" + str(z)]=h_array[np.argmin(f_ces(h_array))]
        den_opt_grid_df.loc[j,"z=" + str(z)]=E_nes(h_array[np.argmin(f_ces(h_array))])


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('$V_r$ at 10 m (m/s)')
ax.set_ylabel('Optimal tower height (m)')
for i,z in enumerate(z0_array):
    ax.plot(v_array,h_opt_df["z=" + str(z)])
ax.legend()
ax.grid(True)
plt.show()  


# In[ ]:


h_opt_df.loc[:,"Vr"]=v_array


# In[ ]:


h_opt_df


# In[ ]:


h_opt_df.to_csv("h_opt_map.csv")


# In[ ]:


den_opt_grid_df


# In[ ]:


fig, ax = plt.subplots()
ax.set_xlabel('$V_r$ at 10 m (m/s)')
ax.set_ylabel('Optimal den(kwh/day)')
for i,z in enumerate(z0_array):
    ax.plot(v_array,den_opt_grid_df["z=" + str(z)])
ax.legend()
ax.grid(True)
plt.show()  

