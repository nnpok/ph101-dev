#########################################################################
# Runs the autograder on a specified file_name.Rmd by stitching to file_name.R, 
# sourcing, and writing the output to results/results.json for parsing by gradescope
# 
# Example usage: Rscript autograde.R hw01.Rmd
#
# see https://gradescope-autograders.readthedocs.io/en/latest/specs/ for json required formatting
#########################################################################

# SETUP: test if there is at least one argument: if not, return an error
if (length(args)==0) {
  stop("At least one argument must be supplied (input file).n", call.=FALSE)
}

library(evaluate)
library(jsonlite)
library(knitr)

### Sources the file to be graded
args = commandArgs(trailingOnly = TRUE)
file_name = args[1]

# Converts .Rmd to .R and sources the file
purl(file_name)
capture.output(evaluate(file(gsub(".Rmd", ".R", file_name)), stop_on_error=0), file='NUL') # local test

#--------------------------------------------------------------------------------------
# generate_results_json

# Description: 

# Inputs:
#   - problemNumber: the number of the current question (integer)
#   - TODO
#--------------------------------------------------------------------------------------
generate_results_json = function() {
  tests = list()
  
  for (i in seq(1:length(scores))) {
    if (problem_types[i] == "autograded") { 
      tests = append(tests, list(list(score = as.numeric(scores[i]),
                                    max_score = as.numeric(max_scores[i]), 
                                    name = as.character(problem_names[i]), 
                                    number = as.character(i))))
    }
  }
  
  result <- list(visibility = "after_published",
                 stdout_visibility = "hidden",
                 tests = tests)
  
  scoresJSON = toJSON(result,
                      pretty=TRUE,
                      auto_unbox=TRUE)
  
  write(scoresJSON, file = "results/results.json")
}

generate_results_json()
