library(readxl)
library(dplyr)
library(stringr)
library(openxlsx)
library(ggplot2)
library(lubridate)
library(ggthemes)
library(gridExtra)


df <- read_excel('data.xlsx')
df$sent <- as.numeric(as.character(df$sent))
df$sent <- as.Date(df$sent, origin = "1899-12-30")
df$sent <- as.POSIXct(df$sent, format = "%Y-%m-%d")





t <- data.frame(table(df$company))
colnames(t) <- c('Company','Frequencies')



ggplot(t, aes(x = Frequencies , y = Company)) +
  geom_bar(stat = "identity", fill = "skyblue") +
  #geom_hline(yintercept = 40, linetype = "dashed", color = "red") +
  #geom_text(aes(label = ifelse(Frequencies > 30, Frequencies, "")), hjust=-1,size=3) +
  geom_text(aes(label = ifelse(Frequencies > 21 & Frequencies < 340, paste(as.character(Company),', ', as.character(Frequencies), sep = ""), "")),hjust=0,size=3,angle=60) +
  geom_text(aes(label = ifelse(Frequencies > 340, paste(as.character(Company),', ', as.character(Frequencies), sep = ""), "")),hjust=0,size=3,angle=0) +
  labs(y = "Frequency") +
  ggtitle("# Applications") +
  scale_y_discrete(labels = function(x) ifelse(t$Frequencies[match(x, t$Company)] > 40, '', "")) + #x if true
  
  scale_x_continuous(breaks = c(1,seq(10,350,30),max(t$Frequencies)), labels =as.character(c(1,seq(10,350,30),max(t$Frequencies)))) +
  theme(axis.text.y = element_text(angle = 90, hjust = 1, size = 7)) +
  theme_clean()


#ggsave("applications.png", plot = n_apps, width = 17.38, height = 8.33, dpi = 400)
print(n_apps)




#n_apps2 <-
ggplot(t, aes(x = Company, y = Frequencies)) +
  geom_bar(stat = "identity", fill = "skyblue") +
  geom_text(aes(label = ifelse(Frequencies > 21, paste(as.character(Frequencies), sep = ""), "")),vjust=-.1,size=3,angle=0) +
  labs(y = "Frequency") +
  ggtitle("# Applications") +
  scale_x_discrete(labels = function(x) ifelse(t$Frequencies[match(x, t$Company)] > 21, x, "")) +
  scale_y_continuous(breaks = c(1,seq(10,350,30),max(t$Frequencies)), labels =as.character(c(1,seq(10,350,30),max(t$Frequencies)))) +
  theme_classic() + 
  theme(axis.text.x = element_text(angle = 45, hjust = 1,size = 6.5,margin = margin(t = .2,unit = "cm"))) +
  theme(plot.title = element_text(face = "bold")) 





ggsave("applications.png", plot = n_apps2, width = 17.38, height = 8.33, dpi = 400)






ggplot(t, aes(x = Frequencies, y = Company)) +
  geom_bar(stat = "identity", fill = "skyblue") +
  #geom_text(aes(label = Frequencies))+
  geom_text(aes(label = ifelse(Frequencies > 19, as.character(Frequencies),""),vjust=-.5)) +
  labs(x = "Frequency") +
  ggtitle("# Applications") +
  scale_y_discrete(labels = function(x) ifelse(t$Frequencies[match(x, t$Company)] > 19, x, "")) +
  scale_x_continuous(breaks = c(1,seq(10,350,30),max(t$Frequencies)), labels =as.character(c(1,seq(10,350,30),max(t$Frequencies)))) +
  theme_classic() + 
  theme(
    plot.title = element_text(size = 11, face = "bold"), # Set title size and style
    axis.text.x = element_text(size = 10),
    axis.text.y = element_text(size = 5),
    
    plot.margin = unit(c(.1, .1, .1, .1), "cm") # Set plot margins (top, right, bottom, left)
  ) 






















posted <- data.frame(table(df$posting_date))
colnames(posted) <- c('Sent','Frequencies')

posted$Sent <- as.Date(posted$Sent) 
posted <- posted[order(posted$Sent), ]

posted$CumulativeNumbers <- cumsum(posted$Frequencies)


post_apps <- ggplot(posted, aes(x = Sent, y = CumulativeNumbers)) +
  geom_point() +
  geom_line() +
  labs(x = "Posting Dates", y = "Cumulative # of posted vacancies") +
  scale_x_date(date_labels = "%b %d", date_breaks = "10 day",
               limits = c(as.Date("2023-05-01"), max(posted$Sent))) +
  ggtitle("# Applications Posted ") +
  theme_clean()

print(post_apps)
ggsave("posted.png", plot = post_apps, width = 14.39, height = 8.46, dpi = 400)



pdf("/internship_report.pdf", width = 20, height = 10)
grid.arrange(n_apps2, post_apps, ncol = 1)
dev.off()







