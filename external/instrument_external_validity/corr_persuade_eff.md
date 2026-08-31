# persuade_eff  (n=2499)
outcome range 0.000..2.000  mean 1.000  sd 0.816

partial rho = Spearman of feature vs label controlling for text_length

| feature | Spearman rho | p | Pearson r | p | partial rho (ctrl length) |
|---|---|---|---|---|---|
| stance | +0.234*** | 2.2e-32 | +0.220*** | 1.2e-28 | +0.228 |
| depth | +0.232*** | 9.3e-32 | +0.199*** | 8.2e-24 | +0.226 |
| rigour | +0.227*** | 1.6e-30 | +0.139*** | 3.3e-12 | +0.220 |
| register | +0.202*** | 1.7e-24 | +0.196*** | 4.4e-23 | +0.201 |
| matter_manner_PC1 | +0.185*** | 1.4e-20 | +0.178*** | 3.8e-19 | +0.178 |
| text_length | +0.082*** | 4.3e-05 | +0.078*** | 9.2e-05 | - |
| originality | -0.072*** | 3.2e-04 | -0.073*** | 2.6e-04 | -0.076 |
| commercial_drive | +0.045* | 2.4e-02 | +0.010 | 6.1e-01 | +0.039 |
| candour | +0.026 | 1.9e-01 | +0.037 | 6.4e-02 | +0.027 |
| affect | -0.016 | 4.3e-01 | -0.020 | 3.1e-01 | -0.019 |
