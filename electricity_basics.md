# Power Sector Basics

## What is Electricity?

Electricity is simply the movement of tiny particles called **electrons** through a wire. Think of it like water flowing through a pipe — the wire is the pipe, and electricity is the water.

**How it reaches you:** Electricity is made at power plants, sent over long distances at very high voltage (like using high pressure to push water far), and then the voltage is reduced before it reaches your home so it's safe to use.

Two types of electricity you must know:

- **AC (Alternating Current):** The current changes direction back and forth very fast — 50 times every second in India (called 50 Hz). This is what comes out of your wall socket. **Why AC?** Because its voltage can be easily increased or decreased using a simple device called a transformer, which makes long-distance transmission cheap and efficient.

- **DC (Direct Current):** The current flows steadily in one direction only, like water flowing down a river. Batteries, solar panels, and electronics (phones, laptops) all work on DC.

- **AC–DC Conversion:** Since the grid runs on AC but solar panels and batteries work on DC, we constantly convert between the two. An **inverter** converts DC to AC (e.g., solar panel output fed into the grid), and a **rectifier/charger** converts AC to DC (e.g., charging your phone or an EV battery). **Why does this matter for modelling?** Every conversion loses a small amount of energy as heat (typically 2–5%). So when building a power or financial model, you must apply these conversion losses — for example, a solar plant's DC capacity (panel rating) is always higher than its AC capacity (what it can actually deliver to the grid). This is why solar projects quote a **DC:AC ratio** (typically 1.2–1.4), and revenue is modelled on AC output, not DC panel capacity.
