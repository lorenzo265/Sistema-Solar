# AUTOPSIA DO REPOSITORIO - simulador_orbitas

**Data:** 2026-05-07
**Analista:** Claude Sonnet via Cowork
**Veredicto geral:** RECUPERAVEL (estrutura funcional, mas arquitetura acoplada e cheia de magic numbers)

---

## RESUMO EXECUTIVO

O projeto funciona e a fisica esta correta, mas o codigo cresceu sem separacao de responsabilidades.
main.py acumula 5 papeis distintos. physics.py mistura integracao numerica com deteccao de colisao.
renderer.py conhece estado de jogo que nao e seu. Ha 95 ocorrencias de magic numbers e variaveis
genericas. Zero testes automatizados. Nenhum arquivo de configuracao centralizado.
O codigo e explicavel em sala de aula, mas nao e facil de estender sem quebrar algo.

---

## INVENTARIO

| Metrica                        | Valor                     |
|-------------------------------|---------------------------|
| Arquivos .py analisados        | 4                         |
| Linhas de codigo total         | 528                       |
| Linhas de teste                | 0 (0% de cobertura)       |
| Dependencias declaradas        | 4 (todas usadas)          |
| Commits                        | nao ha repositorio git    |
| God Classes (+300 linhas)      | 0                         |
| God Functions (+40 linhas)     | 3 (update, main, _check_collisions) |
| Magic numbers identificados    | 67                        |
| Variaveis genericas (n, x, a)  | 28                        |
| Excecoes silenciadas           | 0                         |
| Imports desnecessarios         | 2 (GLU em main e renderer)|
| Constantes sem arquivo proprio | 8 (G, MIN_DIST, TRAIL_LENGTH, FPS, WIDTH, HEIGHT, COLORS, MAX_HUD_PLANETS) |

---

## DIAGNOSTICO POR DIMENSAO

### Arquitetura
**Veredicto: GRAVE**

main.py tem 5 responsabilidades distintas misturadas:
- Criacao de cenarios (create_initial_bodies)
- Fabrica de planetas com calculo orbital (add_orbital_planet)
- Configuracao da janela OpenGL (setup_opengl)
- Loop de eventos e input
- Orquestracao fisica + render

physics.py tem 2 responsabilidades:
- Integracao numerica de Euler (update)
- Deteccao e fusao de colisoes (_check_collisions)

renderer.py conhece game state que nao e seu:
- draw_hud() recebe `paused` e `bodies` -- acoplado ao estado do jogo
- Qualquer mudanca no estado do jogo exige mudanca no renderer

Pior ofensor: main.py:148 def main() = 52 linhas, mistura input + fisica + render + estado.

---

### Qualidade de Codigo
**Veredicto: MODERADO**

Magic numbers sem nome (67 ocorrencias):
  - renderer.py:43  sides = 64         -- por que 64? nao documentado
  - renderer.py:105 line_height = 18   -- hardcoded, nao escala com resolucao
  - physics.py:21   G = 500.0          -- valor magico sem referencia ao espaco de pixels
  - body.py:40      mass ** 0.4        -- expoente sem nome nem justificativa
  - main.py:31      WIDTH, HEIGHT = 900, 700  -- duplicado de qualquer config futura
  - main.py:78      v_orbital * fator * random.uniform(0.7, 1.3) -- 0.7 e 1.3 magicos

Variaveis genericas (28 ocorrencias):
  - physics.py:42   n = len(bodies)    -- poderia ser `num_bodies`
  - physics.py:50   a = bodies[i]      -- poderia ser `body_a`
  - renderer.py:73  n = len(trail)     -- poderia ser `trail_len`
  - varios x, dist usados como nomes de loop sem contexto

Inconsistencias de estilo:
  - glColor3f() usado em draw_circle, draw_text, draw_hud
  - glColor4f() usado apenas em draw_trail
  - Sem razao documentada para a inconsistencia

---

### Error Handling
**Veredicto: MODERADO**

Sem nenhuma excecao silenciada (bom).
Mas tambem sem nenhum tratamento de erros reais:
  - Se glutInit falhar, o programa crasha sem mensagem util
  - Se pygame nao inicializar display OpenGL, crasha sem mensagem
  - Se bodies ficar vazio (todos absorvidos pelo sol), physics.update nao crashea mas o comportamento e indefinido
  - Nao ha validacao de argumentos em nenhuma funcao publica
  - add_orbital_planet usa max(..., 50) para evitar divisao por zero, mas sem comentario explicando o motivo

