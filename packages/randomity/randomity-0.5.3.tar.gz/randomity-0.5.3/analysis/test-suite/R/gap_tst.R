gap_test <- function(data, min_val = 0, max_val = 10, num_bins = 11) {
  breaks <- seq(min_val, max_val + 1, length.out = num_bins + 1)
  binned <- cut(data, breaks = breaks, include.lowest = TRUE, right = FALSE, labels = FALSE)
  calculate_gaps <- function(binned_data) {
    gaps_list <- list()
    for (bin in unique(binned_data)) {
      indices <- which(binned_data == bin)
      if (length(indices) > 1) {
        gaps <- diff(indices)
        gaps_list <- c(gaps_list, gaps)
      }
    }
    return(unlist(gaps_list))
  }
  gaps <- calculate_gaps(binned)
  if (length(gaps) == 0) {
    return(c(gap_p = NA, gap_X2 = NA, gap_df = NA))
  }
  gap_freq <- table(gaps)
  expected <- rep(sum(gap_freq) / length(gap_freq), length(gap_freq))
  gap_test <- chisq.test(gap_freq, p = expected / sum(expected))
  return(c(gap_p = gap_test$p.value,
           gap_X2 = gap_test$statistic,
           gap_df = gap_test$parameter))
}