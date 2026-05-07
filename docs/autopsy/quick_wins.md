# QUICK WINS - simulador_orbitas
# Top 5 mudancas com maior impacto e menor risco, implementaveis hoje

---

## QW1 -- Criar config.py [30 min, risco: zero]

Impacto: resolve 67 magic numbers de uma vez.
Qualquer ajuste de gameplay (tamanho da tela, G, trilha) para de exigir
busca em 4 arquivos diferentes.

Acao: criar config.py com as constantes listadas no remodel_proposal.
Depois substituir os valores hardcoded por referencias a config.

---

## QW2 -- Adicionar tests/test_physics.py [20 min, risco: zero]

Impacto: qualquer refatoracao futura tem seguranca automatica.
Os 5 testes ja foram escritos e validados durante o desenvolvimento.

Acao: mover os asserts do script de validacao para um arquivo pytest permanente.

```python
# tests/test_physics.py
import pytest
from body import Planet, TRAIL_LENGTH
import physics

def test_trail_nao_ultrapassa_limite():
    p = Planet(0, 0, 0, 0, 10, (1,1,1))
    for _ in range(300):
        p.update_trail()
    assert len(p.trail) == TRAIL_LENGTH

def test_sol_pinned_nao_se_move():
    sol = Planet(450, 350, 0, 0, 5000, (1,1,1), pinned=True)
    planeta = Planet(600, 350, 0, 130, 30, (0,0,1))
    bodies = [sol, planeta]
    for _ in range(120):
        bodies = physics.update(bodies, 0.016)
    assert abs(bodies[0].pos[0] - 450) < 0.001

def test_fusao_conserva_momento():
    a = Planet(100, 100,  10, 0, 50, (1,0,0))
    b = Planet(102, 100, -10, 0, 30, (0,0,1))
    resultado = physics._check_collisions([a, b])
    assert len(resultado) == 1
    assert abs(resultado[0].mass - 80) < 0.01
    assert abs(resultado[0].vel[0] - 2.5) < 0.01

def test_planeta_absorvido_pelo_sol():
    sol = Planet(100, 100, 0, 0, 5000, (1,1,0), pinned=True)
    p   = Planet(101, 100, 0, 0,   20, (0,0,1))
    resultado = physics._check_collisions([sol, p])
    assert len(resultado) == 1
    assert resultado[0].pinned
```

---

## QW3 -- Separar step() e check_collisions() em physics.py [15 min, risco: baixo]

Impacto: cada funcao tem uma responsabilidade. Facil de testar cada parte
separadamente. Abre caminho para adicionar MAX_SPEED sem baguncar a colisao.

Acao:
1. Renomear a parte da integracao numerica para step(bodies, dt)
2. Tornar _check_collisions publico: check_collisions(bodies)
3. Manter update(bodies, dt) como wrapper que chama os dois

---

## QW4 -- Adicionar MAX_SPEED em physics.py [10 min, risco: zero]

Impacto: elimina o bug de velocidade infinita quando dois corpos passam
muito proximos. A simulacao para de explodir em casos extremos.

Acao: apos calcular nova velocidade, clampar com numpy:
```python
speed = np.linalg.norm(body.vel)
if speed > MAX_SPEED:
    body.vel = body.vel / speed * MAX_SPEED
```

---

## QW5 -- Adicionar __repr__ em Planet e remover imports desnecessarios [10 min, risco: zero]

Impacto: print(planet) passa a mostrar informacao util durante debug.
Remover `from OpenGL.GLU import *` de main.py e renderer.py limpa
2 imports que nao fazem nada.

Acao em body.py:
```python
def __repr__(self):
    return (f"Planet(pos={self.pos.round(1)}, "
            f"mass={self.mass:.0f}, pinned={self.pinned})")
```

Acao em main.py: remover linha `from OpenGL.GLU import *`
Acao em renderer.py: remover linha `from OpenGL.GLU import *`

---

## ORDEM RECOMENDADA

QW2 (testes) -> QW3 (separar step) -> QW4 (MAX_SPEED) -> QW1 (config) -> QW5 (limpeza)

Razao: criar testes primeiro garante que QW3 e QW4 nao quebram nada.
