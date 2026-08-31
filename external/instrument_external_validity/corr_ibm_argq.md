# ibm_argq  (n=2500)
outcome range 0.017..1.000  mean 0.791  sd 0.194

partial rho = Spearman of feature vs label controlling for text_length

| feature | Spearman rho | p | Pearson r | p | partial rho (ctrl length) |
|---|---|---|---|---|---|
| text_length | +0.212*** | 1.1e-26 | +0.209*** | 4.4e-26 | - |
| depth | +0.208*** | 6.9e-26 | +0.191*** | 5.3e-22 | +0.162 |
| rigour | +0.200*** | 6.9e-24 | +0.131*** | 4.6e-11 | +0.161 |
| register | +0.109*** | 5.3e-08 | +0.128*** | 1.5e-10 | +0.091 |
| matter_manner_PC1 | +0.102*** | 3.0e-07 | +0.108*** | 6.6e-08 | +0.067 |
| affect | -0.072*** | 3.1e-04 | -0.045* | 2.4e-02 | -0.087 |
| stance | +0.068*** | 7.0e-04 | +0.097*** | 1.3e-06 | +0.033 |
| candour | +0.052** | 9.3e-03 | +0.063** | 1.5e-03 | +0.054 |
| commercial_drive | +0.030 | 1.3e-01 | +0.013 | 5.0e-01 | -0.018 |
| originality | -0.029 | 1.4e-01 | -0.041* | 4.1e-02 | -0.062 |
