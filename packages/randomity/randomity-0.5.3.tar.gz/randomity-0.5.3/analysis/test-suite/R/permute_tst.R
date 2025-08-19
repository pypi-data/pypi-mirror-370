permute_test <- function(data, block_size = 5) {
  calculate_statistic <- function(data, block_size) {
    num_blocks <- length(data) %/% block_size
    data_trimmed <- data[1:(num_blocks * block_size)]
    blocks <- matrix(data_trimmed, nrow = block_size, byrow = TRUE)
    block_means <- colMeans(blocks)
    return(mean(block_means))
  }
  permutation_test <- function(data, block_size, num_permutations = 1000) {
    observed_stat <- calculate_statistic(data, block_size)
    permuted_stats <- replicate(num_permutations, {
      permuted_data <- sample(data)
      calculate_statistic(permuted_data, block_size)
    })
    p_value <- mean(abs(permuted_stats - mean(permuted_stats)) >= 
                    abs(observed_stat - mean(permuted_stats)))
    return(c(perm_observed_stat = observed_stat, perm_p = p_value))
  }
  return(permutation_test(data, block_size))
}