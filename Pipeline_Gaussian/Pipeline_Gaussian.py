# -*- coding: utf-8 -*-
"""
Created on Fri Oct 27 14:17:58 2023

@author: 2811088N
"""
#%% - Libraries
###############################################################################
#Libraries
###############################################################################

import pandas as pd
import numpy as np
import math
import os
import openpyxl
from openpyxl import load_workbook

###############################################################################
#%% - Directory setup
###############################################################################
#Directory setup
###############################################################################

#Set directory of output files in computer and path to excel workbook where
#results will be saved.

directory = ''
path = ""

Scaling = 1

####################################CAUTION####################################

#Delete old variables file (Overwrite)
#Comment to disable overwriting of the output Variable file. This will keep the
#contained variables in the file and might lead to redundant duplicates.



if Scaling == 1:
    if os.path.exists("Variables_Pipeline_Gaussian.py"):
        os.remove("Variables_Pipeline_Gaussian.py")
        print("Overwriting old Variables_Pipeline_Gaussian.py file")
        
elif Scaling == 0:
    if os.path.exists("Variables_Pipeline_Gaussian_unscaled.py"):
        os.remove("Variables_Pipeline_Gaussian_unscaled.py")
        print("Overwriting old Variables_Pipeline_Gaussian_unscaled.py file")


###############################################################################
#%% - Gaussian Output (.log) file reading loop 
###############################################################################
#Gaussian-16 Output file reading
###############################################################################

#Create lists for negative and unfinished files: 
#Files with negative wavenumber frequencies (unoptimised geometries) go in
#"negative_freq_ls".
#Files with no Raman information (IR only, Raman not selected) go in 
#"no_Raman_ls".
#Files with no vibrational information (bad terminations or IR spectra) go in
#"no_data_ls".

negative_freq_ls = []
no_Raman_ls = []
no_data_ls = []

#Record lists will contain all the spectral data entries generated

record = []

#Extract the IR and Raman vibrational frequencies and intensities

for filename in os.listdir(directory):
    file = os.path.join(directory, filename)
    if os.path.isfile(file):
        print(file)

    f = open(file)
    content = f.readlines()
    Freq = []
    Infra = []
    Raman = []
    Normal_modes = []
    
    normal_toggle = 0
    checkpoints = []
    counter = 0
    
    Modes = []
    temp_modes = []
    for i in content:
        if "Frequencies --" in i:
            j = str.split(i)
            for char in j:
                if char == "Frequencies" or char.isspace() or "'--'" in char:
                    j.remove(char)
                    for value in j:
                        if value != "--":
                            Freq.append(float(value))
        elif "IR Inten" in i:
            j = str.split(i)
            for char in j:
                if "IR" in char or "Inten" in char or char.isspace() or "'--'" in char:
                    j.remove(char)
                    for value in j:
                        if value != "--" and value != "Inten":
                            Infra.append(float(value))
        elif "Raman Activ" in i:
            j = str.split(i)
            for char in j:
                if char == "Raman" or char.isspace() or "'--'" in char:
                    j.remove(char)
                    for value in j:
                        if value != "--" and value != "Activ":
                            Raman.append(float(value))
        elif "Normal Mode" in i and normal_toggle == 0:
            normal_toggle = 1
        elif normal_toggle == 1 and "Axes" in i:
            normal_toggle = 0
        elif normal_toggle == 1:
            Normal_modes.append(i)
    
    counter = 1
    for i in Normal_modes:
        if "Normal Mode" in i and temp_modes == []:
            Normal_modes.remove(i)
        elif "Normal Mode" in i and temp_modes != []:
            Normal_modes.remove(i)
            Modes.append(temp_modes)
            temp_modes = []
        elif counter == len(Normal_modes):
            Normal_modes.remove(i)
            Modes.append(temp_modes)
            temp_modes = []
        elif any(char.isdigit() for char in i) and "Max" not in i:
            temp_modes.append(i)
        counter = counter + 1
        
    for i in Modes:
        for j in i:
            mode = str.split(j)
            for k in mode:
                if k.isspace():
                    mode.remove(k)
                elif "!" in k:
                    mode.remove(k)
            Modes[Modes.index(i)][Modes[Modes.index(i)].index(j)] = mode
            
###############################################################################
#Normal mode reading
###############################################################################
    
#Create Dataframe

    df = pd.DataFrame({"Frequency": Freq, "IR Intensity": Infra, "Raman activity": Raman})
    df.dropna(inplace=True)
    df = df.astype(float)
    df.insert(3, "Modes", Modes)
