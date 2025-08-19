# Mass Defect

- There are four different methods for mass defect figure.

  - Kendrick mass defect

  $$
      y_i = mz_i - round(mz_i)
  $$

  , where _mz_ is the m/z of the detected peak.

  - Kendrick mass defect with base-unit

  $$
      KM(mz, R) = mz * (round(R) / R)
  $$

  $$
      y_i = round(KM(mz_i, R)) -  KM(mz_i, R)
  $$

  , where _R_ is e.g. CH2, NO2, O, CH2O etc. base unit mass.

  - resolution enchanced Kendrick mass defect (REKMD)

  $$
      REKM(mz, R, X) = mz * (round(R/X) / R/X)
  $$

  $$
      y_i = REKM(mz_i, R, X) - round(REKM(mz_i, R, X))
  $$

  , where _X_ is integer divisors.

  - scaled Kendrick mass defect
    $$
        SKM(mz, R, X) = mz * (X/R)
    $$

  $$
      y_i = SKM(mz_i, R, X) - round(SKM(mz_i, R, X))
  $$
