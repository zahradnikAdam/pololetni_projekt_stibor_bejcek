"""`Assets` – služba (service object) pro obrázky.

OOP pohled:
- `Assets` zapouzdřuje načítání a cache obrázků (ostatní části hry neřeší cesty).
- Ostatní objekty používají jen rozhraní `get()` / `get_scaled()`.
- `ASSETS` je singleton instance sdílená napříč moduly.
"""

import os
import pygame
import re


class Assets:
    def __init__(self):
        # prefer a top-level `img/` folder in this project if present (user-provided art)
        repo_root = os.path.dirname(__file__)  # složka, kde leží `assets.py`
        candidates = [
            os.path.join(repo_root, 'img'),  # `.../pololetni_projekt_stibor_bejcek/img/`
            os.path.join(os.path.dirname(repo_root), 'img'),  # případně `.../img/`
        ]
        img_folder = next((p for p in candidates if os.path.isdir(p)), None)
        self.images = {}

        # If user has an `img/` directory, use only files from there (no fallbacks).
        # This ensures we don't use any generated placeholders when user art exists.
        if img_folder and os.path.isdir(img_folder):
            for fname in os.listdir(img_folder):
                lower = fname.lower()
                if not (lower.endswith('.png') or lower.endswith('.jpg') or lower.endswith('.jpeg') or lower.endswith('.webp')):
                    continue
                clean = lower
                clean = os.path.splitext(clean)[0]
                for suf in ('-removebg-preview', '_removebg', '-removebg', '-bg', '_bg', '-transparent'):
                    if clean.endswith(suf):
                        clean = clean[: -len(suf)]
                cleaned_key = ''.join(c if c.isalnum() else '_' for c in clean).strip('_')

                path = os.path.join(img_folder, fname)
                try:
                    # Pozor: `convert_alpha()` vyžaduje inicializované video (display mode).
                    # Tento soubor se načítá už při importu, takže display často ještě neběží.
                    # Proto nejdřív načteme obrázek a `convert_alpha()` uděláme jen když existuje display.
                    surf = pygame.image.load(path)
                    if pygame.display.get_surface():
                        surf = surf.convert_alpha()
                except Exception:
                    surf = None

                if not surf:
                    continue

                # map player skins
                if 'knight' in cleaned_key:
                    self.images['player_knight'] = surf
                if 'mage' in cleaned_key or 'wizard' in cleaned_key:
                    self.images['player_mage'] = surf

                # map common enemy keys
                for enemy_key in ('slime', 'bat', 'skeleton', 'rat', 'dragon', 'boss'):
                    if enemy_key in cleaned_key:
                        self.images[enemy_key] = surf

                # pickups / UI
                if 'heart' in cleaned_key or 'srdce' in cleaned_key:
                    self.images['heart'] = surf
                if 'shield' in cleaned_key or 'stit' in cleaned_key:
                    self.images['shield'] = surf
                if 'power' in cleaned_key or 'boost' in cleaned_key or 'skull' in cleaned_key:
                    self.images['power'] = surf

                # backgrounds (podle levelu)
                # podporuje názvy typu: background_1.png, background-level2.png, level3_background.png, bg4.png ...
                if any(k in cleaned_key for k in ('background', 'bg', 'level', 'lvl', 'pozadi')):
                    m = re.search(r'(\d+)', cleaned_key)
                    if m:
                        n = m.group(1)
                        if 'background' in cleaned_key or 'bg' in cleaned_key or 'pozadi' in cleaned_key or 'lvl' in cleaned_key:
                            self.images[f'background_{n}'] = surf
                        if 'level' in cleaned_key:
                            self.images[f'level_{n}'] = surf
                    if 'background' in cleaned_key or 'pozadi' in cleaned_key:
                        # default fallback background
                        self.images['background'] = surf

                # Přímé mapování pro názvy typu `level1.webp` / `level2.jpg` apod.
                m2 = re.fullmatch(r'level_?(\d+)', cleaned_key)
                if m2:
                    n = m2.group(1)
                    self.images[f'background_{n}'] = surf

                # also expose the cleaned filename as a key
                if cleaned_key:
                    self.images[cleaned_key] = surf

            # aliases
            if 'dragon' not in self.images:
                self.images['dragon'] = self.images.get('boss')
            if 'player_wizard' not in self.images:
                self.images['player_wizard'] = self.images.get('player_mage')
            return

        # No user img/ folder -> fallback to built-in assets directory (if present)
        self.base = os.path.join(os.path.dirname(__file__), 'assets')
        # map logical names to filenames
        self.map = {
            'player_knight': 'player_knight.png',
            'player_mage': 'player_mage.png',
            'slime': 'slime.png',
            'bat': 'bat.png',
            'skeleton': 'skeleton.png',
            'rat': 'rat.png',
            'boss': 'boss.png',
            'background': 'background.png',
            'wall': 'wall.png',
            'heart': 'heart.png',
            'shield': 'shield.png',
            'power': 'power.png',
        }
        for key, fname in self.map.items():
            path = os.path.join(self.base, fname)
            try:
                if os.path.exists(path):
                    surf = pygame.image.load(path)
                    if pygame.display.get_surface():
                        surf = surf.convert_alpha()
                    self.images[key] = surf
                else:
                    self.images[key] = None
            except Exception:
                self.images[key] = None

    def get(self, name):
        # Jednoduché rozhraní: key -> surface.
        return self.images.get(name)

    def get_scaled(self, name, size):
        # Utility metoda: key -> surface přepočítaný na velikost pro UI/hitbox.
        surf = self.get(name)
        if surf:
            # Dodatečná konverze až ve chvíli, kdy už je inicializovaný display.
            # (Pomůže, pokud se obrázky načetly při importu bez `convert_alpha()`).
            if pygame.display.get_surface():
                try:
                    surf = surf.convert_alpha()
                except Exception:
                    pass
            try:
                return pygame.transform.smoothscale(surf, (int(size[0]), int(size[1])))
            except Exception:
                return pygame.transform.scale(surf, (int(size[0]), int(size[1])))
        return None


# singleton instance
ASSETS = Assets()