#Detect and report files with negative frequencies (non-optimised structures)
    
    if df.empty == True:
        print("No vibrational information for " + str.split(str(filename), ".")[0])
        no_data_ls.append(str.split(str(filename), ".")[0])
        continue
    elif df.iloc[0, 0].astype(float) < 0:
        print("Negative frequency found for " + str.split(str(filename), ".")[0])
        negative_freq_ls.append(str.split(str(filename), ".")[0])
        continue
    else: 
        
        df_mode_lst = []
        important_contributions = []        
        counter = 1
        for i in df.iloc[:,3]:
            temp_type = []
            temp_stretch = []
            temp_stretch_sign = []
            temp_stretch_perc = []
            
            temp_bend = []
            temp_bend_sign = []
            temp_bend_perc = []
            
            temp_wag = []
            temp_wag_sign = []
            temp_wag_perc = []
            
            for j in i:
                if "R" in j[0]:
                    temp_stretch.append(j[1].replace("R",""))
                    temp_stretch_sign.append(float(j[2]))
                    temp_stretch_perc.append(float(j[3]))
                    if float(j[-1]) > 5:
                        important_contributions.append(j)
                elif "A" in j[0]:
                    temp_bend.append(j[1].replace("A",""))
                    temp_bend_sign.append(float(j[2]))
                    temp_bend_perc.append(float(j[3]))     
                elif "D" in j[0]:
                    temp_wag.append(j[1].replace("D",""))
                    temp_wag_sign.append(float(j[2]))
                    temp_wag_perc.append(float(j[3]))
            temp_df_stretch = pd.DataFrame({"Stretching mode": temp_stretch, "Stretch value": temp_stretch_sign, "Stretch percentage": temp_stretch_perc})
            temp_df_bend = pd.DataFrame({"Bending mode": temp_bend, "Bend value": temp_bend_sign, "Bend percentage": temp_bend_perc})
            temp_df_wag = pd.DataFrame({"Wagging mode": temp_wag, "Wag value": temp_wag_sign, "Wag percentage": temp_wag_perc})
            exec("df_mode_"+str(counter)+" = pd.concat([temp_df_stretch, temp_df_bend, temp_df_wag])")
            df_mode_lst.append("df_mode_"+str(counter))
            counter = counter + 1
        
            
                
#%% - Scaling factor setting
###############################################################################
#Insert Scaling factor for Functional/Basis set combination.
###############################################################################
        
        if Scaling == 1:
            Scaling_factor = 0.95 
        else:
            Scaling_factor = 1
        
###############################################################################
#%% - Data organisation
#Organise Dataframe

        scaled_freq = []
        for i in list(df["Frequency"]):
            scaled_freq.append(float(i) * Scaling_factor)
        
        df.insert(1, "Scaled Frequency", scaled_freq)
                        
        #Get peak x and y values
        dfx = list(df.iloc[:,1].round())
        df_IR_y = list(df.iloc[:,2])
        
        if Raman != []:
            df_Ram_y = list(df.iloc[:,3])

            
        #Create new arrays for all spectrum coordinates
        x = list(range(1,4001,1))
        x = [round(elem, 1) for elem in x]
        IR_y = [0] * 4000
        Ram_y = [0] * 4000
        
        #Update peak y-values
        counter = -1
        for i in x:
            counter = counter + 1
            if i in dfx:
                position = dfx.index(i)
                IR_y[counter] = df_IR_y[position]
                Ram_y[counter] = df_Ram_y[position]
                
#%% - Spectra graph loops
###############################################################################
#Spectra graphs
###############################################################################

#Peak distribution curve (Gaussian model).

#x corresponds to the x-value, a corresponds to y-max, b corresponds
#to x-value for y-max and c corresponds to variance (determines width of peak).

        def Gaussian(x, a, b, c):
            return a * (math.e ** (-(((x - b) ** 2) / (2 * (c ** 2)))))
        
        c = 8
#In this case, a Gaussian curve is chosen to model the peaks, alternatively,
#a Lorentzian curve could be used instead.

#In this case, peak modelling is done by keeping the peak height constant, 
#while changing the "Variance", or width, of the curve. An alternative would be
#to keep the peak volume constant, changing the peak height accordingly.


###############################################################################
#First graph - "Convoluted" IR and Raman spectra
###############################################################################

#This attempts to model the realistic peak behaviour in vibrational spectra.
#As peaks overlap with each other, they combine additively, "convolving" to
#give merged, combined peaks of greater peak heights.  

#This is done by creating a y-array of size 4000 for each peak, calculating
#the Gaussian distribution graph for that peak and then adding it in an
#element-wise fashion to the final graph array (IR_y_conv).

