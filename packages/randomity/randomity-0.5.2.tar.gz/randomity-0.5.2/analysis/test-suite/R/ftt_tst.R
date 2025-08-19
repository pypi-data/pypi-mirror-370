ftt_test <- function(data) {
  n <- length(data)
  fft_result <- fft(data)
  magnitudes <- Mod(fft_result)
  frequencies <- (0:(n-1)) / n
  half_n <- floor(n / 2)
  if (half_n < 2) {
    return(c(fft_dominant_frequency = NA,
             fft_dominant_period = NA,
             fft_max_magnitude = NA))
  }
  dominant_index <- which.max(magnitudes[2:(half_n + 1)]) + 1
  dominant_magnitude <- magnitudes[dominant_index]
  dominant_frequency <- frequencies[dominant_index]
  dominant_period <- if (dominant_frequency > 0) 1 / dominant_frequency else NA
  return(c(fft_dominant_frequency = dominant_frequency,
           fft_dominant_period = dominant_period,
           fft_max_magnitude = dominant_magnitude))
}