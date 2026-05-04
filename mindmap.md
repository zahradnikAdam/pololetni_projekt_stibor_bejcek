## OOP mindmap – Pololetní projekt (PyGame)

### 1) Vstup aplikace

- **`main.py`**
  - vytváří `Game()`
  - spouští `Game.run()`
  - drží minimum logiky (single responsibility: jen start programu)

---

### 2) Hlavní orchestrátor

- **`game/game.py` → `class Game`**
  - **role**
    - koordinační objekt; propojuje gameplay, UI, level flow, spawn, kolize
    - není herní entita, ale aplikační controller
  - **vlastní stav / kompozice**
    - `Player`
    - `LevelManager`
    - `ScoreTracker`
    - kolekce runtime objektů: `enemies`, `walls`, `player_projectiles`, `enemy_projectiles`, `super_projectiles`
    - pickupy: `heart_rect`, `shield_rect`, `power_rect` + timery
    - přechody levelů + end-state (`level_transition_timer`, `level_cleared_display`, `game_won`)
  - **hlavní metody**
    - `_build_border_walls()` → okraje mapy
    - `_generate_level_walls(level_no, blocked_rects)` → procedural platform layout s průchodem
    - `_place_on_platform(rect, platforms)` → přicvaknutí rectu na platformu
    - `_apply_difficulty(enemies_list, difficulty, level_manager)` → scaling nepřátel
    - `_has_clear_path_between(a_rect, b_rect, walls)` → line-of-sight kontrola (melee nesmí přes zeď)
    - `_show_end_screen(screen, clock, won)` → finální UI smyčka
    - `run()` → game loop: input → update → kolize/damage → draw → level transition
  - **combat flow**
    - hráč: melee/ranged (`F`), super (`V`)
    - enemy: melee + ranged + special rat burst
    - super hit se počítá do damage, ale **ne** do skóre
  - **score flow**
    - při zásahu melee/ranged hráče volá `score_tracker.register_hit()`
    - v HUD renderuje `Score` a `Hits`

---

### 3) Hráč a hráčské projektily

- **`player/player.py`**
  - **`class Player`**
    - **stav**
      - pozice/fyzika: `rect`, `speed`, `vel_y`, `gravity`, `on_ground`
      - život: `hp`, `max_hp`, `lives`, `spawn_pos`
      - boj: `attack_cooldown`, `attack_damage`, `super_cooldown`
      - obrana: `hit_invuln`
      - mobilita: `jump_buffer`, `coyote_timer`, `facing`
      - **double jump**: `max_air_jumps`, `air_jumps_left`
    - **chování**
      - `handle_input()` → horizontální input + facing
      - `jump()` → vloží jump do bufferu
      - `move(move_x, walls)` → fyzika + kolize + spotřeba air jumpu ve vzduchu
      - `update()` → tik cooldownů/timerů
      - `take_damage()` → hp/lives/respawn logika
      - `respawn()` a `snap_to_ground(walls)` → reset fyziky a air jumpů
      - `attack()` → polymorfní návrat:
        - `('melee', pygame.Rect)` pro Knight
        - `('ranged', PlayerProjectile)` pro Mage/Wizard
      - `super_attack()` → `HomingSuperProjectile`
      - `draw(surface)` → sprite + fallback + invuln blink + směrová čára
  - **`class PlayerProjectile`**
    - drží vlastní `rect`, `vel`, `damage`, `ttl`
    - `update(walls)` vrací alive/dead
    - `draw(surface)` render
  - **`class HomingSuperProjectile`**
    - navádění na cíl (priorita Bat, jinak nejbližší enemy)
    - `update(enemies, walls)` vrací `(alive, hit_enemy_or_None)`
    - `draw(surface)` render

---

### 4) Nepřátelé a enemy projektily

