chisqr_test <- function(data, min_val = 0, max_val = 10) {
  bins <- cut(data, breaks = seq(min_val, max_val + 1, by = 1), 
              include.lowest = TRUE, right = FALSE)
  freq <- table(bins)
  expected <- rep(length(data) / (max_val - min_val + 1), max_val - min_val + 1)
  chi_test <- chisq.test(freq, p = expected / sum(expected))
  return(c(chisqr_p = chi_test$p.value,
           chisqr_X2 = chi_test$statistic,
           chisqr_df = chi_test$parameter))
}