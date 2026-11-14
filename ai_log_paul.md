# Check the Machine — CtM-NN


**Name: Pau Rich**
**Section:** EEE 4701
**Week:** Project 1 — <technique>
**Autonomy tier:** self-directed
**Assistant used:** <web interface, <10 2026>">
---

## 1. Task

 Develop the functional coverage model for the FIFO verification environment. List Coverpoints, bins, and crosses that could be used to verify the required FIFO behaviors.

**Prompt (verbatim):**

```text
<Given the requirements and objectives of this project, what would you condsider to be in scope (what this project claims to verify) and out of scope>
<What entries should be includued in the feature list, converage model , crosses, text matrix sections of the template>
```

---

## 2. Before

**Prediction 1 —** <Missing coverage for simultaneous read and write operations.>
*Evidence that would show it:* <Coverage report showing no bin for wr_en=1, rd_en=1>

**Prediction 2 —** <Missing crosses between FIFO occupancy and read/write enables.>
*Evidence that would show it:* <Coverage report or generated code showing the cross is absent>

**Review criteria I am checking against:**

1. <Model includes coverpoints for FIFO occupancy, read/write enables, and full/empty conditions.>
2. <The model includes meaningful crosses between FIFO occupancy and read/write operations, including simultaneous read/write conditions.>
3. <The model covers transitions into and out of full and empty states.>
4. <The model correctly identifies legal, illegal, and undefined FIFO operations according to the specification.>
4. <Coverage is sampled at the correct clock or transaction event using valid DUT signals.>
6. <The model contains identifiable bins and crosses that can be measured using simulation results and a coverage report.>

---

## 3. After

**Raw output:**

```text
<https://github.com/tiyakapadia/Project-1/blob/main/vplan.md>
```

**The number:** <8/8, 100%>

**Against each prediction:**

| # | Predicted | Observed | Verdict |
|---|-----------|----------|---------|
| 1 | Missing coverage for simultaneous read and write operations. | X1 defines operation × operand-class coverage using C1, C2, and C3.  | refuted |
| 2 | Missing crosses between FIFO occupancy and read/write enables | C4 defines operand sign combinations, and X2 crosses these combinations with ADD/SUB. | refuted |

---

## 4. Takeaway

**The class of failure (or of success): Functional coverage failure. The coverage model did not account for all required interactions between ALU operations and operand values, which could allow certain defects to remain undetected.**

**Where it connects: This connects to functional coverage and reachability. A testbench can pass all tests while still missing important corner cases if the coverage model does not include the required bins and crosses.**

**What I would change in how I framed the request: I would include the vplan.md template in the initial prompt and require the AI to explain how each generated coverpoint and cross relates to a specific ALU requirement.**

---

## Disclosure

- [X] Every prompt above is verbatim and complete.
- [X] I have marked every edit I made to the generated output.
- [X] The tool is described by class, not by product name.
- [X] Section 2 was written before the prompt was sent.