---

### Testes
**Veredicto: CRITICO**

Zero arquivos de teste. Zero cobertura automatizada.
Os unicos testes existentes foram scripts pontuais rodados via python -c "..." durante o desenvolvimento.
Nenhum pytest, nenhum fixture, nenhuma assertion permanente.

Componentes criticos sem cobertura:
  - _check_collisions(): logica de fusao com momento linear
  - update(): integracao numerica e estabilidade orbital
  - add_orbital_planet(): calculo de velocidade tangencial
  - draw_hud(): overflow de texto com muitos planetas

---

### Seguranca
**Veredicto: OK**

Nao aplicavel em profundidade para um jogo local sem rede.
Sem credenciais, sem SQL, sem I/O de arquivos externos.
Paths hardcoded ausentes. Sem entrada de usuario nao sanitizada.

---

### Coerencia com Requisitos do Projeto
**Veredicto: BOM**

Requisitos originais (jogo educativo simples com PyOpenGL):
[OK] Usa PyOpenGL como motor principal
[OK] Logica simples e comentada
[OK] Fisica real (gravitacao de Newton, momento linear)
[OK] Interacao basica (clicar para adicionar, espaco para pausar)
[FALTANDO] Nenhuma estrutura de missoes ou desafios educativos
[FALTANDO] Nenhum controle de velocidade do tempo
[FALTANDO] Nenhuma telemetria educativa (periodo orbital, excentricidade)

---

## TOP 15 PROBLEMAS (ordenados por impacto)

| #  | Severidade | Problema                                        | Arquivo          |
|----|------------|-------------------------------------------------|------------------|
| 1  | CRITICO    | Zero testes automatizados                        | todos            |
| 2  | GRAVE      | main.py com 5 responsabilidades distintas        | main.py:148      |
| 3  | GRAVE      | physics.update() mistura fisica e colisao        | physics.py:28    |
| 4  | GRAVE      | renderer.draw_hud() acoplado ao game state       | renderer.py:97   |
| 5  | GRAVE      | Sem arquivo de configuracao centralizado         | todos            |
| 6  | MODERADO   | 67 magic numbers espalhados sem nome             | renderer.py, main.py |
| 7  | MODERADO   | Sem limite de velocidade maxima em physics       | physics.py       |
| 8  | MODERADO   | Orbitas de Euler acumulam energia (drift longo)  | physics.py:74    |
| 9  | MODERADO   | G e MIN_DIST sem referencia ao espaco de pixels  | physics.py:21    |
| 10 | MODERADO   | imports desnecessarios: GLU em main e renderer   | main.py, renderer.py |
| 11 | MODERADO   | numpy importado diretamente em main.py           | main.py:102      |
| 12 | MODERADO   | glColor3f/4f inconsistentes sem motivo           | renderer.py      |
| 13 | MODERADO   | Planet sem __repr__ (debug dificil)              | body.py          |
| 14 | MODERADO   | Sem validacao de range em Planet.color           | body.py          |
| 15 | COSMETICO  | Variaveis a, b, n em loops (nomes genericos)     | physics.py       |

---

## VEREDICTO FINAL

O codigo e funcional e pedagogicamente honesto: cada conceito fisico aparece em um lugar claro.
Isso e o ponto forte real do projeto.

O problema nao e o que esta errado -- e o que vai dificultar crescer.
main.py ja esta sobrecarregado e qualquer nova feature (missoes, telemetria, cenarios) vai
entrar ali e tornar o arquivo ilegivel. physics.py vai ganhar mais fisica e mais deteccao de
colisao no mesmo lugar. renderer.py vai ganhar mais elementos visuais acoplados ao estado do jogo.

A ausencia total de testes e o risco mais alto: qualquer refatoracao pode quebrar a fisica
e o programador so vai descobrir rodando o jogo e "achando que parece errado".

O que salvar: a logica de fisica em physics.py e correta e bem comentada.
O que refatorar: main.py, renderer.py (separar HUD do renderer puro).
O que adicionar: config.py, tests/, e os 5 features educativos descritos no remodel_proposal.
