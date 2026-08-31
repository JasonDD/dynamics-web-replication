# External-validity Spearman rho matrix (feature x corpus)

rho with the human label; asap_aes n=2243; ibm_argq n=2500; persuade_eff n=2499; persuade_essay n=2496
significance: * p<.05  ** p<.01  *** p<.001

| feature | asap_aes | ibm_argq | persuade_eff | persuade_essay |
|---|---|---|---|---|
| rigour | +0.278*** | +0.200*** | +0.227*** | +0.594*** |
| depth | +0.294*** | +0.208*** | +0.232*** | +0.555*** |
| originality | +0.032 | -0.029 | -0.072*** | +0.252*** |
| candour | -0.003 | +0.052** | +0.026 | +0.207*** |
| affect | +0.122*** | -0.072*** | -0.016 | -0.055** |
| commercial_drive | +0.192*** | +0.030 | +0.045* | +0.370*** |
| stance | +0.230*** | +0.068*** | +0.234*** | +0.480*** |
| register | +0.222*** | +0.109*** | +0.202*** | +0.147*** |
| matter_manner_PC1 | +0.167*** | +0.102*** | +0.185*** | +0.581*** |
| text_length | +0.490*** | +0.212*** | +0.082*** | +0.841*** |

## Partial Spearman rho controlling for text_length
(text_length row omitted; this asks whether an axis predicts the human label BEYOND essay/argument length)

| feature | asap_aes | ibm_argq | persuade_eff | persuade_essay |
|---|---|---|---|---|
| rigour | +0.155 | +0.161 | +0.220 | +0.181 |
| depth | +0.170 | +0.162 | +0.226 | +0.177 |
| originality | -0.120 | -0.062 | -0.076 | +0.020 |
| candour | -0.197 | +0.054 | +0.027 | +0.152 |
| affect | -0.118 | -0.087 | -0.019 | +0.012 |
| commercial_drive | +0.122 | -0.018 | +0.039 | +0.055 |
| stance | +0.008 | +0.033 | +0.228 | +0.276 |
| register | +0.116 | +0.091 | +0.201 | +0.200 |
| matter_manner_PC1 | -0.012 | +0.067 | +0.178 | +0.225 |
