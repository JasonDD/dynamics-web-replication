# asap_aes  (n=2243)
outcome range 0.000..1.000  mean 0.547  sd 0.296

partial rho = Spearman of feature vs label controlling for text_length

| feature | Spearman rho | p | Pearson r | p | partial rho (ctrl length) |
|---|---|---|---|---|---|
| text_length | +0.490*** | 7.1e-136 | +0.307*** | 3.5e-50 | - |
| depth | +0.294*** | 4.4e-46 | +0.295*** | 3.3e-46 | +0.170 |
| rigour | +0.278*** | 3.3e-41 | +0.260*** | 7.3e-36 | +0.155 |
| stance | +0.230*** | 3.0e-28 | +0.276*** | 2.1e-40 | +0.008 |
| register | +0.222*** | 1.8e-26 | +0.206*** | 5.0e-23 | +0.116 |
| commercial_drive | +0.192*** | 4.8e-20 | +0.170*** | 6.1e-16 | +0.122 |
| matter_manner_PC1 | +0.167*** | 1.6e-15 | +0.195*** | 1.1e-20 | -0.012 |
| affect | +0.122*** | 7.4e-09 | +0.148*** | 1.8e-12 | -0.118 |
| originality | +0.032 | 1.3e-01 | +0.043* | 4.4e-02 | -0.120 |
| candour | -0.003 | 8.7e-01 | +0.029 | 1.6e-01 | -0.197 |
