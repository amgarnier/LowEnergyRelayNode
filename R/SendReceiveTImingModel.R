#ggplot library to build a heat map
library(ggplot2)

#Create the number_of_send and number_of_Listen variables from 1 to 300
nSend<- seq(1, 10000, by=1)
nListen<- seq(1,10000, by=1)

#binomial distribution probability funciton
success_binomial_prob <- function(listens,blocks,sends){
  p <- 1-((1-(listens/blocks))^sends)
  
  return(p)
}

#create intersecting line
createLineIntersectingLine <- function(xValue){
  probValue <- result_vary_listens[xValue]
  abline(v = xValue, col="red")
  abline(h = probValue, col="red")
  text(x=xValue, y = probValue, label = paste(xValue, signif(probValue,3) , sep=" , "),  adj=c(0,1.5))
       
}

#place results in a data frame

data<- list(send= nSend, listen=nListen, probability=success_binomial_prob(nListen,10000,nSend))
dataFrame<-as.data.frame(data)

#first plot the succesful binomial probability with the 7 listens and 15 send blocks
results <- success_binomial_prob(7,10000,15)

print(results)

#now we plot the visual assuming a set send value of 15
result_vary_listens <-  success_binomial_prob(nListen,10000,15)
plot(result_vary_listens[1:200],
    xlab= "number of listen shots",
    ylab="probability of succss",
    main="Probability of success in 10000 shots",
    sub = "send shots limited to 15")
createLineIntersectingLine(100)


#now create the plot to balance send and receive slots fix send shots to 50
result_vary_listens <-  success_binomial_prob(nListen,10000,150)
plot(result_vary_listens[1:400],
     xlab= "number of listen shots",
     ylab="probability of succss",
     main="Probability of success in 10000 shots",
     sub = "send shots limited to 150")
createLineIntersectingLine(150)


result_vary_sends <- success_binomial_prob(7,300,nSend)
lines(result_vary_sends, col = 'red', lwd = 5)

result_both <- success_binomial_prob(nListen,300, nSend)
plot(result_both)



