# Drug Discovery Analyst Report: Divarasib (GDC-6036) — A Covalent KRAS G12C Inhibitor

**Paper:** "Discovery and Characterization of Divarasib (GDC-6036), a Potent Covalent Inhibitor of KRAS G12C"
**Journal:** Journal of Medicinal Chemistry (2026)
**Developer:** Genentech / Roche
**Report Date:** 2026-03-24

---

## 1. Paper Summary

### Target
**KRAS G12C** — a gain-of-function oncogenic mutation in the GTPase KRAS, present in ~13% of non-small cell lung cancers (NSCLC), ~3–5% of colorectal cancers, and other solid tumors. KRAS was historically considered "undruggable" until covalent inhibitors targeting the mutant Cys12 residue in the switch-II pocket were discovered.

### Scope
The paper describes the full medicinal chemistry optimization journey from initial hit to clinical candidate divarasib (GDC-6036, compound 10). It covers:
- Scaffold selection (quinazoline core)
- Back-pocket optimization to fill the lipophilic cavity between the alpha-2 (switch-II) and alpha-3 helices
- Two-step covalent inhibition kinetics (noncovalent Ki → covalent kinact)
- Co-crystal structures (PDB: 9PZF, 9PZY)
- In vitro potency, selectivity, and DMPK profiling
- Multi-species pharmacokinetic characterization

### Key Message
Divarasib achieves superior potency and selectivity over first-generation KRAS G12C inhibitors (sotorasib, adagrasib) primarily through optimization of **noncovalent binding affinity (Ki)**, which drives both higher potency and faster alkylation kinetics. The compound is orally bioavailable with favorable drug-like properties and has advanced into Phase III clinical trials.

---

## 2. Compound Table

| Compound | Role in Paper | Activity Value | Units | Assay/Property | Species | Notes |
|----------|--------------|----------------|-------|----------------|---------|-------|
| **1** | Early analog | — | — | — | — | Isoquinoline at quinazoline-C7 to fill back-pocket lipophilic cavity |
| **4** | Optimized analog | — | — | — | — | Aminopyridine with methyl group replacing aminoisoquinoline; reduced Ar ring count |
| **Divarasib (10)** | Clinical candidate | — | — | — | — | Highly potent, selective covalent KRAS G12C inhibitor |
| Divarasib | Physchem | 622 | g/mol | Molecular Weight | — | — |
| Divarasib | Physchem | 100 | Å² | TPSA | — | — |
| Divarasib | Physchem | 2.3 | — | LogD | — | Moderate lipophilicity |
| Divarasib | Solubility | 150 | µM | Kinetic Solubility (PBS) | — | Good aqueous solubility |
| Divarasib | Reactivity | 55 | min (t½) | Cys Reactivity T½ | — | Controlled warhead reactivity |
| Divarasib | PK | 24 | % F | Oral Bioavailability | Mouse | Low mouse F |
| Divarasib | PK | 69 | % F | Oral Bioavailability | Rat | Good rat F |
| Divarasib | PK | 75 | % F | Oral Bioavailability | Dog | Good dog F |
| Divarasib | Metabolism | — | — | LM CLint (µL/min/mg) | H/R/M/D/Cy | 19/19/130/23/190 (human/rat/mouse/dog/cyno) |

**Additional literature-sourced data:**
- Biochemical HTRF IC50: **2.9 pM** (sub-nanomolar)
- Selectivity: >18,000-fold for KRAS G12C vs. wild-type cell lines
- 5–20× more potent and up to 50× more selective than sotorasib/adagrasib in vitro

---

## 3. SAR Narrative

### 3.1 Scaffold Selection
The quinazoline core was selected from a range of aromatic and partially saturated cores as the scaffold that best filled the switch-II pocket while maintaining synthetic tractability.

### 3.2 Back-Pocket Optimization
The deepest region of the switch-II pocket (the "back-pocket"), located between the alpha-2 and alpha-3 helices, was identified as a key area for potency enhancement:

1. **Isoquinoline at C7 (compound 1):** The initial approach attached an isoquinoline moiety at quinazoline-C7 to fill the lipophilic back-pocket cavity. While this occupied the target region, the high aromatic ring count was a liability for drug-like properties.

2. **Aminopyridine replacement (compound 4):** The aminoisoquinoline was replaced with a smaller **aminopyridine bearing a methyl group**. This change:
   - Reduced aromatic ring count (improving physicochemical properties)
   - Maintained occupancy of the lipophilic cavity
   - Enforced the desired dihedral angle about the biaryl bond
   - Preserved the hydrogen bond to **Asp69** (key H-bond acceptor)

3. **Trifluoromethyl group:** In divarasib, a CF3 group on the pyridine projects into the hydrophobic back-pocket, making van der Waals contacts with Gln99, His95, Ile100, Met72, Val9, Phe78, and Tyr96.

