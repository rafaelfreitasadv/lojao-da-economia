# Suporte de celular para bicicleta ergométrica (console Athletic)

Suporte para **impressão 3D** que **abraça o tubo horizontal** do guidão (atrás do
visor) e segura o celular durante o cardio — **deitado (paisagem)** para assistir
vídeos e **em pé (retrato)** para Reels/Shorts. Sem precisar segurar na mão.

> **Por que braçadeira e não "apoiado":** o topo do console é todo curvo e
> inclinado, não tem parte plana. Prender no tubo redondo é o jeito firme e que
> não escorrega com a vibração do pedal.

![perspectiva](preview_1_perspectiva.png)

## Como funciona

- **Canal semicircular** por baixo que assenta no tubo (**~30–35 mm** + espuma).
- **Dois túneis passa‑correia:** uma **abraçadeira de nylon (zip‑tie)** ou uma
  **fita velcro** passa por dentro do túnel (por cima do tubo) e por baixo do
  tubo, e fecha — puxando o suporte firme contra a barra. **Sem furar, sem
  ferramenta.**
- **Encosto reclinado ~20°** + **calha inferior** que segura o celular nas duas
  posições, com a tela virada para o seu rosto enquanto pedala.
- **Recorte central** para o **cabo do carregador** e para tirar o celular.

| Montado no tubo | Celular deitado (vídeo) | Corte com medidas |
|---|---|---|
| ![perspectiva](preview_1_perspectiva.png) | ![deitado](preview_3_deitado.png) | ![cotas](preview_5_cotas.png) |

## Medidas da peça

- Tamanho final: **72 × 67 × 115 mm** (L × P × A)
- Canal do tubo: **Ø 36 mm** → serve tubo de **~30 a 35 mm** (a espuma acerta a folga)
- Calha do celular: **14 mm** (cabe celular com capa de até ~14 mm)
- Filamento: **~85 g** (+ um pouco de suporte) · tempo aprox.: **5–7 h**

Serve para praticamente qualquer celular: em pé ele encosta a traseira no encosto
e a base fica na calha; deitado ele sobra para os lados sem problema.

## ⚠️ Material — atenção ao sol

Pelas fotos a bike fica em **área externa, no sol**. **Não use PLA** (amolece perto
de 55–60 °C e entorta parado no sol). Prefira, nesta ordem:

1. **PETG** (recomendado) — barato, aguenta o calor e o sol.
2. **ASA** — melhor ainda para exterior/UV.
3. PLA **só** se a bike ficar sempre na sombra / coberta.

## 🖨️ Configurações de impressão

| Parâmetro | Valor |
|---|---|
| Orientação | **em pé**, do jeito que o arquivo abre (canal do tubo para baixo) |
| **Suportes** | **Sim** — para o **canal do tubo** e os **dois túneis** (use suporte "em árvore"; sai fácil) |
| Altura de camada | 0,2 mm |
| Paredes/perímetros | 3 a 4 |
| Preenchimento (infill) | 20–25 % |
| Material | PETG ou ASA (ver acima) |

Arquivo pronto: **`bike_phone_holder.stl`** — mande para a impressora / gráfica 3D.

## 🔧 Montagem no tubo

1. **Espuma/borracha no canal:** forre o canal semicircular com **EVA, um pedaço
   de câmara de ar de bike, ou fita de alta fixação**. Isso dá aderência, protege a
   pintura do tubo e acerta a folga para tubos de 30–33 mm.
2. **Encaixe** o suporte no **tubo horizontal atrás do visor**, no centro.
3. **Prenda:** passe **2 abraçadeiras de nylon** (ou uma **fita velcro** resistente)
   pelos **dois túneis**, contorne por baixo do tubo e **aperte bem firme**. As duas
   abraçadeiras separadas impedem que o suporte incline ou gire.
4. **Cabo:** passe o carregador pelo **recorte central** e ligue no celular.
5. Encaixe o celular na calha, encostado no encosto — em pé ou deitado.

> **Segurança:** com as duas abraçadeiras bem apertadas + espuma, fica firme para
> pedalar. Confira o aperto antes de pedalar em pé ou muito forte. Faça um teste
> chacoalhando de leve antes de confiar o celular.

## Quer ajustar a medida?

O modelo é **paramétrico**. No topo de `generate.py` estão as medidas — em especial
**`BAR_DIA`** (diâmetro do tubo) e **`GROOVE_DIA`** (canal). Para gerar sob medida:

```bash
pip install trimesh manifold3d shapely scipy numpy matplotlib
python3 generate.py
```

Isso regera o `.stl` e as imagens. Se preferir, **meça o tubo** (largura com régua,
ou passe um barbante em volta e me diga o comprimento) e eu gero a versão exata.
Se um dia quiser prender na **haste vertical**, também dá — é só avisar.
