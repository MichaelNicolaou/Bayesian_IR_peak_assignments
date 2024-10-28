# -*- coding: utf-8 -*-
"""
Created on Thu Sep  5 12:20:22 2024

@author: 2811088N
"""

###############################################################################
##Import libraries##
###############################################################################

import pandas as pd
import matplotlib.pyplot as plt
import math
import os

###############################################################################
##Define functions##
###############################################################################

def Gaussian(x, std, mean):
    return (1 / (math.sqrt(2 * math.pi * (std**2)))) * (math.exp(- ((x-mean) ** 2) / (2 * (std ** 2))))

def Bayes(Prior, Likelihood, Marginal):
    Posterior = (Likelihood * Prior) / Marginal
    return Posterior

def Bayes_models(Likelihood_Hi, Prior_Hi, Likelihood_Hj, Prior_Hj):
    Factor = (Likelihood_Hi / Likelihood_Hj) * (Prior_Hi / Prior_Hj)
    return Factor

def STD_conv(peak, rel_MSD, rel_STD):
    STD = (peak + (peak * (rel_MSD / 100))) * (rel_STD / 100)
    return STD

def Mean_conv(peak, rel_MSD):
    Mean = peak + (peak * (rel_MSD / 100))
    return Mean

###############################################################################

# Molecule_list = ["Vanillin", "Syringaldehyde", "Hydroxybenzaldehyde", "Cinnamaldehyde", "Cuminaldehyde", "Eugenol", "Estragole", "Coumarin", "Dihydrocoumarin", "Umbelliferone"]
Molecule_list = ["Cuminaldehyde"]
path = 'Z:\\Michael Nicolaou\\Projects\\Back to the roots\\Workbench.xlsx'