### 3.3 Quinazoline C8-Fluorine
Addition of fluorine at C8 improved potency **5–7-fold** by:
- Restricting the torsion angle of the back-pocket substituent (introducing atropisomeric bias)
- Improving van der Waals contacts in the back-pocket

### 3.4 Piperazine Methyl Substitution
A methyl group on the piperazine spacer provided torsional control, yielding a modest potency increase.

### 3.5 Noncovalent Binding as the Key Driver
A central finding of the paper is that **improvements in noncovalent Ki drove improvements in both potency and kinetics of covalent alkylation**, consistent with a two-step kinetic model:
- Step 1: Reversible noncovalent binding (governed by Ki)
- Step 2: Irreversible covalent bond formation (governed by kinact)

This was validated using non-reactive acetamide analogs and SPR measurements. The biochemical SOS exchange assay correlated well with cellular target engagement, providing a reliable SAR readout.

### 3.6 Selectivity
Non-KRAS G12C cell lines showed no sensitivity to divarasib, confirming high mutation-specific selectivity — a critical feature for therapeutic index.

---

## 4. Post-Publication Context

### 4.1 Clinical Development Status

| Trial | Phase | Setting | Status |
|-------|-------|---------|--------|
| NCT04449874 | Phase I | Advanced solid tumors with KRAS G12C | Completed enrollment; long-term follow-up published |
| Krascendo-170 | Phase Ib/II | 1L NSCLC + pembrolizumab ± chemo | Ongoing |
| **Krascendo-1** | **Phase III** | **2L+ NSCLC vs. sotorasib/adagrasib** | **Ongoing; primary completion ~2027** |
| **Krascendo-2** | **Phase III** | **1L NSCLC + pembrolizumab vs. pembro + chemo** | **Ongoing; enrollment started late 2025** |
| Phase Ib | Phase Ib | CRC + cetuximab | Data published (Nature Medicine 2023) |

### 4.2 Key Clinical Efficacy Data

**Phase I monotherapy (NSCLC, long-term follow-up, JCO 2025):**
- Confirmed ORR: **55.6%** (95% CI: 42.5–68.1)
- Median duration of response: **18.0 months**
- Median PFS: **13.8 months** (overall); **15.3 months** (400 mg cohort)
- 48% of patients treated beyond 1 year

**Phase Ib CRC + cetuximab (Nature Medicine 2023):**
- ORR: **62.5%** in KRAS G12C+ CRC patients

### 4.3 Comparison with Approved KRAS G12C Inhibitors

| Parameter | Sotorasib | Adagrasib | **Divarasib** |
|-----------|-----------|-----------|---------------|
| ORR (NSCLC) | 28–37% | 32–43% | **~54–56%** |
| Median PFS (NSCLC) | 5.6–6.8 mo | 5.5–6.5 mo | **13.1–15.3 mo** |
| Grade ≥3 AEs | ~20% | ~45% | **~11%** |
| Approval Status | FDA approved | FDA approved | **Investigational** |

### 4.4 Safety Profile
- No dose-limiting toxicities or treatment-related deaths in Phase I (n=137)
- Most common AEs: nausea (45%), diarrhea (42%), vomiting (25%) — predominantly grade 1–2
- Grade 3 hepatotoxicity signals: ALT/AST elevations in ~3% of patients (4/137 each)
- Treatment discontinuation due to AEs: 3% (4/137)
- **No specific structural alerts** identified for divarasib's scaffold in the hepatotoxicity literature
- The acrylamide warhead has controlled reactivity (Cys t½ = 55 min), reducing off-target covalent binding risk

### 4.5 Regulatory & Commercial Outlook
- **Not yet FDA-approved** as of March 2026
- Roche projects peak sales of **CHF 1–2 billion**
- NDA filing likely **no earlier than 2027**, pending Krascendo-1 Phase III readout
- RP2D established at **400 mg QD oral**

---

## 5. Consistency Assessment

### Claims Supported by Broader Literature

| Paper Claim | External Validation | Verdict |
|-------------|-------------------|---------|
| Divarasib has greater potency than other KRAS G12C inhibitors | Phase I ORR (~55%) vs. sotorasib (~37%) and adagrasib (~43%); sub-nanomolar IC50 confirmed by multiple vendors | **Strongly supported** |
| Noncovalent binding drives potency and kinetics | Consistent with two-step covalent inhibition kinetic models established in literature; MD simulation studies (Nature Sci Reports 2025) support significant noncovalent binding component | **Supported** |
| High selectivity for KRAS G12C over wild-type | >18,000-fold selectivity confirmed; low rate of off-target clinical AEs consistent with selectivity claims | **Strongly supported** |
| Favorable oral bioavailability | Clinical activity at 400 mg QD with good PK; rat (69%) and dog (75%) F values consistent with oral drug | **Supported** |
| Rapid alkylation kinetics | Clinical data showing rapid onset of tumor response consistent with fast target engagement | **Supported** |

