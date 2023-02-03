#CODE 1 = Proportional Stacked Area Graph

#import files

library(rvest)
library(tidyverse)
library(dplyr)
library(ggplot2)
library(datasets)
library(reshape2)


#set working directory and load files 
setwd("~/DS105_Project")
table_main2_file <- read.csv("processedplayers.txt")

#creating different dataframes
table_mmr_race_league <- table_main2_file[, c("mmr","race", "league")]
table_mmr_race_region <- table_main2_file[, c("mmr","race", "region")]
table_race_league <- table_main2_file[, c("race", "league")]


#editing the format of the variables and creating a dataframe with the percentages

table_race_league$league <- as.factor(table_race_league$league)
table_race_league$race <- as.factor(table_race_league$race)
view(table_race_league)

main_table <- table_race_league %>% group_by(race, league) %>%
  tally()

main_final_table <- transform(main_table, percent = ave(n, league, FUN = prop.table))

#creating the Proportional Stacked Area Graph.

main_final_table2 <- main_final_table[!(main_final_table$race=="Unknown" |main_final_table$race=="unknown"),]

main_final_table2$league <- factor(main_final_table2$league , levels=c("Bronze 3", "Bronze 2", "Bronze 1", "Silver 3", "Silver 2", "Silver 1", "Gold 3", "Gold 2", "Gold 1", "Diamond 3", "Diamond 2", "Diamond 1", "Masters 3", "Masters 2", "Masters 1", "Grandmaster 1"))
main_final_table2$race <- factor(main_final_table2$race , levels=c("RANDOM", "ZERG", "PROTOSS", "TERRAN"))

final_graph_1 <- ggplot(main_final_table2, (aes(x = league,  y = percent, fill = race, group = race))) +
  geom_area(alpha=0.6 , linewidth=0.3, colour="black") +   scale_fill_manual(values=c('grey', '#5519BD', '#FFFF40', '#244CB9'))

#to view the graph
final_graph_1

#----------------------------------------------------------------------------------

#CODE 2 = Heatmap of times people play Starcraft 2

#import the packages

library(rvest)
library(tidyverse)
library(dplyr)
library(ggplot2)
library(datasets)
library(plotly)
library(lubridate)

#set working directory and load files 
setwd("~/DS105_Project")
matches_full <- read.csv("matchesdata.txt")

#Grpah - time heat map

matches_full_only_1v1 <- matches_full %>% filter(X7=="1v1")

main_dataframe_matches <- matches_full_only_1v1 %>% 
  mutate(new_timezone=if_else(X4 == 1, 
                              as.POSIXct(X10, origin="1970-01-01", timezone="America/New_York"), 
                              if_else(X4 == 2, 
                                      as.POSIXct(X10, origin="1970-01-01", tz="Europe/London"),
                                      as.POSIXct(X10, origin="1970-01-01", tz="KR time" ))   ))


#creating new coloumns (in 'main_dataframe_matches' dataframe) for day and hour

main_dataframe_matches$weekday <- weekdays(as.Date(main_dataframe_matches$new_timezone))

main_dataframe_matches$hour_min_sec <- substr(main_dataframe_matches$new_timezone, 12, 19)

main_table_heatmap <- data.frame(main_dataframe_matches$weekday, main_dataframe_matches$hour_min_sec, main_dataframe_matches$X4)

#making a new coloumn in the 'heatmap dataframe' with just the hour, and categorizing the hour and weekday coloumn

main_table_heatmap$hour <- hour(hms(main_table_heatmap$main_dataframe_matches.hour_min_sec))

hr_breaks = seq(0, 25, by = 1)
hr_labels <- c('00', '01', '02', '03', '04', '05', '06', '07', '08', '09',
               '10', '11', '12', '13', '14', '15', '16', '17', '18', '19',
               '20', '21', '22', '23', '24')

main_table_heatmap$ordered_time = cut(main_table_heatmap$hour, breaks = hr_breaks, 
                                      labels = hr_labels,
                                      include.lowest = T, right = F)


main_table_heatmap$ordered_time <- factor(main_table_heatmap$ordered_time,
                                          levels=c('24', '23', '22', '21', '20', '19', 
                                                   '18', '17', '16', '15',
                                                   '14', '13', '12', '11', '10', '09',
                                                   '08', '07', '06', '05',
                                                   '04', '03', '02', '01', '00'))


main_table_heatmap$main_dataframe_matches.weekday <- factor(main_table_heatmap$main_dataframe_matches.weekday,
                                                            levels=c('Monday', 'Tuesday', 'Wednesday', 'Thursday',
                                                                     'Friday', 'Saturday', 'Sunday'))

#final step is to create the Heatmap

final_graph_heatmap_main <- ggplot(data= main_table_heatmap, aes(main_dataframe_matches.weekday, ordered_time, frame = main_dataframe_matches.X4)) + geom_bin2d() +  xlab(label = "weekday") + ylab(label = "hour") +
  scale_fill_gradient(low = "deepskyblue", high = "midnightblue") 


#to view the graph

final_graph_heatmap_main 






