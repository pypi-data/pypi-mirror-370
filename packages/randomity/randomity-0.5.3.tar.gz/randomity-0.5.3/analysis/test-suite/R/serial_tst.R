serial_test <- function(data, min_val = 0, max_val = 10) {
  data_scaled <- (data - min_val) / (max_val - min_val)
  if (var(data) == 0) {
    return(c(serial_autocorrelation = NA))
  }
  serial_test <- cor(data_scaled[-length(data_scaled)], data_scaled[-1])
  return(c(serial_autocorrelation = serial_test))
}