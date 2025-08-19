entropy_test <- function(data, min_val = 0, max_val = 10, num_bins = 11) {
  breaks <- seq(min_val, max_val + 1, length.out = num_bins + 1)
  bins <- cut(data, breaks = breaks, include.lowest = TRUE, right = FALSE)
  freq_table <- table(bins)
  probabilities <- freq_table / sum(freq_table)
  entropy_value <- -sum(probabilities * log2(probabilities + 1e-10))
  return(c(entropy_val = entropy_value))
}