#########################################################################
# Basic functions for providing test cases for students, providing
# feedback, and autograding assignments
#
#########################################################################

# Load dependencies
suppressWarnings(library(jsonlite))
suppressWarnings(library(dplyr))
suppressWarnings(library(assertthat))
suppressWarnings(library(rlang))

#--------------------------------------------------------------------------------------
# setup_autograder

# Description: Initializes vector to track scores for each problem

# Inputs:
#   - num_questions: number of questions in the assignment (integer)
#--------------------------------------------------------------------------------------

setup_autograder <- function(num_questions) {
  scores <<- vector(mode="character", length=num_questions)  
  for (problem_num in 1:num_questions){
    scores[problem_num] <<- 0
  }
  
  max_scores <<- vector(mode="character", length=num_questions)  
  for (problem_num in 1:num_questions){
    max_scores[problem_num] <<- 0
  }
  
  problem_names <<- vector(mode="character", length=num_questions)  
  for (problem_num in 1:num_questions){
    problem_names[problem_num] <<- paste0("Problem ", problem_num)
  }
  
  problem_types <<- vector(mode="character", length=num_questions)  
  for (problem_num in 1:num_questions){
    problem_types[problem_num] <<- "autograded"
  }
}

#--------------------------------------------------------------------------------------
# test_case

# Description: Checks student work using assert_that test cases.
#   Autograder will stop running after the first failed test case 
#   and show the student's progress for the question. 
#   Used for questions where there is a logical order to test cases.

# Inputs:
#   - test: conditional statement that checks student work. Evaluates to 
#           TRUE if correct, FALSE if incorrect (boolean)
#   - error_message: Message to display if a student fails the test case.
#--------------------------------------------------------------------------------------

test_case <- function(test, error_message = "Test Failed"){
  if (test) {
    tests_failed <<- tests_failed - 1
  } else {
    return_score(problem_num, num_tests, tests_failed)
    assert_that(test, msg = error_message)
  }
}

#--------------------------------------------------------------------------------------
# checkpoint

# Description: Checks student work using print statements.
#   Autograder will run through all checkpoints, regardless of how students
#   answered the question. Feedback statements will be provided to students 
#   depending if they passed/failed the test case.
#   Used for questions where there is no logical order to test cases, or if
#   test cases are unrelated

# Inputs:
#   - checkpoint_number: the number of the checkpoint within the questions (integer)
#   - test: conditional statement that checks student work. Evaluates to 
#           TRUE if correct, FALSE if incorrect (boolean)
#   - correct_message: Message to display if a student passes the test case. (string)
#   - error_message: Message to display if a student fails the test case. (string)
#--------------------------------------------------------------------------------------

checkpoint <- function(checkpoint_number, test, correct_message = "", error_message = ""){
  correct <- sprintf("Checkpoint %d Passed", checkpoint_number)
  if (nchar(correct_message) != 0){
    correct <- paste0(correct, ": ", correct_message)
  }
  
  error <- sprintf("Checkpoint %d Error", checkpoint_number)
  if (nchar(error_message) != 0){
    error <- paste0(error, ": ", error_message)
  }
  
  suppressMessages(suppressWarnings(tryCatch({
    if (test) {
      tests_failed <<- tests_failed - 1
      print(correct)
    } else {
      print(error)
    }
  }, error = function(e) {
    print(error)
  }
  )))
  

}

#--------------------------------------------------------------------------------------
# return_score

# Description: Returns a student's progress on a particular question. Displays the 
#   number of test cases passed, the number of test cases failed, the percent of 
#   test cases passed, and the overall question score.

# Inputs:
#   - problem_num: the number of the current question (integer)
#   - num_tests: the total number of test cases related to the question (integer)
#   - num_failed: the total number of test cases failed in the question (integer)
#--------------------------------------------------------------------------------------

return_score <- function(problem_num, num_tests, num_failed) {
  num_passed <- num_tests - num_failed
  score <- ifelse(num_failed == 0, "PASSED", "FAILED")
  
  if (problem_types[problem_num] == "autograded") {
    cat(sprintf("\nProblem %d\nCheckpoints Passed: %d\nCheckpoints Errored: %d\n%g%% passed\n--------\nTest: %s\n", 
              problem_num, num_passed, num_failed, round(num_passed/num_tests * 100, digits = 2), score))
  } else {
    cat(sprintf("\nProblem %d\nTest: NOT YET GRADED\n", 
                problem_num, num_passed, num_failed, round(num_passed/num_tests * 100, digits = 2), score))
  }
}

#--------------------------------------------------------------------------------------
# total_score

# Description: Renders scores from each problem and returns as a dataframe.
#   Runs at the end of each assignment script to display overall student progress.
#--------------------------------------------------------------------------------------
total_score <- function() {
  # To display scores vector instead, substitute scores for the first column
  rendered_score <- data.frame(Test = ifelse(as.numeric(scores), "PASSED", "FAILED"), Points_Possible = max_scores, Type = problem_types)
  
  # Correct frq status to UNGRADED
  rendered_score$Test <- ifelse(rendered_score$Type == "autograded", as.character(rendered_score$Test), "NOT YET GRADED")
  
  ag_total_score <- 0
  ag_pts_possible <- 0
  frq_pts_possible <- 0
  
  for (problem_num in 1:length(scores)) {
    if (problem_types[problem_num] == "autograded") {
      ag_total_score <- ag_total_score + as.numeric(scores[problem_num])
      ag_pts_possible <- ag_pts_possible + as.numeric(max_scores[problem_num])
    } else if (problem_types[problem_num] == "frq") {
      frq_pts_possible <- frq_pts_possible + as.numeric(max_scores[problem_num])
    }
  }
  
  # For totaling scores
  # rendered_score <- add_row(rendered_score, Score = ag_total_score, Points_Possible = ag_pts_possible, Type = "--")
  # rendered_score <- add_row(rendered_score, Score = "?", Points_Possible = frq_pts_possible, Type = "--")
  # rendered_score <- add_row(rendered_score, Score = ag_total_score, Points_Possible = sum(as.numeric(max_scores)), Type = "--")
  
  for (problem_num in 1:nrow(rendered_score)) {
    rownames(rendered_score)[problem_num] <- problem_names[problem_num]
  }
  
  # Naming score totals rows
  # rownames(rendered_score)[length(scores) + 1] <- "Subtotal (autograded)"
  # rownames(rendered_score)[length(scores) + 2] <- "Subtotal (free-response)"
  # rownames(rendered_score)[length(scores) + 3] <- "Total"
  return(rendered_score)
}




