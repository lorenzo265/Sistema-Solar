# Simulador de Órbitas

Um simulador gravitacional 2D em tempo real, escrito em Python com **PyOpenGL** + **Pygame** + **NumPy**. O objetivo é didático: tornar visível o que normalmente fica escondido em equações — força gravitacional, energia orbital, conservação de momento, leis de Kepler.

> Clique em qualquer ponto da tela e um planeta aparece, já com a velocidade tangencial certa para entrar em órbita. Aperte `V` e você passa a *ver* a força gravitacional como uma seta vermelha em cada corpo.

---

## Sumário

1. [Como rodar](#1-como-rodar)
2. [Controles](#2-controles)
3. [A física por trás da simulação](#3-a-física-por-trás-da-simulação)
4. [Arquitetura: o caminho de um frame](#4-arquitetura-o-caminho-de-um-frame)
5. [Cada arquivo, por dentro](#5-cada-arquivo-por-dentro)
   - [config.py](#51-configpy--o-painel-de-controle)
   - [body.py](#52-bodypy--o-que-é-um-planeta)
   - [physics.py](#53-physicspy--gravidade-integração-e-colisão)
   - [scenarios.py](#54-scenariospy--cenários-iniciais-e-fábrica-de-planetas)
   - [renderer.py](#55-rendererpy--primitivas-de-desenho)
   - [hud.py](#56-hudpy--interface-de-informações)
   - [missions.py](#57-missionspy--modo-missão)
   - [main.py](#58-mainpy--o-loop-principal)
6. [As 5 features educativas](#6-as-5-features-educativas)
7. [Testes](#7-testes)
8. [Decisões de projeto](#8-decisões-de-projeto)

---

## 1. Como rodar

```bash
# (Opcional) usar o venv que já vem no projeto
.\env\Scripts\activate

# Instalar dependências
pip install -r requirements.txt

# Rodar a simulação
python main.py

# Rodar os testes (23 testes)
python -m pytest tests -q
```

**Dependências:** `pygame`, `PyOpenGL`, `PyOpenGL_accelerate`, `numpy`, `pytest`.

---

## 2. Controles

| Tecla / ação            | Efeito                                                              |
|-------------------------|---------------------------------------------------------------------|
| **Clique esquerdo**     | Adiciona um planeta no cursor com velocidade tangencial orbital     |
| **Espaço**              | Pausa / continua a simulação                                        |
| **+ / −**               | Aumenta / reduz a velocidade do tempo (0.25× → 4×)                  |
| **1 / 2 / 3**           | Carrega um cenário (sistema solar / estrelas binárias / lua)        |
| **V**                   | Liga / desliga as setas de força gravitacional                      |
| **M**                   | Avança para a próxima missão                                        |
| **R**                   | Reinicia o cenário atual                                            |
| **Q** / fechar janela   | Encerra                                                             |

---

## 3. A física por trás da simulação

Toda a simulação se sustenta em **três leis de Newton** e uma equação:

### 3.1. Lei da Gravitação Universal

$$F = G \cdot \frac{m_1 \cdot m_2}{r^2}$$

Cada par de corpos se atrai com uma força proporcional ao produto das massas e inversamente proporcional ao quadrado da distância. O `G` aqui não é o `6.67 \times 10^{-11}` real — usamos `G = 500` para que o movimento seja visível em pixels e segundos.

### 3.2. Segunda Lei de Newton

$$a = F / m$$

Convertemos a força em aceleração para cada corpo. Note que dois corpos sentem a *mesma força* mas *acelerações diferentes* — quem tem mais massa acelera menos. É por isso que o sol fica praticamente parado e os planetas é que correm.

### 3.3. Integração de Euler semi-implícita

A cada frame, dado um intervalo `dt`:

```
v ← v + a · dt        # primeiro atualiza a velocidade
x ← x + v · dt        # depois usa a NOVA velocidade pra mover
```

Essa ordem (semi-implícita) é mais estável para sistemas orbitais que a Euler clássica (`x ← x + v·dt; v ← v + a·dt`), mesmo sendo só uma linha trocada de lugar.

### 3.4. Velocidade orbital circular

Para que um corpo entre em órbita circular ao redor de outro:

$$v_{\text{orbital}} = \sqrt{\frac{G \cdot M}{r}}$$

É essa fórmula que faz o clique do mouse criar um planeta que *de fato orbita* em vez de cair direto no sol.

### 3.5. Velocidade de escape

$$v_{\text{escape}} = \sqrt{\frac{2 \cdot G \cdot M}{r}}$$

Se um corpo passar dessa velocidade, sua energia mecânica fica positiva e ele escapa do sistema. O HUD marca cada corpo como `[OK]` (ligado) ou `[ESC]` (escapando).

---

## 4. Arquitetura: o caminho de um frame

```
┌──────────────────────────────────────────────────────────────┐
│                       LOOP PRINCIPAL                         │
│                                                              │
│   [INPUT]            [FÍSICA]              [RENDER]          │
│   pygame.event   →   physics.update    →   renderer.render   │
│   - clique           - compute_accel       - clear           │
│   - teclas           - step (Euler)        - trilhas         │
│                      - check_collisions    - planetas        │
│                                            - força (V)       │
│                                            - hud.draw        │
└──────────────────────────────────────────────────────────────┘
        │                  │                       │
        ▼                  ▼                       ▼
   scenarios.py       physics.py              renderer.py
   missions.py        body.py                 hud.py
                      config.py               (config.py)
```

Cada módulo tem **uma responsabilidade**:

- **config.py** guarda *números* (constantes). Não tem lógica.
- **body.py** define *o que é* um planeta. Não calcula nada.
- **physics.py** calcula *como o universo evolui*. Não desenha.
- **scenarios.py** sabe *quem está no palco no início*. Não calcula física.
- **renderer.py** sabe *como desenhar primitivas* (círculos, linhas, texto). Não conhece o jogo.
- **hud.py** sabe *qual informação mostrar*. Usa o renderer como ferramenta.
- **missions.py** sabe *quais desafios existem*. Avalia o estado a cada frame.
- **main.py** orquestra tudo.

Esse desacoplamento permite testar a física **sem abrir uma janela** (e os testes fazem exatamente isso).

---

## 5. Cada arquivo, por dentro

### 5.1. `config.py` — o painel de controle

Todas as constantes do projeto vivem aqui. Quer ver o sol mais forte? Mude `G`. Quer trilhas mais longas? Mude `TRAIL_LENGTH`. Quer mais cenários no futuro? Adicione cores em `COLORS`.

Organizado em blocos:

- **Janela:** `WIDTH`, `HEIGHT`, `FPS`, `BG_COLOR`.
- **Física:** `G`, `MIN_DIST` (distância mínima — evita força infinita), `MAX_SPEED` (clamp de velocidade), `DT_CAP` (limite do passo de tempo).
- **Visual:** `TRAIL_LENGTH`, `CIRCLE_SIDES`, `RADIUS_SCALE`, `RADIUS_MIN`.
- **HUD:** cores, espaçamento de linha, número máximo de planetas listados.
- **Orbital:** parâmetros do clique-pra-criar-planeta.
- **Tempo / vetores de força:** parâmetros das features 1 e 4.
- **Paleta de cores** dos planetas novos.

### 5.2. `body.py` — o que é um planeta

Uma classe `Planet` com seis atributos:

```python
self.pos     # numpy.array([x, y]) em pixels
self.vel     # numpy.array([vx, vy]) em pixels/segundo
self.mass    # massa, determina força gravitacional
self.color   # tupla (R, G, B) com componentes em [0, 1]
self.pinned  # se True, atrai os outros mas não se move (sol fixo)
self.trail   # deque com as últimas TRAIL_LENGTH posições
```

**Por que numpy?** Porque permite escrever `delta = b.pos - a.pos` em vez de calcular `dx`, `dy` separadamente. O código fica mais curto e ainda fica mais rápido em laços com muitos corpos.

**Por que `deque(maxlen=N)`?** Porque ele descarta o ponto mais antigo automaticamente em **O(1)**. Uma `list.pop(0)` faria isso em **O(n)** — irrelevante com 150 pontos, mas o hábito vale.

Métodos / propriedades:

- `update_trail()` — anexa a posição atual à trilha. Usa `pos.copy()` para não guardar uma referência viva (que mudaria junto com o corpo).
- `radius()` — raio visual: `mass ** RADIUS_SCALE` com piso `RADIUS_MIN`. Sub-linear em massa para que sóis enormes não cubram a tela inteira.
- `speed` (property) — módulo do vetor velocidade. Usado pelo HUD e pelo `physics.orbital_info`.
- `_validate_color` — valida que a cor é uma tripla com cada componente em `[0, 1]`. Evita o erro silencioso de passar `(255, 0, 0)` em vez de `(1.0, 0, 0)`.
- `__repr__` — útil quando um teste falha e o pytest mostra os planetas envolvidos.

### 5.3. `physics.py` — gravidade, integração e colisão

Núcleo da simulação. Quatro funções públicas, cada uma com uma responsabilidade.

#### `compute_accelerations(bodies)` — função pura

Recebe a lista de corpos e devolve uma lista de vetores aceleração. **Não modifica os corpos.** Por que isso importa?

1. Permite reutilizar o cálculo na visualização das setas de força (Feature 4).
2. Permite testar a física sem precisar simular um passo inteiro.

Para cada par `(i, j)` com `i < j`:

```python
delta = b.pos - a.pos                           # vetor A → B
dist = max(np.linalg.norm(delta), MIN_DIST)     # módulo, com piso anti-singularidade
direction = delta / dist                        # vetor unitário
force_magnitude = G * a.mass * b.mass / dist**2 # F = G·m₁·m₂/r²
force = direction * force_magnitude
accelerations[i] += force / a.mass              # F = m·a → a = F/m
accelerations[j] -= force / b.mass              # 3ª Lei: oposta e igual
```

Note que percorremos só **pares únicos** (`j > i`) — calcular o mesmo par duas vezes seria desperdício. E a 3ª Lei vira aquele `+=` num corpo e `-=` no outro.

#### `step(bodies, dt)` — só integração

Aplica as acelerações para atualizar velocidade e posição:

```python
body.vel += a * dt
speed = np.linalg.norm(body.vel)
if speed > MAX_SPEED:
    body.vel = body.vel / speed * MAX_SPEED   # clamp
body.pos += body.vel * dt
body.update_trail()
```

O **clamp de velocidade** é uma proteção contra "ejeções" — quando dois corpos passam muito perto, a aceleração instantânea pode disparar a velocidade para valores absurdos. Em vez de deixar o planeta sumir da tela em uma fração de segundo, limitamos a `MAX_SPEED`.

Corpos com `pinned=True` (o sol fixo) **não** têm posição/velocidade atualizadas, mas atualizam a trilha do mesmo jeito.

#### `check_collisions(bodies)` — fusão por contato

Dois corpos colidem quando a distância entre eles é menor que a soma dos seus raios visuais. Três casos:

1. **Sol absorve planeta** (`a.pinned`): o planeta some, sol não muda.
2. **Planeta absorvido pelo sol** (`b.pinned`): mesmo que (1), apenas com índices trocados.
3. **Dois planetas comuns:** **fusão com conservação de momento linear**:

   $$\vec{p}_{\text{total}} = m_A \vec{v}_A + m_B \vec{v}_B$$

   ```python
   total_mass = a.mass + b.mass
   a.pos = (a.pos * a.mass + b.pos * b.mass) / total_mass  # centro de massa
   a.vel = (a.vel * a.mass + b.vel * b.mass) / total_mass  # v = p/m
   a.mass = total_mass
   ```

   O corpo `b` é descartado.

Devolve uma **nova lista** sem os corpos removidos. A função usa um `set` `to_remove` e um `for ... continue` para pular pares que envolvem corpos já marcados — assim, três corpos colidindo no mesmo frame fundem dois a dois sem inconsistência.

#### `update(bodies, dt)` — o que main.py chama

```python
def update(bodies, dt):
    step(bodies, dt)
    return check_collisions(bodies)
```

Uma linha cada. Compor é mais barato do que misturar.

#### `orbital_info(planet, anchor)` — telemetria orbital (Feature 2)

Devolve um dicionário com:

```python
{
    "dist":   distância atual ao âncora,
    "speed":  velocidade escalar do planeta,
    "v_esc":  velocidade de escape nessa distância,
    "bound":  True se a órbita é fechada,
    "energy": energia mecânica específica  ½v² - GM/r
}
```

Energia mecânica específica é o critério "limpo" para saber se uma órbita é ligada:

- `energy < 0` → órbita fechada (elíptica/circular)
- `energy = 0` → parábola, no limite
- `energy > 0` → hipérbole, escape

É o mesmo invariante das equações de Kepler — e fica visível no HUD em tempo real.

### 5.4. `scenarios.py` — cenários iniciais e fábrica de planetas

Três cenários e uma fábrica. Cada cenário devolve uma `list[Planet]` pronta para entrar no loop.

#### `orbital_velocity(anchor_mass, distance)`

Wrapper para `√(G·M/r)`. Usado por todo cenário e pela fábrica do clique.

#### `create_solar_system()` (tecla 1)

Sol fixo (`pinned=True`) no centro + dois planetas em órbita circular. As velocidades são calculadas com `orbital_velocity` para que as órbitas iniciem **exatamente circulares**.

#### `create_binary_stars()` (tecla 2)

Duas estrelas iguais orbitando o centro de massa comum, mais um planeta circumbinário em órbita externa. Demonstra que objetos podem orbitar um *par* de corpos.

#### `create_moon_system()` (tecla 3)

Sol + planeta + lua. A lua tem velocidade `v_planeta + v_orbital_local` — assim ela orbita o planeta enquanto o conjunto orbita o sol. Demonstra a composição de movimentos.

#### `add_orbital_planet(bodies, mouse_x, mouse_y)` — o clique do mouse

A peça que faz a UX ser intuitiva. Em vez de criar um planeta com velocidade aleatória (que sempre cairia no sol), calculamos:

1. **Âncora:** o corpo mais massivo (`max(bodies, key=lambda b: b.mass)`).
2. **Vetor radial:** do âncora ao clique. Distância com piso `ORBIT_MIN_DIST` para evitar criar planetas em cima do sol.
3. **Velocidade orbital ideal:** `v = √(G·M/r)`.
4. **Direção tangencial:** vetor perpendicular ao raio. Se o raio aponta em `(dx, dy)`, a tangente é `(-dy, dx)/|r|` — a rotação de 90°.
5. **Variação aleatória de ±30%:** dá órbitas elípticas variadas em vez de só círculos perfeitos.

```python
tx = -dy / dist
ty = +dx / dist
fator = random.uniform(0.7, 1.3)
bodies.append(Planet(
    mouse_x, mouse_y,
    vx=tx * v_orb * fator,
    vy=ty * v_orb * fator,
    mass=random.uniform(PLANET_MASS_MIN, PLANET_MASS_MAX),
    color=random.choice(COLORS),
))
```

### 5.5. `renderer.py` — primitivas de desenho

Camada gráfica pura. **Não conhece o estado do jogo** — só desenha o que recebe.

- `clear_screen()` — `glClear(GL_COLOR_BUFFER_BIT)`.
- `draw_circle(x, y, r, color, filled)` — aproxima um círculo com `CIRCLE_SIDES = 64` lados. `GL_TRIANGLE_FAN` para preencher, `GL_LINE_LOOP` para contorno.
- `draw_trail(trail, color)` — `GL_LINE_STRIP` com `glColor4f(r, g, b, alpha)` onde `alpha = i / n`. O ponto mais antigo é totalmente transparente, o mais recente é opaco — efeito de cauda de cometa.
- `draw_text(x, y, text, color)` — texto bitmap GLUT (`GLUT_BITMAP_9_BY_15`).
- `draw_arrow(x1, y1, x2, y2, color)` — segmento principal + dois segmentos curtos formando a ponta da seta. Calcula a ponta com rotação trigonométrica de ±150° em torno da direção do vetor.
- `draw_force_vectors(bodies, accelerations)` — para cada corpo não-pinned, desenha uma seta proporcional à sua aceleração. Pula vetores muito pequenos (`abs < 0.5`) para não poluir a tela.
- `render(bodies)` — função principal: limpa → desenha trilhas → desenha planetas. **Não desenha HUD nem força** — `main.py` decide a ordem dessas camadas.

**Por que GL_BLEND fica habilitado o tempo todo?** Porque alternar `glEnable`/`glDisable` por frame custa chamadas de driver. Com `glColor3f` (alpha=1) o blend é inativo nos planetas sólidos; só age nas trilhas com `glColor4f`.

### 5.6. `hud.py` — interface de informações

Esta camada **conhece** o estado do jogo (planetas, pausa, missão, escala de tempo). Usa apenas `renderer.draw_text` como primitiva.

A função pública é `draw(bodies, height, paused, time_scale_index, show_forces, mission)`. Ela renderiza:

1. **Estado:** "RODANDO" ou "PAUSADO".
2. **Velocidade do tempo:** "Tempo: 1.00x".
3. **Contagem de corpos** + estado dos vetores de força.
4. **Lista dos primeiros `HUD_MAX_PLANETS` corpos** com:
   - Massa e velocidade.
   - **Telemetria orbital** (Feature 2): distância ao âncora + tag `[OK]` (órbita ligada) ou `[ESC]` (escape). Calculada via `physics.orbital_info`.
5. **Indicador de overflow:** "+N outros" se houver mais corpos.
6. **Missão ativa:** texto laranja se em andamento, verde se completa.
7. **Controles fixos no rodapé:** sempre visíveis, independentes do número de planetas.

A cor de cada linha é a cor do próprio planeta — assim o aluno consegue mapear visualmente "essa linha vermelha é aquele ponto vermelho na tela".

### 5.7. `missions.py` — modo missão

Transforma exploração livre em aprendizado guiado.

#### Classe `Mission`

```python
class Mission:
    description: str
    check_fn:    callable(bodies) -> bool
    completed:   bool
    
    def update(self, bodies):
        if not self.completed and self.check_fn(bodies):
            self.completed = True
    
    def reset(self): ...
```

Uma vez completa, fica completa. Dá feedback positivo persistente.

#### Predicados auxiliares

- `_orbiting_bodies(bodies)` — todos os corpos não-pinned.
- `_anchor(bodies)` — corpo mais massivo (referência da órbita).
- `_has_bound_orbit(bodies, min_dist, max_dist)` — existe pelo menos um corpo em órbita ligada na faixa de distância?
- `_has_escape(bodies)` — algum corpo atingiu velocidade de escape?

#### Catálogo de missões

```python
MISSIONS = [
    "Coloque um planeta em órbita ligada a menos de 200px do sol",
    "Coloque um planeta em órbita ligada além de 300px do sol",
    "Faça um corpo escapar do sistema (atingir velocidade de escape)",
    "Mantenha 5 corpos simultaneamente em órbita",
]
```

Cada missão é uma `lambda bodies: <predicado>`. Tecla `M` cicla entre elas via `missions.cycle(index)`.

### 5.8. `main.py` — o loop principal

Toda a orquestração vive aqui — e nada além disso. O arquivo agora tem ~120 linhas (antes eram 205) porque a lógica de criação saiu para `scenarios.py` e o HUD saiu para `hud.py`.

#### `setup_opengl()`

Configura OpenGL para 2D em coordenadas de pixel:

```python
glOrtho(0, WIDTH, 0, HEIGHT, -1, 1)   # (0,0) = canto inferior esquerdo
glClearColor(*BG_COLOR)               # azul-marinho do fundo
glEnable(GL_BLEND)                    # uma vez só
glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
```

#### Estado da sessão

```python
bodies            = scenarios.create_solar_system()
current_scenario  = scenarios.create_solar_system   # para R reiniciar
paused            = False
time_scale_index  = TIME_SCALE_DEFAULT              # 1.0x
show_forces       = False
mission_index     = 0
mission           = missions.get(mission_index)
```

#### Cada frame

```python
dt     = min(clock.tick(FPS) / 1000.0, DT_CAP)
dt_sim = dt * TIME_SCALES[time_scale_index]   # tempo "do simulador"
```

Note a separação:
- `dt` real do clock controla o frame rate.
- `dt_sim` é o dt entregue à física, multiplicado pela escala de tempo.

Resultado: se você apertar `+` para ir a 4×, a simulação acelera, mas a UI (cliques, HUD) continua suave.

#### Despacho de eventos

`pygame.event.get()` em um loop com `if/elif`. Cada tecla mapeia para uma ação simples — sem máquina de estados, sem callbacks aninhados.

Para os cenários (1/2/3) usamos um dicionário:

```python
SCENARIO_BUILDERS = {
    K_1: scenarios.create_solar_system,
    K_2: scenarios.create_binary_stars,
    K_3: scenarios.create_moon_system,
}

if event.key in SCENARIO_BUILDERS:
    current_scenario = SCENARIO_BUILDERS[event.key]
    bodies = current_scenario()
    mission.reset()
```

#### Conversão de coordenadas do mouse

Pygame: Y cresce **para baixo**. OpenGL: Y cresce **para cima**. Cada clique:

```python
mx, my = event.pos
scenarios.add_orbital_planet(bodies, mx, HEIGHT - my)
```

#### Ordem do render

```python
renderer.render(bodies)                       # 1. fundo + trilhas + planetas
if show_forces:
    renderer.draw_force_vectors(bodies, ...)  # 2. setas por cima
hud.draw(bodies, HEIGHT, paused, ...)         # 3. HUD por cima de tudo
pygame.display.flip()                         # 4. swap buffers
```

---

## 6. As 5 features educativas

| # | Feature                  | Tecla    | Onde mora                                              |
|---|--------------------------|----------|--------------------------------------------------------|
| 1 | Velocidade do tempo      | `+` `−`  | `config.TIME_SCALES`, `main.dt_sim`                    |
| 2 | Telemetria orbital       | sempre   | `physics.orbital_info`, `hud.draw`                     |
| 3 | Cenários pré-definidos   | `1` `2` `3` | `scenarios.create_*`, `main.SCENARIO_BUILDERS`      |
| 4 | Vetores de força         | `V`      | `renderer.draw_force_vectors`, `physics.compute_accelerations` |
| 5 | Modo missão              | `M`      | `missions.py`, `hud.draw`                              |

**Por que cada uma é educativa?**

1. **Velocidade do tempo:** demonstra que as leis físicas são independentes da escala temporal. A órbita em 4× tem a mesma forma que em 1×.
2. **Telemetria orbital:** as Leis de Kepler aparecem em tempo real — a velocidade aumenta no periélio, diminui no afélio, e a tag `[ESC]` aparece exatamente quando `½v² > GM/r`.
3. **Cenários pré-definidos:** comparar comportamentos diferentes lado a lado (sistema único × binário × hierárquico) sem precisar reconfigurar tudo na mão.
4. **Vetores de força:** torna visível o que normalmente é invisível. O aluno *vê* a força aumentar quando o planeta se aproxima do sol.
5. **Modo missão:** transforma exploração livre em desafio com feedback imediato — "consegui!" tem peso pedagógico.

---

## 7. Testes

23 testes em `tests/`, rodáveis sem abrir janela:

```
tests/
├── conftest.py          # adiciona o root ao sys.path
├── test_body.py         # 6 testes  - speed, repr, radius, color, trail
├── test_physics.py      # 6 testes  - pinning, atração, órbita estável,
│                        #             clamp de velocidade, MIN_DIST,
│                        #             orbital_info bound vs unbound
├── test_collision.py    # 4 testes  - sem colisão, fusão de pares,
│                        #             absorção pelo sol, conservação
│                        #             de momento
└── test_scenarios.py    # 7 testes  - cenários básicos, missões, ciclo
```

Comando: `python -m pytest tests -q`.

Por que isso é importante? Porque **a física é testável sem PyOpenGL e sem Pygame**. Quando os testes passam, sei que a fusão por colisão preserva o momento; sei que a órbita não diverge em 5 segundos de simulação; sei que o `bound` é coerente com a velocidade de escape. Esses não são acidentes — são contratos.

---

## 8. Decisões de projeto

**Por que separar `physics.compute_accelerations` de `physics.step`?**
Porque o desenho de vetores de força (Feature 4) precisa das acelerações sem avançar o tempo. Antes da refatoração, a única forma de obter as acelerações era integrar — agora elas são um valor publicamente acessível.

**Por que `pinned=True` em vez de `mass=infinity`?**
Massa infinita quebra os cálculos numéricos (divisões, inicializações). `pinned` é uma flag explícita e barata: o corpo *participa* da gravidade que sente os outros, mas seu movimento é simplesmente pulado na hora de aplicar `dt`.

**Por que Euler em vez de Runge-Kutta 4?**
Porque o foco é didático e o Euler semi-implícito é estável o suficiente para órbitas em escala visível. O custo de RK4 (4× as chamadas de aceleração) não compensa quando `MAX_SPEED` e `MIN_DIST` já dão estabilidade prática.

**Por que `deque` para a trilha?**
Porque queremos um buffer circular com complexidade O(1) tanto no `append` quanto no descarte do antigo. `list.pop(0)` seria O(n) — irrelevante com 150 pontos, mas é o tipo de hábito que evita bugs em projetos maiores.

**Por que `numpy.array` para `pos` e `vel`?**
Porque permite escrever `body.vel += a * dt` em vez de calcular cada componente. Mais legível, mais fácil de generalizar para 3D no futuro, e — bônus — mais rápido na soma vetorial.

**Por que cada cenário é uma função em vez de uma classe?**
Porque um cenário é um **valor inicial**, não um comportamento contínuo. Função pura entra, lista sai. Não precisa de estado.

**Por que `config.py` em vez de constantes espalhadas?**
Antes da refatoração, `G` estava em `physics.py`, `WIDTH/HEIGHT` em `main.py`, `TRAIL_LENGTH` em `body.py`, `MAX_HUD_PLANETS` em `renderer.py`. Mexer no balanceamento exigia abrir 4 arquivos. Agora é 1.

---

> Projeto desenvolvido para a disciplina de **Computação Gráfica**.
> Simulador de órbitas com PyOpenGL — combinação de física newtoniana, integração numérica e visualização em tempo real.
