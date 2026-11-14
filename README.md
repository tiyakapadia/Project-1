# Synchronous FIFO Functional Verification (EEE 4701 — Project 1)

**Demo Walkthrough:** [Watch Project 1 Demo Video on YouTube](https://youtu.be/U6vcurAWQeE?is=HfgOoc364MhdUAMX)

## Team Members
* **Tiya Kapadia**  — Cocotb Driver & Monitor (`driver.py`, `monitor.py`), Verification Plan (`vplan.md`), Demo & Report
* **Paul Rich** — Reference Model, Scoreboard (`scoreboard.py`), Functional Coverage Model & Report
* **Jason Ralph** — Constrained-Random Stimulus (`test_crv.py`), Seeded Regression & Mutation Analysis

---

## Repository Structure

```text
project1/
├── README.md              # Project overview and demo link
├── vplan.md               # Verification plan (features, coverpoints, bins, crosses, assertions)
├── FINDINGS.md            # Mutation testing results (found/total) and survivor analysis
├── Project1_Report.pdf    # Full technical verification report
├── CONTRIBUTIONS.md       # Detailed breakdown of team responsibilities
├── tb/                    # Testbench components (driver, monitor, scoreboard)
├── crv/                   # Constrained-random stimulus, sequences, and seeded regression
└── coverage/              # PyVSC functional coverage model and coverage closure reports
