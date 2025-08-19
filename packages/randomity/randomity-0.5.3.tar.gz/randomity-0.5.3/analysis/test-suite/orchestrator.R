required_packages <- c("dplyr", "tidyverse")
installed_packages <- installed.packages()[, "Package"]
for (pkg in required_packages) {
  if (!(pkg %in% installed_packages)) {
    install.packages(pkg, repos = "http://cran.us.r-project.org")
  }
}

library(dplyr)
library(tidyverse)

source("R/chisqr_tst.R")
source("R/ks_tst.R")
source("R/freq_tst.R")
source("R/eqdist_tst.R")
source("R/gap_tst.R")
source("R/serial_tst.R")
source("R/permute_tst.R")
source("R/entropy_tst.R")
source("R/ftt_tst.R")

orchestrator <- function() {
  print("Starting feature extraction...")
  print("Current directory is:")
  print(getwd())

  sequences <- list.files(path = "Data", pattern = "\\.csv$", full.names = TRUE)
  print("Got sequences...")

  result_list <- list()

  for (i in seq_along(sequences)) {
    print(paste("Processing sequence", i, "of", length(sequences)))
    file <- basename(sequences[i])
    seq_label <- tools::file_path_sans_ext(file)
    seq_num <- as.integer(sub("randoms-", "", seq_label))

    source <- if (seq_num <= 60) "QRNG" else "PRNG"
    generator <- case_when(
      seq_num <= 60 ~ "IBM Qiskit (Single-Qubit)",
      seq_num <= 80 ~ "Mersenne Twister (MT19937)",
      seq_num <= 100 ~ "Linear Congruential Generator (LCG)",
      seq_num <= 120 ~ "XORShift",
      TRUE ~ NA_character_
    )

    data <- read.csv(sequences[i], header = TRUE)
    seq_numbers <- data$n

    res_chisqr <- chisqr_test(seq_numbers)
    res_ks <- ks_test(seq_numbers)
    res_freq <- freq_test(seq_numbers)
    res_eqdist <- eqdist_test(seq_numbers)
    res_gap <- gap_test(seq_numbers)
    res_serial <- serial_test(seq_numbers)
    res_permute <- permute_test(seq_numbers)
    res_entropy <- entropy_test(seq_numbers)
    res_ftt <- ftt_test(seq_numbers)

    result_vector <- c(index = i,
                       sequence_label = seq_label,
                       source = source,
                       generator = generator,
                       res_chisqr,
                       res_ks,
                       res_freq,
                       res_eqdist,
                       res_gap,
                       res_serial,
                       res_permute,
                       res_entropy,
                       res_ftt)

    result_list[[i]] <- as.data.frame(t(result_vector),
                                      stringsAsFactors = FALSE)
  }

  features_df <- bind_rows(result_list) %>%
    mutate(across(where(is.character) & !c("sequence_label",
                                           "source",
                                           "generator"),
                  as.numeric))

  print("Saving features dataframe...")
  write.csv(features_df, "feature_vector.csv", row.names = FALSE)
  print("Feature extraction completed and saved to feature_vector.csv")

  return(features_df)
}

orchestrator()
