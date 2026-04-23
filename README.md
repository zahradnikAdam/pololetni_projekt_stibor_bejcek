# Dungeon Game (PyGame)

2D akční hra v Pythonu postavená nad `pygame` s více levely, nepřáteli, bossem, náhodným rozvržením zdí a základní RPG logikou (HP, životy, melee/ranged útoky).

## Požadavky
- Python 3.8+
- `pygame`

## Instalace

```powershell
python -m pip install -r requirements.txt
```

## Spuštění

```powershell
python .\main.py
```

## Ovládání
- Pohyb: `WASD` nebo šipky
- Útok: `Space` nebo `F`
- Pauza: `Esc`
- Menu: myš / `Tab` / `Enter` / `1-2-3` (obtížnost)

## OOP Struktura Projektu
- `main.py` – vstupní bod aplikace.
- `game.py` – třída `Game` (hlavní smyčka, kolize, level flow, vykreslování).
- `player.py` – třída `Player` + `PlayerProjectile`.
- `enemy.py` – základní třída `Enemy`, specializace (`Slime`, `Bat`, `Skeleton`, `Rat`, `Dragon`) a `Projectile`.
- `level.py` – `LevelManager` (obsah levelů a načítání nepřátel).
- `menu.py` – `MainMenu` a `PauseMenu` (UI jako samostatné třídy).
- `assets.py` – `Assets` loader a mapování obrázků z `img/`.

## Kvalita a Čitelnost
- Chování je rozdělené do doménových tříd (hráč, nepřítel, menu, level manager).
- Kód používá malé metody (`_handle_events`, `_draw`, `try_attack`, `move`, `update`) pro snadnější úpravy.
- UI logika je oddělena od gameplay logiky.

## Zabezpečení Dat a Stabilita
- Hra nepracuje s citlivými daty ani síťovou komunikací.
- Asset loading je ošetřen `try/except`, takže chybějící soubory hru neshodí.
- Vstupy hráče jsou omezeny na explicitně zpracované klávesy/události.

## Hratelnost
- Náhodné rozložení zdí pro každý level.
- Různé typy enemy AI (`wander` / `follow`) a ranged/melee útoky.
- Boss (`Dragon`) používá meteor projektil z `img/meteor.png`.
- Obtížnost (`Easy/Normal/Hard`) upravuje HP, rychlost i cooldowny nepřátel.

## Optimalizace
- Opakovaně používané textury (např. zeď/meteor) se připravují před render smyčkou nebo cachují.
- Kolize jsou řešené osově (X/Y), což je levnější a stabilnější než složitější fyzika.
- Projektily a efekty jsou průběžně uklízeny ze seznamů při zániku.
