freq_test <- function(data, min_val = 0, max_val = 10, num_bins = 11) {
  breaks <- seq(min_val, max_val + 1, length.out = num_bins + 1)
  freq <- table(cut(data, breaks = breaks, include.lowest = TRUE, right = FALSE))
  expected <- rep(length(data) / num_bins, num_bins)
  chi_test <- chisq.test(freq, p = expected / sum(expected))
  return(c(freq_p = chi_test$p.value,
           freq_X2 = chi_test$statistic,
           freq_df = chi_test$parameter))
}