import os
import pygame


class Assets:
    def __init__(self):
        # prefer a top-level `img/` folder if present (user-provided art)
        repo_root = os.path.dirname(os.path.dirname(__file__))
        img_folder = os.path.join(repo_root, 'img')
        self.images = {}

        # If user has an `img/` directory, use only files from there (no fallbacks).
        # This ensures we don't use any generated placeholders when user art exists.
        if os.path.isdir(img_folder):
            for fname in os.listdir(img_folder):
                if not fname.lower().endswith('.png'):
                    continue
                clean = fname.lower()
                clean = os.path.splitext(clean)[0]
                for suf in ('-removebg-preview', '_removebg', '-removebg', '-bg', '_bg', '-transparent'):
                    if clean.endswith(suf):
                        clean = clean[: -len(suf)]
                cleaned_key = ''.join(c if c.isalnum() else '_' for c in clean).strip('_')

                path = os.path.join(img_folder, fname)
                try:
                    surf = pygame.image.load(path).convert_alpha()
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
        }
        for key, fname in self.map.items():
            path = os.path.join(self.base, fname)
            try:
                if os.path.exists(path):
                    surf = pygame.image.load(path).convert_alpha()
                    self.images[key] = surf
                else:
                    self.images[key] = None
            except Exception:
                self.images[key] = None

    def get(self, name):
        return self.images.get(name)

    def get_scaled(self, name, size):
        surf = self.get(name)
        if surf:
            try:
                return pygame.transform.smoothscale(surf, (int(size[0]), int(size[1])))
            except Exception:
                return pygame.transform.scale(surf, (int(size[0]), int(size[1])))
        return None


# singleton instance
ASSETS = Assets()
