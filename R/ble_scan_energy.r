library(DescTools)

#data set for low energy node scanning at full capacity or always running
setwd("~/Documents/LowPowerNodeRep/LowEnergyRelayNode/R")
ble_scan_full <- read.csv("ble_scan_full.csv")
ble_scan_df <- as.data.frame(ble_scan_full)

colnames(ble_scan_df)[1] <- "time" #add time as the column header
colnames(ble_scan_df)[2] <- "a" #since r=1 v=i so column2 is amps

#if we integrate using the trapezodial method over the plot and then divide by the number of values
#we get the average
print(length(ble_scan_df$time))
print(length(ble_scan_df$a))
auc <- AUC(ble_scan_df$time, ble_scan_df$a, method = "trapezoid")
print(auc/262)
mean_amp <- auc / 262 # integral/total time
print(mean_amp)

#take the mean amps and multiply by volts to get power
#P = I*V
power_average <- mean_amp * 5 *1000 #mwatts
print(power_average) #watts average over the 262 seconds

