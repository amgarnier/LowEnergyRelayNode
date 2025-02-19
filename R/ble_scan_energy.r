library(DescTools)


#data set for low energy node scanning at full capacity or always running
setwd("~/Documents/LowPowerNodeRep/LowEnergyRelayNode/R")
ble_scan_full <- read.csv("ble_scan_full_fixed.csv")
ble_scan_df <- as.data.frame(ble_scan_full)

colnames(ble_scan_df)[1] <- "time" #add time as the column header
colnames(ble_scan_df)[2] <- "a" #since r=1 v=i so column2 is amps

#if we integrate using the trapezodial method over the plot and then divide by the number of values
#we get the average
ble_scan_df<-subset(ble_scan_df, ble_scan_df$time >= 0)
auc <- AUC(ble_scan_df$time, ble_scan_df$a, method = "trapezoid")
mean_amp <- auc / 3.2755 # integral/total time

#take the mean amps and multiply by volts to get power
#P = I*V
power_average_full <- mean_amp * 5 *1000 #mwatts
print("average power full time")
print(power_average_full) #watts average over the 131 seconds

#windowed data
ble_scan_full <- read.csv("ble_scan_windowed.csv")
ble_scan_df <- as.data.frame(ble_scan_full)

colnames(ble_scan_df)[1] <- "time" #add time as the column header
colnames(ble_scan_df)[2] <- "a" #since r=1 v=i so column2 is amps

#if we integrate using the trapezodial method over the plot and then divide by the number of values
#we get the average

ble_scan_df<-subset(ble_scan_df, ble_scan_df$time >= 0)

auc <- AUC(ble_scan_df$time, ble_scan_df$a, method = "trapezoid")
mean_amp <- auc / 131 # integral/total time

#take the mean amps and multiply by volts to get power
#P = I * V
power_average_windowed <- mean_amp * 5 * 1000 #mwatts
print(paste("average power ", power_average_windowed))
print(power_average_windowed) #watts average over the 262 seconds
print(paste("Power saved", ((power_average_full-power_average_windowed)/power_average_full) * 100, "%"))
