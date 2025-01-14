# O que é

A Mobile Verification Toolkit (MVT) é uma coleção de utilitários projetados para simplificar e automatizar o processo de coleta de vestígios forenses úteis para identificar um possível comprometimento de dispositivos Android e iOS
Ela foi desenvolvida e lançada pelo Laboratório de Segurança da Anistia Internacional em julho de 2021, no contexto do Projeto Pegasus, juntamente com uma metodologia técnica forense. A ferramenta continua sendo mantida pela Anistia Internacional e outros colaboradores.

# Indicadores de compromisso

O MVT oferece suporte ao uso de indicadores públicos de comprometimento (IOCs) para escanear dispositivos móveis em busca de possíveis vestígios de ataque ou infecção por campanhas conhecidas de spyware. Isso inclui IOCs publicados pela Anistia Internacional e por outros grupos de pesquisa.

Aviso: Indicadores públicos de comprometimento são insuficientes para determinar que um dispositivo está "limpo" e não foi alvo de uma ferramenta específica de spyware. Confiar apenas em indicadores públicos pode deixar passar vestígios forenses recentes e gerar uma falsa sensação de segurança.

Um suporte forense digital confiável e abrangente, assim como uma triagem eficaz, requerem acesso a indicadores não públicos, pesquisas e inteligência sobre ameaças.

Esse suporte está disponível para a sociedade civil por meio do Security Lab da Anistia Internacional ou através de nossa parceria forense com a linha de apoio em segurança digital da Access Now.

Mais informações sobre o uso de indicadores de comprometimento com o MVT estão disponíveis na [documentação sobre IOCs](https://docs.mvt.re/en/latest/iocs/).


# Instalação

O MVT pode ser instalado a partir do código-fonte ou do [PyPI](https://pypi.org/project/mvt/) (você precisará de algumas dependências, consulte a [documentação](https://docs.mvt.re/en/latest/install/)):

Para instalar através do código fonte, abra o terminal do seu sistema operacional e digite

pip3 install mvt

# Uso da ferramenta

A ferramenta pode ser usada tanto para dispositivos ios quanto para dispositivos android.

