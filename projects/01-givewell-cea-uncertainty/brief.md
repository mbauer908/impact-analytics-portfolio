# Evaluator note: uncertainty in an AMF-style LLIN CEA

**Status:** draft — results below use *illustrative* parameters until the GiveWell spreadsheet is coded.

## Decision

_Replace this paragraph on Day 2._ One sentence on whether, under stated distributions, cost per death averted stays below a working bar most of the time, and which two assumptions would flip that.

## Question

GiveWell’s published CEAs are point estimates. Funding decisions are bets under uncertainty. Which inputs in a simplified LLIN model drive the spread of cost per death averted?

## Method

- Recode the causal chain: cost → nets → coverage-time → deaths averted, with a residual adjustment for funging/leverage.
- Independent draws (see `parameters.yaml`); 20,000 Monte Carlo samples.
- Rank-correlation tornado on inputs vs log(cost per death averted).

Not in this version: full replication of every GiveWell adjustment, correlations between parameters, or value-of-information on new RCTs.

## Results

_Fill from the notebook._

## What would change my mind

- Recalibration that moves the median by >2× after using official cells.
- Evidence that baseline malaria mortality and net efficacy are strongly negatively correlated (narrows the tail).

## Limitations

Illustrative parameters; independent draws; simplified chain. This is a template for how an evaluator should *talk* about uncertainty, not a substitute for GiveWell’s model.