### Potential Caveats
1. **Mouse bioavailability is low (24%)** — the paper reports this but does not extensively discuss it. Mouse PK may not predict human PK for this compound; high liver microsome clearance in mouse (CLint = 130) likely explains this.
2. **MW of 622** is above the traditional Rule-of-5 cutoff (500), though this is common for covalent inhibitors occupying deep binding pockets.
3. **Phase I data is non-randomized** — the favorable ORR/PFS comparisons with sotorasib/adagrasib await confirmation in randomized Phase III (Krascendo-1).
4. **Resistance mechanisms** observed with first-generation agents (RAS pathway reactivation, bypass signaling) are expected to also affect divarasib. Duration of response data and resistance profiling will be critical.

---

## 6. Recommendations

### Compounds Worth Further Investigation

#### Divarasib (GDC-6036) — **Highest Priority**
- **Rationale:** Best-in-class preclinical potency and selectivity, compelling Phase I clinical data (ORR 55.6%, PFS 13.8 mo), manageable safety profile, and favorable oral dosing (400 mg QD).
- **Key questions to resolve:**
  1. Does the PFS/ORR advantage over sotorasib/adagrasib hold in randomized Phase III (Krascendo-1)?
  2. What are the dominant acquired resistance mechanisms, and how do they compare to first-generation agents?
  3. Can combination strategies (+ pembrolizumab, + cetuximab in CRC) extend benefit further?
  4. What is the overall survival benefit?

#### Combination Strategies — **High Priority**
- **Divarasib + cetuximab** in CRC showed 62.5% ORR — significantly above historical benchmarks for KRAS-mutant CRC. This combination warrants Phase III evaluation.
- **Divarasib + pembrolizumab** (Krascendo-170, Krascendo-2) is being tested in frontline NSCLC and represents the highest commercial opportunity.

#### Intermediate Analogs (Compounds 1, 4) — **Low Priority for Direct Development**
- These are important for understanding SAR but are superseded by divarasib as clinical candidates.
- The SAR lessons (back-pocket optimization, biaryl dihedral control, noncovalent Ki as potency driver) are valuable design principles for:
  - Next-generation KRAS G12C inhibitors addressing resistance
  - Inhibitors targeting other KRAS mutants (G12D, G12V, G13D)

### Strategic Recommendations
1. **Monitor Krascendo-1 Phase III results** (expected 2026–2027) — this is the pivotal readout that will determine divarasib's commercial viability.
2. **Track resistance profiling data** — understanding whether divarasib's deeper pocket engagement delays or alters resistance patterns vs. first-generation agents.
3. **Evaluate applicability of SAR principles to pan-KRAS programs** — the noncovalent Ki optimization strategy and back-pocket filling motifs may translate to non-G12C KRAS mutants.
4. **Watch for hepatotoxicity signals** in larger patient populations — while Phase I rates were low, ALT/AST elevations warrant monitoring.

---

## Sources

- [Discovery and Characterization of Divarasib (GDC-6036) — J. Med. Chem.](https://pubs.acs.org/doi/10.1021/acs.jmedchem.5c02272)
- [Single-Agent Divarasib in Solid Tumors — NEJM Phase I](https://www.nejm.org/doi/full/10.1056/NEJMoa2303810)
- [Long-Term Follow-Up Phase I — JCO 2025](https://ascopubs.org/doi/10.1200/JCO-25-00040)
- [Divarasib + Cetuximab in CRC — Nature Medicine](https://www.nature.com/articles/s41591-023-02696-8)
- [Divarasib in the Evolving Landscape of KRAS G12C Inhibitors — Targeted Oncology](https://link.springer.com/article/10.1007/s11523-024-01055-y)
- [Krascendo-2 Phase III — ASCO 2025](https://ascopubs.org/doi/10.1200/JCO.2025.43.16_suppl.TPS8656)
- [ClinicalTrials.gov NCT04449874](https://clinicaltrials.gov/study/NCT04449874)
- [Divarasib — Wikipedia](https://en.wikipedia.org/wiki/Divarasib)
- [Binding Modes MD Simulations — Scientific Reports](https://www.nature.com/articles/s41598-025-07532-2)
- [Synthesis of Quinazoline Organozinc — Org. Process Res. Dev.](https://pubs.acs.org/doi/10.1021/acs.oprd.3c00164)
- [Potency and Safety of KRAS G12C Inhibitors — PMC Systematic Review](https://pmc.ncbi.nlm.nih.gov/articles/PMC12035108/)
