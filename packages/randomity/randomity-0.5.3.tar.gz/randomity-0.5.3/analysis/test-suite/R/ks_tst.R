ks_test <- function(data, min_val = 0, max_val = 10) {
  data_scaled <- (data - min_val) / (max_val - min_val)
  ks_test <- ks.test(data_scaled, "punif", min = 0, max = 1)
  return(c(ks_p = ks_test$p.value,
           ks_D = ks_test$statistic))
}