for Molecule in Molecule_list:
    
    df_th = pd.read_excel(path, str(Molecule) + "-DFT").fillna("")
    df_exp = pd.read_excel(path, str(Molecule) + "-IR").fillna("")
    
    ###############################################################################
    ##Define statistical metrics (%)##
    ###############################################################################
    
    MSD = -0.12
    STD = 1.18
    
    #As fixed values
    
    # MSD = 1.19
    # STD = 12.75

    if Molecule == "Vanillin":
        Threshold = 50
    elif Molecule == "Vanillin":
        Threshold = 50
    else:
        Threshold = 50
    

    ###############################################################################
    ##Overwrite previous results##
    if os.path.exists("IR_assignment_" + Molecule + ".xlsx"):
        os.remove("IR_assignment_" + Molecule + ".xlsx")
        print("Overwriting old IR_assignment_" + Molecule + ".xlsx file")
    
    ###############################################################################
    ##Input set of studied Theoretical (DFT) and Experimental IR peaks## 
    ###############################################################################
    print("Performing inference for " + str(Molecule) + ".")
    
    Theoretical_peaks = []
    Experimental_peaks = []
    
    if Molecule == "Cinnamaldehyde":
        for mode in range(0, len(df_th.loc[:, "Mode"])):
            if str(df_th.loc[mode, "Normal mode"]) != "":
                Theoretical_peaks.append(round(df_th.loc[mode, "Scaled Frequency"]))
        
        for wavenumber in range(0, len(df_exp.loc[:, "Frequency"])):
            if df_exp.loc[wavenumber, "Sign"] < 0 and df_exp.loc[wavenumber, "Difference"] > 0 and df_exp.loc[wavenumber, "Frequency"] > 680 and df_exp.loc[wavenumber, "Frequency"] < 1650 and str(df_exp.loc[wavenumber, "Observation"]) != "Noise":
                Experimental_peaks.append(round(df_exp.loc[wavenumber, "Frequency"]))
            elif str(df_exp.loc[wavenumber, "Observation"]) == "Shoulder" and df_exp.loc[wavenumber, "Frequency"] > 680 and df_exp.loc[wavenumber, "Frequency"] < 1800:
                Experimental_peaks.append(round(df_exp.loc[wavenumber, "Frequency"]))
                
    elif Molecule == "Dihydrocoumarin":
        for mode in range(0, len(df_th.loc[:, "Mode"])):
            if str(df_th.loc[mode, "Normal mode"]) != "":
                Theoretical_peaks.append(round(df_th.loc[mode, "Scaled Frequency"]))
        
        for wavenumber in range(0, len(df_exp.loc[:, "Frequency"])):
            if df_exp.loc[wavenumber, "Sign"] < 0 and df_exp.loc[wavenumber, "Difference"] > 0 and df_exp.loc[wavenumber, "Frequency"] > 740 and df_exp.loc[wavenumber, "Frequency"] < 1650 and str(df_exp.loc[wavenumber, "Observation"]) != "Noise":
                Experimental_peaks.append(round(df_exp.loc[wavenumber, "Frequency"]))
            elif str(df_exp.loc[wavenumber, "Observation"]) == "Shoulder" and df_exp.loc[wavenumber, "Frequency"] > 740 and df_exp.loc[wavenumber, "Frequency"] < 1800:
                Experimental_peaks.append(round(df_exp.loc[wavenumber, "Frequency"]))
                
    else:
        for mode in range(0, len(df_th.loc[:, "Mode"])):
            if str(df_th.loc[mode, "Normal mode"]) != "":
                Theoretical_peaks.append(round(df_th.loc[mode, "Scaled Frequency"]))
        
        for wavenumber in range(0, len(df_exp.loc[:, "Frequency"])):
            if df_exp.loc[wavenumber, "Sign"] < 0 and df_exp.loc[wavenumber, "Difference"] > 0 and df_exp.loc[wavenumber, "Frequency"] > 750 and df_exp.loc[wavenumber, "Frequency"] < 1650 and str(df_exp.loc[wavenumber, "Observation"]) != "Noise":
                Experimental_peaks.append(round(df_exp.loc[wavenumber, "Frequency"]))
            elif str(df_exp.loc[wavenumber, "Observation"]) == "Shoulder" and df_exp.loc[wavenumber, "Frequency"] > 750 and df_exp.loc[wavenumber, "Frequency"] < 1800:
                Experimental_peaks.append(round(df_exp.loc[wavenumber, "Frequency"]))
        
    ###############################################################################
    ##Hypothesis amount calculator##
    
    ## As the algorithm iterates through all possible "hypotheses", taken as all the
    ## possible assignments of theoretical to experimental peaks (which is to say all
    ## the permutations of n-experimental peaks and r-theoretical peaks),I thought it,
    ## would be useful to build in a small segment that calculates how many hypotheses
    ## are formed with a given set. ##
    
    ## This had proven to be useful after realising the silliness of inputting 16
    ## theoretical peaks and 19 experimental peaks, as it can easily lead to massive
    ## computational times.
    
    Hypotheses_number = math.factorial(len(Experimental_peaks)) / (math.factorial(len(Experimental_peaks) - len(Theoretical_peaks)))
    print("This combination of peak sets will result in " + str(int(Hypotheses_number)) + " hypotheses.")
    
    
    ###############################################################################
    ##Create all possible Hypotheses with peak ranges within the threshold##
    ###############################################################################
    ## These can be done in two ways, the more straight-forward would be to find all
    ## permutations using the itertools.permutations() function with inputs of the 
    ## "Exp" list (Labelled experimental peaks) and length of combinations (length
    ## of our "Theoretical_peaks" list) and then remove all entries from the resulting
    ## list which translate to a difference between the labels that's greater than
    ## the "Threshold". The code for this is kept here:
    
        
    # Theo = list(range(1, len(Theoretical_peaks)+1))
    # Exp = list(range(1, len(Experimental_peaks)+1))
    
    # Hypotheses = list(itertools.permutations(Exp, len(Theoretical_peaks)))
    
    # Rm_list = []
    
    # for h in Hypotheses:
    #     counter = 0
    #     for i in h:
    #         if abs(Theoretical_peaks[counter] - Experimental_peaks[i-1]) > Threshold:
    #             Rm_list.append(h)
    #             break
    #         else:
    #             counter = counter + 1
        
    # Hypotheses = [h for h in Hypotheses if h not in Rm_list]
    
    # print(str(len(Rm_list)) + " hypotheses have been filtered, " + str(len(Hypotheses)) + " remaining.")
    
    
    ##############################################################################
    # This however proves to be VERY computationally inefficient (it has to calculate
    # differences from all possible permutations before removing the ones that are
    # deemed over the threshold. This proves to be prohibitively expensive when 
    # 100,000s of permutations can be generated (Usually when using lists of
    # around 10 peaks). For this reason, a hand-coded segment was created that 
    # creates the permutations and filters off the filtered entries as it goes,
    # allowing for the computation of the final hypotheses list to be done much
    # faster. This segment is shown here:
    
    Theo = list(range(1, len(Theoretical_peaks)+1))
    Exp = list(range(1, len(Experimental_peaks)+1))    
    
    Hypotheses = []
    
    temp_hypothesis = []
    
    exec("Unassigned_peaks_" + Molecule + " = []")
    Theo_to_remove = []
    
    for i in Theo:
        counter = 0
        temp_hypothesis_2 = []
        if i == 1:
            for j in Exp:
                if abs(Theoretical_peaks[i-1] - Experimental_peaks[j-1]) < Threshold:
                    temp_hypothesis.append([j])     
        else:
            for h in temp_hypothesis:
                for j in Exp:
                    temp_h = []
                    if abs(Theoretical_peaks[i-1] - Experimental_peaks[j-1]) < Threshold and j not in h:
                        temp_h = h[:]
                        temp_h.append(j)
                        temp_hypothesis_2.append(temp_h)
            if temp_hypothesis_2 != []:
                temp_hypothesis = temp_hypothesis_2[:]
            elif temp_hypothesis_2 == []:
                print("Could not fit an assignment for theoretical peak: " + str(Theoretical_peaks[i-1]))
                Theo_to_remove.append(i)    
                exec("Unassigned_peaks_" + Molecule + ".append(Theoretical_peaks[i-1])")
    
    exec("[Theoretical_peaks.remove(i) for i in Unassigned_peaks_" + Molecule + "]")
    [Theo.remove(i) for i in Theo_to_remove]
    
    Hypotheses = temp_hypothesis[:]    
    
    print(str(int(Hypotheses_number - int(len(Hypotheses)))) + " hypotheses have been filtered, " + str(len(Hypotheses)) + " remaining.")
    
    Hypotheses_labelled = [] 
    Evidence_labelled = []
       
    
    ###############################################################################
    ##Create Dataframe##
    ###############################################################################
    
    for i in range(1,len(Hypotheses)+1):
        Hypotheses_labelled.append("Hypothesis " + str(i))
    
    for i in range(1,len(Theoretical_peaks)+1):
        Evidence_labelled.append("E"+ str(i))
    
    Probs = pd.DataFrame(columns = Evidence_labelled, index = Hypotheses_labelled)
    Probs["Theoretical peak assignment"] = Hypotheses
    
    Peaks1 = pd.DataFrame({"Experimental peak label": Exp})
    Peaks2 = pd.DataFrame({"Experimental peak": Experimental_peaks})
    Peaks3 = pd.DataFrame({"Theoretical peak label": Theo})
    Peaks4 = pd.DataFrame({"Theoretical peak": Theoretical_peaks})
    Peaks = pd.concat([Peaks1, Peaks2, Peaks3, Peaks4], axis = 1)
    
    ###############################################################################
    ##Bayesian processing loop##
    ###############################################################################
    
    #Relative MSD and STD
    for E in range(0, len(Theoretical_peaks)):
        counter = 0
        if E == 0:
            for H in Hypotheses:
                Marginal = []
                for i in Hypotheses:   
                    Marginal.append(Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[i[E]-1], MSD, STD), Mean_conv(Experimental_peaks[i[E]-1], MSD)) * (1/len(Hypotheses)))
                Marginal = sum(Marginal)
                P_H_given_E = Bayes((1/len(Hypotheses)), Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[H[E]-1], MSD, STD), Mean_conv(Experimental_peaks[H[E]-1], MSD)), Marginal)
                Probs.iloc[counter, E] = P_H_given_E
                counter = counter + 1
        else:
            for H in Hypotheses:
                Marginal = []
                counter_2 = 0
                for i in Hypotheses:   
                    Marginal.append(Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[i[E]-1], MSD, STD), Mean_conv(Experimental_peaks[i[E]-1], MSD)) * Probs.iloc[counter_2, E-1])
                    counter_2 = counter_2 + 1
                Marginal = sum(Marginal)
                P_H_given_E = Bayes(Probs.iloc[counter, E-1], Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[H[E]-1], MSD, STD), Mean_conv(Experimental_peaks[H[E]-1], MSD)), Marginal)
                Probs.iloc[counter, E] = P_H_given_E
                counter = counter + 1
    
    #Fixed MSD and STD
    # for E in range(0, len(Theoretical_peaks)):
    #     counter = 0
    #     if E == 0:
    #         for H in Hypotheses:
    #             Marginal = []
    #             for i in Hypotheses:   
    #                 Marginal.append(Gaussian(Theoretical_peaks[E], STD, MSD + Experimental_peaks[E]) * (1/len(Hypotheses)))
    #             Marginal = sum(Marginal)
    #             P_H_given_E = Bayes((1/len(Hypotheses)), Gaussian(Theoretical_peaks[E], STD, MSD + Experimental_peaks[E]), Marginal)
    #             Probs.iloc[counter, E] = P_H_given_E
    #             counter = counter + 1
    #     else:
    #         for H in Hypotheses:
    #             Marginal = []
    #             counter_2 = 0
    #             for i in Hypotheses:   
    #                 Marginal.append(Gaussian(Theoretical_peaks[E], STD, MSD + Experimental_peaks[E]) * Probs.iloc[counter_2, E-1])
    #                 counter_2 = counter_2 + 1
    #             Marginal = sum(Marginal)
    #             P_H_given_E = Bayes(Probs.iloc[counter, E-1], Gaussian(Theoretical_peaks[E], STD, MSD + Experimental_peaks[E]), Marginal)
    #             Probs.iloc[counter, E] = P_H_given_E
    #             counter = counter + 1
    
    
    # for i in range(0, len(Probs.iloc[0, :])-1):
    #     for j in range(0, len(Probs.iloc[:, 0])):
    #         if Probs.iloc[j, i] < 1e-50:
    #             Probs.iloc[j, i] = 1e-50
    
    ###############################################################################
    ##Model comparing method##
    ###############################################################################
    
    Probs = Probs.sort_values(Probs.columns[-2], ascending = False)
    
    Hypotheses = Probs.iloc[0:5, -1].tolist()
    temp_H = []
    for Hypothesis in Hypotheses:
        exec("temp_H.append(" +str(Hypothesis)+ ")")
    Hypotheses = temp_H
    
    Probs_models = pd.DataFrame(columns = range(1, len(Hypotheses)+1), index = range(1, len(Hypotheses)+1)).astype(float)
    Probs_models_log = pd.DataFrame(columns = range(1, len(Hypotheses)+1), index = range(1, len(Hypotheses)+1)).astype(float)
    
    #Relative MSD and STD
    for E in range(0, len(Theoretical_peaks)):
        if E == 0:
            for Hi in range(0, len(Hypotheses)):
                for Hj in range(0, len(Hypotheses)):
                    if Hj == 0:
                        Probs_models.iloc[Hi, Hj] = 1
                    else:
                        Probs_models.iloc[Hi, Hj] = Bayes_models(
                            Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[Hypotheses[Hi][E]-1], MSD, STD), Mean_conv(Experimental_peaks[Hypotheses[Hi][E]-1], MSD)),
                            (1/len(Hypotheses)),
                            Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[Hypotheses[Hj][E]-1], MSD, STD), Mean_conv(Experimental_peaks[Hypotheses[Hj][E]-1], MSD)),
                            (1/len(Hypotheses))
                        )
                        
        else:
            for Hi in range(0, len(Hypotheses)):
                for Hj in range(0, len(Hypotheses)):
                    if Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[Hypotheses[Hj][E]-1], MSD, STD), Mean_conv(Experimental_peaks[Hypotheses[Hj][E]-1], MSD)) == 0 or Probs.iloc[Hj, E-1] == 0:
                        Probs_models.iloc[Hi, Hj] = 1
                    else:
                        Probs_models.iloc[Hi, Hj] = Bayes_models(
                            Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[Hypotheses[Hi][E]-1], MSD, STD), Mean_conv(Experimental_peaks[Hypotheses[Hi][E]-1], MSD)),
                            Probs.iloc[Hi, E-1],
                            Gaussian(Theoretical_peaks[E], STD_conv(Experimental_peaks[Hypotheses[Hj][E]-1], MSD, STD), Mean_conv(Experimental_peaks[Hypotheses[Hj][E]-1], MSD)),
                            Probs.iloc[Hj, E-1]
                        )
    
    #Fixed MSD and STD
    # for E in range(0, len(Theoretical_peaks)):
    #     if E == 0:
    #         for Hi in range(0, len(Hypotheses)):
    #             for Hj in range(0, len(Hypotheses)):
    #                 if Hj == 0:
    #                     Probs_models.iloc[Hi, Hj] = 1
    #                 else:
    #                     Probs_models.iloc[Hi, Hj] = Bayes_models(
    #                         Gaussian(Theoretical_peaks[E], STD, MSD + Experimental_peaks[E]),
    #                         (1/len(Hypotheses)),
    #                         Gaussian(Theoretical_peaks[E], STD, MSD + Experimental_peaks[E]),
    #                         (1/len(Hypotheses))
    #                     )
                        
    #     else:
            
    #         for Hi in range(0, len(Hypotheses)):
    #             for Hj in range(0, len(Hypotheses)):
    #                 if Gaussian(Theoretical_peaks[E], STD, MSD) == 0 or Probs.iloc[Hj, E-1] == 0:
    #                     Probs_models.iloc[Hi, Hj] = 1
    #                 else:
    #                     Probs_models.iloc[Hi, Hj] = Bayes_models(
    #                         Gaussian(Theoretical_peaks[E], STD, MSD + Experimental_peaks[E]),
    #                         Probs.iloc[Hi, E-1],
    #                         Gaussian(Theoretical_peaks[E], STD, MSD + Experimental_peaks[E]),
    #                         Probs.iloc[Hj, E-1]
    #                     )
    
    
    Probs_models_log = Probs_models.applymap(math.log10)
    for Hypothesis in range(1, len(Probs_models.index)+1):
        print("Lowest Hypothesis " + str(Hypothesis) + " factor is " + str(min(Probs_models.iloc[Hypothesis-1, :])))
    
    ###############################################################################
    ## Gaussian plotting ##
    ###############################################################################
    
    # plt.yticks([])
    # plt.xlabel("Wavenumber / cm$^{-1}$")
    # plt.ylabel("Intensity")
    # plt.ylim([0,0.17])
    # plt.xlim([1180, 1310])
    
    # x = list(range(1170, 1325))
    # Gauss_y_1 = []
    # Gauss_y_2 = []
    # Gauss_y_3 = []
    # Gauss_y_4 = []
    # Gauss_y_5 = []
    # Gauss_y_6 = []
    # Gauss_y_7 = []
    
    # for i in x:
    #     Gauss_y_1.append(Gaussian(i, STD_conv(Theoretical_peaks[0], MSD, STD), Mean_conv(Theoretical_peaks[0], MSD)))
    #     Gauss_y_2.append(Gaussian(i, STD_conv(Theoretical_peaks[1], MSD, STD), Mean_conv(Theoretical_peaks[1], MSD)))
    #     Gauss_y_3.append(Gaussian(i, STD_conv(Theoretical_peaks[2], MSD, STD), Mean_conv(Theoretical_peaks[2], MSD)))
    #     Gauss_y_4.append(Gaussian(i, STD_conv(Experimental_peaks[0], MSD, STD), Mean_conv(Experimental_peaks[0], MSD)))
    #     Gauss_y_5.append(Gaussian(i, STD_conv(Experimental_peaks[1], MSD, STD), Mean_conv(Experimental_peaks[1], MSD)))
    #     Gauss_y_6.append(Gaussian(i, STD_conv(Experimental_peaks[2], MSD, STD), Mean_conv(Experimental_peaks[2], MSD)))
    #     Gauss_y_7.append(Gaussian(i, STD_conv(Experimental_peaks[3], MSD, STD), Mean_conv(Experimental_peaks[3], MSD)))
    
        
    # plt.plot(x, Gauss_y_1, linewidth = 2, c = "Black", zorder = 2)
    # plt.plot(x, Gauss_y_2, linewidth = 2, c = "Black", zorder = 2)
    # plt.plot(x, Gauss_y_3, linewidth = 2, c = "Black", zorder = 2)
    # plt.plot(x, Gauss_y_4, linewidth = 1.5, c = "Red")
    # plt.plot(x, Gauss_y_5, linewidth = 1.5, c = "Red")
    # plt.plot(x, Gauss_y_6, linewidth = 1.5, c = "Red")
    # plt.plot(x, Gauss_y_7, linewidth = 1.5, c = "Red")
    # # plt.plot([Mean_conv(Experimental_peaks[3], MSD), Mean_conv(Experimental_peaks[3], MSD)], [0, .17], linewidth = 1.5, linestyle = "--", c = "Black")
    # # plt.plot([1096, 1103], [Gauss_y[46], Gauss_y[46]], linewidth = 1.5, c = "Black", linestyle = "--")
    # plt.text(Theoretical_peaks[0], .15, "1", fontsize = 12, c = "Black")
    # plt.text(Theoretical_peaks[1], .15, "2", fontsize = 12, c = "Black")
    # plt.text(Theoretical_peaks[2], .15, "3", fontsize = 12, c = "Black")
    # plt.text(Experimental_peaks[0], .15, "1", fontsize = 12, c = "Red")
    # plt.text(Experimental_peaks[1], .15, "2", fontsize = 12, c = "Red")
    # plt.text(Experimental_peaks[2], .15, "3", fontsize = 12, c = "Red")
    # plt.text(Experimental_peaks[3], .15, "4", fontsize = 12, c = "Red")
    
    # plt.text(1101, max(Gauss_y) + 0.002, "Mean", fontsize = 12)
    
    # plt.savefig("Peak_gaussians.jpg", format = "jpg", bbox_inches='tight', dpi = 300)
    
    # plt.yticklabels([])
    
    ##Write record of results
    with pd.ExcelWriter('IR_assignments_' + Molecule + '.xlsx') as writer:
        Peaks.to_excel(writer, sheet_name= "Legend")
        Probs.to_excel(writer, sheet_name='Probabilities')
        Probs_models.to_excel(writer, sheet_name='Model comparisons')
        Probs_models_log.to_excel(writer, sheet_name='Model comparisons (log)')