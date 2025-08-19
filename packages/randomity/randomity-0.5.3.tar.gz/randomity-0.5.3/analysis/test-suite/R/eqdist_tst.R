eqdist_test <- function(data, min_val = 0, max_val = 10) {
  data_scaled <- (data - min_val) / (max_val - min_val)
  empirical_mean_val <- mean(data_scaled)
  expected_mean <- 0.5
  diff <- abs(empirical_mean_val - expected_mean)
  return(c(eqdist_empiricalMean = empirical_mean_val,
           eqdist_diff = diff))
}