###############################################################################

        IR_y_conv = np.zeros(4000)
        
        for i in dfx:
            templist = [0] * 4000
            z = x.index(i)     
            if z >= 50 and z < 3950:
                xdata = np.array(x[(z - 50):(z + 51)])
            elif z < 50:
                xdata = np.array(x[0:(z + 51)])
            elif z > 3950:
                xdata = np.array(x[(z - 50):4000])
            for j in xdata:
                templist[j-1] = Gaussian(z, IR_y[z], j, c)
            IR_y_conv = IR_y_conv + np.array(templist)

        if Raman != []:            
            
            Ram_y_conv = np.zeros(4000)
            
            for i in dfx:
                templist = [0] * 4000
                z = x.index(i)     
                if z > 50 and z < 3950:
                    xdata = np.array(x[(z - 50):(z + 51)])
                elif z < 50:
                    xdata = np.array(x[0:(z + 51)])
                elif z > 3950:
                    xdata = np.array(x[(z - 51):4000])
                    
                for j in xdata:
                    templist[j] = Gaussian(z, Ram_y[z], j, c)
                Ram_y_conv = Ram_y_conv + np.array(templist)
        else:
            print("Raman unavailable for " + str.split(str(filename), ".")[0])
        
        print("Convoluted spectra completed")

#%% - Result exporting information      
###############################################################################
#Results exporting
###############################################################################

#This section will save the read data (IR (and Raman) peaks and intensities in
#the new excel spreadsheet (path, as defined at the start) and the calculated
#spectral data (x, IR_y, Ram_y, IR_y_conv and Ram_y_conv in a .py file
#(Named Variables_Pipeline_Gaussian.py).

#The saved variables will have some alterations to their names, so as to make
#them readable by Python scripts importing them, such as changing "-" and "+".
#If any other characters intervene with the import function, a similar line of
#code to the ones presented below can be used to include those characters by
#simply duplicating the line and replacing the first argument with the 
#character that is to be replaced and the second with the replacement.

#Output file names (excluding the .out extension) with 31 or more characters 
#will give a notice in the console, saying that the title name is too long and 
#might not be readable. This doesn't seem to be an issue, as opening the excel
#spreadsheet afterwards will call it "corrupted" and ask if it should attempt
#to recover data. Pressing yes on that will just cut the title in question
#beyond the 31st letter and present it as such.
#%% - Data saving
##############################################################################
#Save the spectral data
        new_filename = filename.replace("-", "_")    
        new_filename = new_filename.replace("+", "plus")
        new_filename = new_filename.replace(",", "_")
        if len(new_filename) >= 31:
            new_filename = new_filename[:30]
        if Scaling == 1:
            with open('Variables_Pipeline_Gaussian.py', 'a') as f:
                f.write('x_' + str.split(str(new_filename), ".")[0] + ' = ' + str(x) + '\n' + 'IR_y_conv_' + str.split(str(new_filename), ".")[0] + ' = ' + str(list(IR_y_conv)) + '\n' + 'Ram_y_conv_' + str.split(str(new_filename), ".")[0] + ' = ' + str(list(Ram_y_conv)) + '\n')
        elif Scaling == 0:
            with open('Variables_Pipeline_Gaussian_unscaled.py', 'a') as f:
                f.write('x_' + str.split(str(new_filename), ".")[0] + ' = ' + str(x) + '\n' + 'IR_y_conv_' + str.split(str(new_filename), ".")[0] + ' = ' + str(list(IR_y_conv)) + '\n' + 'Ram_y_conv_' + str.split(str(new_filename), ".")[0] + ' = ' + str(list(Ram_y_conv)) + '\n')
#Save the read data
        counter = 1
        with pd.ExcelWriter(path + "\\" + str.split(str(new_filename), ".")[0]+"_normal_modes.xlsx") as writer:
            df.to_excel(writer, sheet_name = "Frequencies", index = False)
            for i in range(1,len(df_mode_lst)):
                name = "Normal_mode_"+ str(counter)
                exec(str(df_mode_lst[i-1])+" = "+str(df_mode_lst[i-1])+".to_excel(writer, sheet_name ="+"'"+str(name)+"'"+", index = False)")
                counter = counter + 1
        print(str.split(str(new_filename), ".")[0] + " completed")
        
#Record entry
        record.append(str.split(str(new_filename), ".")[0])
###############################################################################

#Write record of entries
if Scaling == 1:
    with open('Variables_Pipeline_Gaussian.py', 'a') as f:
        f.write("record = " + str(record))
elif Scaling == 0:
    with open('Variables_Pipeline_Gaussian_unscaled.py', 'a') as f:
        f.write("record = " + str(record))

