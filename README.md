# Hit the Cup! – Projectile Motion Simulator

A browser version of the Hit the Cup projectile motion simulator. Students only need a web browser.

**Student link:** https://ntruncale.github.io/hit-the-cup/

- **Lab simulator**: enter the measurements from the marble-and-cup experiment, watch the flight, and get the predicted landing spot. Each run goes into a table students can copy into Excel.
- **Target game**: the cup moves each level, and students calculate the launch speed that lands the bird in the cup.
- **Choose your bird**: students pick a cardinal, owl, penguin or chick and any color. The choice is remembered on that device.
- `index.html#game` opens the Target game directly. `index.html#lab` opens the Lab simulator.

## Files

- `index.html` – the whole web app (HTML, CSS and JavaScript in one file)
- `hit_the_cup.py` – the original Python (turtle) version, which runs in IDLE or Thonny

## Changing settings

The **Teacher settings** panel on the page sets gravity (Earth, Moon or Mars) and the cup diameter.
The game levels are listed in `GAME_LEVELS` near the top of the script in `index.html`.
