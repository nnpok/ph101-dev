## ----setup, include = FALSE---------------------------------------------------
# Don't change these lines, just run them!
source("setup/hw01.RAGS.R")


## -----------------------------------------------------------------------------
x <- "<<<<YOUR CODE HERE>>>>"
y <- "<<<<YOUR CODE HERE>>>>"

# BEGIN SOLUTION
x <- 2
y <- 8
# END SOLUTION

check_problem1()


## -----------------------------------------------------------------------------
z <- "<<<<YOUR CODE HERE>>>>"

# BEGIN SOLUTION
z <- x * y
# END SOLUTION

check_problem2()


## -----------------------------------------------------------------------------
# p3 <- "load"
# p3 <- "library"
# p3 <- "package"
# p3 <- "read"

# BEGIN SOLUTION
p3 <- "library"

# END SOLUTION
check_problem3()


## -----------------------------------------------------------------------------
library(nycflights13)
subsetFlights <- "<<<<YOUR CODE HERE>>>>"

# BEGIN SOLUTION
subsetFlights <- flights[1:10,]

# END SOLUTION
check_problem4()


## ----check-total-score--------------------------------------------------------
# Just run this chunk.
total_score()

