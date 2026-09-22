# Pilot Services Agreement — Spectral Health Pilot

> **Template — not legal advice.** Have an attorney review before use.

**This Pilot Services Agreement** ("Agreement") is entered into as of
**[DATE]** ("Effective Date") by and between:

- **Provider:** Nexus Research (Jeffrey Michael Gurd),
  jeffrey@nexus-research.org ("Provider"); and
- **Client:** [CLIENT LEGAL NAME], [ADDRESS] ("Client").

## 1. Services

Provider will deliver the "Spectral Health Pilot" described in
[PILOT.md](PILOT.md), consisting of:

1. **Diagnostic report (JSONL)** — spectral health analysis (eigenvalues,
   spectral gap, condition number, heat-kernel/spectral-dimension curve,
   symmetry checks) for 3–5 Client matrices from one production pipeline.
2. **One CI gate integration** — `spectral gate` wired into one Client build
   pipeline, with thresholds tuned on Client data.
3. **Findings call** — up to 60 minutes to review results and recommendations.

The pilot runs for **two (2) weeks** from the kickoff call ("Pilot Term").

## 2. Fees and payment

- **Fixed fee: USD $5,000** for the Pilot Term.
- **50% ($2,500) due on execution** of this Agreement; **50% ($2,500) due on
  delivery** of the findings report. Net 15 days.
- The full $5,000 is **credited against an annual license** if Client executes
  one within 90 days of the findings call.

## 3. Client responsibilities

Client will provide, within 3 business days of the kickoff call:

- 3–5 matrices (`.npy`, `.csv`, or via Provider's API/S3) from one pipeline;
- access needed to integrate the CI gate into one build pipeline;
- one 30-minute kickoff call and one 30-minute findings call with a
  technical decision-maker.

Delays in Client responsibilities extend the Pilot Term day-for-day.

## 4. Intellectual property

- Provider's pre-existing technology (including the open-core spectral-diag
  software, MIT-licensed at github.com/jeffgurd888/spectral-diag) remains
  Provider's property.
- The diagnostic report and gate configuration produced for Client are
  licensed to Client perpetually for internal use.
- Nothing in this Agreement grants Client rights to Provider's underlying
  engine IP beyond the MIT-licensed open core.

## 5. Confidentiality

Each party will keep the other's non-public information confidential for
2 years. Client matrices and results are Client's confidential information.
Provider will not use Client data to train models or for any other client.

## 6. Warranty and liability

Provider warrants the services will be performed professionally. EXCEPT AS
STATED, SERVICES ARE PROVIDED "AS IS." Provider's total liability under this
Agreement is capped at the fees paid. Neither party is liable for indirect,
incidental, or consequential damages.

## 7. Termination

Either party may terminate with 5 days' written notice. On termination,
Client pays for work performed through the termination date (prorated against
the fixed fee milestones met). Sections 4–6 and 8 survive.

## 8. General

- **Independent contractor.** Nothing here creates employment, partnership,
  or agency.
- **Governing law:** [STATE — e.g., New York].
- **Entire agreement.** This Agreement plus PILOT.md is the entire agreement
  for the pilot; amendments must be written and signed.

**AGREED:**

Provider: ___________________________ Date: __________
Jeffrey Michael Gurd, Nexus Research

Client: _____________________________ Date: __________
Name / Title: _______________________