- **`game/enemy.py`**
  - **`class Enemy` (base)**
    - společný stav: HP, pohyb, cooldowny, AI parametry, útok
    - společné helpery: `_move_platformer`, `_jump`, `_has_ground_ahead`, `_has_reachable_platform_above`
    - public API: `update(player, walls)`, `try_attack(player)`, `draw(surface)`
  - **dědičnost (`Enemy` potomci)**
    - `Slime` → melee, lehký
    - `Bat` → přepisuje `update()` (létání)
    - `Skeleton` → ranged
    - `Rat` → melee + `try_special_attack()` (burst 3 střel)
    - `Dragon` → boss, přepíná země/létání, ranged meteor
  - **`class Projectile`**
    - enemy ranged projektil
    - `update(walls)` + `draw(surface)`

---

### 5) Správa levelů

- **`game/level.py` → `class LevelManager`**
  - drží konfiguraci levelů (`self.levels`) a index (`self.current`)
  - `load_current()` vytváří konkrétní instance enemy tříd (factory-like přístup)
  - `advance()` posouvá level
  - `has_next()` a `get_level_number()` poskytují stav do UI/game flow

---

### 6) Skóre (nová samostatná třída)

- **`game/score.py` → `class ScoreTracker`**
  - **role**
    - zapouzdřuje pravidla bodování za zásahy enemy
  - **stav**
    - `score`, `hits`, `points_per_hit`
  - **API**
    - `register_hit()` → přidá hit + body
    - `get_score()`
    - `get_hits()`
  - **poznámka**
    - super útok (`HomingSuperProjectile`) se do skóre nepřičítá

---

### 7) Menu/UI komponenty

- **`menu/menu.py`**
  - **`class MainMenu`**
    - drží stav výběru skinu + obtížnosti
    - metody: `run()`, `_handle_events()`, `_handle_key()`, `_handle_click()`, `_draw()`
    - vrací tuple `(skin, difficulty)`
    - layout obsahuje:
      - title + subtitle
      - výběr skinu (Knight/Wizard)
      - tlačítka obtížnosti (Easy/Normal/Hard)
      - `Start Game`
      - hint text pod panelem (aby se nepřekrýval s tlačítky)
    - text `Obtiznost (1/2/3):` byl odstraněn (zůstávají jen tlačítka)
  - **`class PauseMenu`**
    - vrací `resume` / `quit`
    - obsahuje `_settings_loop()` s ovládáním

---

### 8) Asset service + singleton

- **`assets.py` → `class Assets`**
  - zapouzdření načítání obrázků + cache
  - mapování názvů souborů na logické klíče (`player_knight`, `slime`, `background_1`, ...)
  - API: `get(name)` a `get_scaled(name, size)`
- **singleton**
  - `ASSETS = Assets()`
  - sdílená instance napříč `Game`, `Player`, `Enemy`, `MainMenu`

---

### 9) OOP principy v projektu (shrnutí)

- **dědičnost**
  - `Enemy` → `Slime`, `Bat`, `Skeleton`, `Rat`, `Dragon`
- **polymorfismus**
  - jednotné volání `update()/draw()/try_attack()` přes různé enemy třídy
  - jednotný kontrakt projektilů (`update/draw`) s odlišnou implementací
- **kompozice**
  - `Game` skládá herní systém z objektů (`Player`, `LevelManager`, `ScoreTracker`, seznamy projektilů/enemy)
- **zapouzdření**
  - `Assets` skrývá práci se soubory obrázků
  - `ScoreTracker` skrývá pravidla bodování
  - `Player` skrývá interní fyziku a jump state

---

### 10) Runtime datové toky (rychlá mapa)

- **input**
  - klávesy/mouse → `MainMenu` nebo `Game.run()`
- **update**
  - `Player.update()` + `Enemy.update()` + projektily `update()`
- **kolize**
  - rect-vs-rect: hráč/enemy/projektil/walls/pickupy
  - line-of-sight check u melee enemy proti hráči
- **score**
  - běžné hity hráče → `ScoreTracker.register_hit()`
  - super hity → damage ano, score ne
- **render**
  - background → walls → enemies/projectiles/pickupy → player → HUD
