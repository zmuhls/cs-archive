# tinker devlog

development notes for fine-tuning vision-language models on historical archival materials

---

## project overview

this project explores fine-tuning Qwen3-VL-30B-A3B-Instruct for transcribing historical documents from the Common School Archive, a collection documenting the administrative history of New York State's public school system from the early 19th century through mid-20th century consolidation efforts.

the work advances three interconnected goals:
1. **methodological transparency** - documenting the full pipeline from archival digitization to fine-tuned model, suitable for DH quarterly publication
2. **local-first AI research** - demonstrating how institutions can develop specialized transcription capabilities without relying on proprietary black-box services
3. **reproducible fine-tuning** - contributing to the tinker-cookbook ecosystem with recipes tailored to archival document types

---

## archival materials: four document types

the Common School Archive contains heterogeneous materials requiring distinct transcription strategies. we have identified four primary document classes for fine-tuning:

### 1. notecards (B0594 - District Notecard Records)

index cards with typed headers and handwritten action entries tracking individual school district administrative history.

**characteristics:**
- typed header with school name and county (e.g., "Deaser Union School (Albany Co.)")
- chronological handwritten entries with abbreviated dates
- action notation using historical abbreviations: "adm" (admitted), "appli" (application), "adv" (advanced), "M-1", "M-P" (classification codes)
- mixed media: typewritten structure with cursive fill-in

**transcription challenges:**
- date format variability: "19 July 1926", "4/30/59", "4 Nov. 1926"
- abbreviated actions requiring expansion or preservation
- faded ink, overlapping entries, correction marks

**parser status:** implemented in `parsers/notecards.py` with date extraction, school/county metadata, and action classification

### 2. ledgers and tables (B0494 - District-Consolidation-Data)

tabular records documenting school district consolidations, mergers, and closures across New York State.

**characteristics:**
- column-based layout with district names, dates, action types
- variable separators: pipes, tabs, multiple spaces
- header rows with standardized vocabulary: "District", "Date", "Action", "County"
- spans multiple decades of consolidation activity (1940s-1960s)

**transcription challenges:**
- column alignment detection in degraded scans
- distinguishing header rows from data
- handling merged cells and spanning entries
- OCR noise in ruled line detection

**parser status:** implemented in `parsers/tables.py` with separator detection, header inference, and row extraction

### 3. handwritten minutes (South-Kortright style)

19th-century school district meeting minutes written in period cursive, following formal parliamentary structure.

**characteristics:**
- opening statement identifying meeting location, date, and participants ("At a meeting of the inhabitants or freeholders of School District No. 2...")
- numbered vote resolutions: "Vote 1st. That the trustees shall have to hire who they please..."
- adjournment notation
- archaic spellings and abbreviations ("ye", "rec'd", "&c.")

**transcription challenges:**
- 19th-century cursive letterforms
- period spelling variations requiring diplomatic vs. normalized output
- ink degradation over 150+ years
- understanding vote numbering conventions (1st, 2nd, 3rd, etc.)

**parser status:** implemented in `parsers/meeting_minutes.py` with vote extraction, opening/adjournment detection, and date parsing

### 4. typewritten minutes

mid-20th century meeting records produced on typewriters, representing the transition from handwritten to mechanized documentation.

**characteristics:**
- standard business letter formatting
- clearer text but with typewriter-specific artifacts
- carbon copy degradation
- institutional letterhead and stamps
- mixed handwritten annotations and signatures

**transcription challenges:**
- strike-through and overtype corrections
- carbon copy fading
- handwritten marginalia alongside typed text
- distinguishing original typing from later additions

**parser status:** pending - will extend meeting_minutes parser with typewriter-specific preprocessing

---

## why Qwen3-VL-30B-A3B-Instruct

selected this model for historical OCR based on architectural fit:

| feature | relevance to archival materials |
|---------|--------------------------------|
| **A3B (Active 3B params)** | 30B total parameters but only 3B active per forward pass - enables training on academic GPU budgets |
| **high-resolution support** | native 1280px+ processing preserves fine cursive details critical for 19th-century handwriting |
| **multilingual pretraining** | exposed to diverse scripts during pretraining (Latin variants, Gothic, etc.) |
| **32K context window** | handles full-page transcriptions without chunking, preserving document structure |
| **efficient training** | LoRA fine-tuning with rank 64 yields strong results in 3-5 epochs |

the model's mixture-of-experts architecture aligns with the heterogeneous nature of archival collections - different "experts" may activate for different document types without explicit routing.

---

## tinker api: training infrastructure

using Thinking Machines Lab's Tinker platform for distributed fine-tuning. key advantages for this project:

**infrastructure abstraction:**
```python
import tinker
service_client = tinker.ServiceClient()
training_client = service_client.create_lora_training_client(
    base_model="Qwen/Qwen3-VL-30B-A3B-Instruct",
    rank=64,  # higher rank for complex visual-text alignment
)
```

the API handles:
- distributed training across GPU clusters
- gradient accumulation and optimizer state management
- checkpoint serialization and weight export

**local control preserved:**
- all training data remains local until explicitly sent
- loss functions, data augmentation, prompt engineering happen client-side
- full access to weights for local deployment post-training

**workflow:**
1. prepare training examples locally (image + ground truth transcription pairs)
2. send batches via API for forward/backward passes
3. accumulate gradients, step optimizer via API
4. export fine-tuned LoRA weights for local inference

this division of labor keeps sensitive archival materials under institutional control while leveraging scalable compute.

---

## training configuration rationale

optimized hyperparameters for historical document transcription:

```python
@chz.chz
class HistoricalOCRExperimentConfig:
    learning_rate: float = 1e-4      # conservative for long sequences
    lora_rank: int = 64              # high rank for visual grounding
    batch_size: int = 4              # small due to long sequences + images
    max_length: int = 16384          # full-page transcription support
    num_epochs: int = 3              # quick convergence with quality data
    max_image_size: int = 1280       # preserve fine handwriting details
    enhance_contrast: bool = True    # handle faded historical documents
    contrast_factor: float = 1.3     # moderate boost for degraded ink
```

**key decisions:**

*lower learning rate (1e-4 vs typical 5e-4):* historical documents have idiosyncratic patterns that can be overfit quickly. slower learning preserves the model's general visual understanding while adapting to period-specific letterforms.

*higher LoRA rank (64 vs typical 16-32):* transcription requires tight visual-text alignment. higher rank provides more capacity for learning the mapping between visual cursive strokes and corresponding text tokens.

*longer max_length (16384):* full-page transcriptions regularly exceed 3000 tokens. truncating would lose document structure and create training/inference mismatch.

*contrast enhancement:* archival scans frequently suffer from faded ink against aged paper. adaptive contrast preprocessing recovers legibility without manual per-image tuning.

---

## transcription modes

three output modes support different research uses:

**diplomatic** (default):
preserves all original features - archaic spellings, abbreviations, line breaks
```
ye olde shoppe → ye olde shoppe
```
use case: linguistic analysis, paleographic study, legal/archival citation

**normalized:**
modernizes spelling, expands abbreviations
```
ye olde shoppe → the old shop
```
use case: full-text search, accessibility, downstream NLP

**structured:**
JSON-style output with uncertainty markers
```
the old [?]hop
```
use case: quality control, human-in-the-loop correction, confidence estimation

mode selection happens at training time via system prompt, enabling single model to serve multiple output requirements.

---

## data pipeline

### local data organization
```
common_school_archive/
├── notecards/
│   ├── images/
│   │   ├── B0594_001.jpg
│   │   └── ...
│   └── transcriptions/
│       ├── B0594_001.txt
│       └── ...
├── ledgers/
│   ├── images/
│   └── transcriptions/
├── handwritten_minutes/
│   ├── images/
│   └── transcriptions/
└── typewritten_minutes/
    ├── images/
    └── transcriptions/
```

### training invocation
```bash
export TINKER_API_KEY=your_key

python -m tinker_cookbook.recipes.historical_ocr.train \
    experiment_dir=./experiments \
    data_source=local \
    data_dir=/path/to/common_school_archive \
    ocr_mode=diplomatic \
    max_image_size=1280 \
    enhance_contrast=True
```

---

## evaluation metrics

tracking three complementary metrics:

1. **Character Error Rate (CER):** primary metric for OCR quality
   - edit distance between predicted and ground truth at character level
   - handles insertions, deletions, substitutions
   - sensitive to minor transcription variations

2. **Word Error Rate (WER):** secondary, more interpretable
   - edit distance at word level
   - better correlates with downstream usability
   - less sensitive to spacing/punctuation

3. **Negative Log-Likelihood (NLL):** tracked automatically during training
   - model confidence measure
   - useful for detecting overfitting
   - correlates with but doesn't replace CER/WER

custom evaluators extend `SamplingClientEvaluator` for document-type-specific assessment:
```python
class CERDocumentEvaluator(SamplingClientEvaluator):
    async def __call__(self, sampling_client):
        # compute CER on held-out set
        ...
```

---

## toward openness and transparency

this project embodies principles for responsible AI research in cultural heritage contexts:

### open methodology
- full training pipeline documented in tinker-cookbook
- hyperparameter rationale explained, not just listed
- failure modes and limitations acknowledged

### local-first architecture
- archival materials never leave institutional control
- fine-tuned weights can be exported for fully local inference
- no ongoing dependence on external API for production use

### reproducibility
- deterministic train/test splits with documented seeds
- versioned parser implementations
- configuration files capture full experiment state

### appropriate automation
- AI transcription as assistance, not replacement for expertise
- uncertainty markers enable human verification
- diplomatic mode preserves source fidelity

---

## development timeline

### phase 1: parser development (completed)
- implemented NotecardParser for B0594 records
- implemented TableParser for B0494 consolidation data
- implemented MeetingMinutesParser for South-Kortright documents
- established ParsedDocument/ParsedEntry data structures

### phase 2: training infrastructure (completed)

- integrated historical_ocr recipe into tinker-cookbook
- configured Qwen3-VL-30B-A3B training parameters
- established local data pipeline and preprocessing
- fixed inference.py SamplingClient API (create_sampling_client, num_samples, renderer/tokenizer decode)

### phase 3: fine-tuning experiments (current)

- completed LoRA fine-tuning run (rank 64, 3 epochs, lr 0.0001) on 578 training samples
- holdout evaluation on 244 unseen pages (2026-01-24):
  - overall: fine-tuned CER 57.25% vs baseline 61.01% (+6% relative improvement)
  - typed minutes: 1.22% CER vs 23.58% baseline (strongest category, near-perfect)
  - handwritten minutes: 114.89% vs 117.57% (marginal, both struggle on 1831 cursive)
  - tables: 38.08% vs 38.63% (negligible difference)
  - notecards: 74.79% vs 64.28% (regression, only 3 holdout pages available)
- key finding: fine-tuned model eliminates preamble hallucination and produces cleaner output format
- key finding: notecard regression suggests overfitting with limited holdout coverage

### phase 4: evaluation and publication (next)

- larger holdout runs (25+ per type) for typed minutes and tables
- error analysis by document type and era
- cross-document-type transfer experiments
- methodological commentary for DH quarterly
- weight release under appropriate license

---

## notes for DH quarterly methodology section

key themes for the article:

1. **heterogeneous archives require heterogeneous approaches** - the four document types demand different preprocessing, prompting, and evaluation strategies despite sharing an OCR objective

2. **fine-tuning democratizes specialized transcription** - institutions can develop capabilities matching their collections without enterprise contracts or perpetual API dependencies

3. **transparency enables critique** - publishing the full pipeline (data preparation, training config, evaluation protocol) allows the DH community to assess, replicate, and improve upon results

4. **diplomatic vs. normalized is a research question** - the choice of transcription mode encodes scholarly values; fine-tuning enables per-project customization rather than one-size-fits-all

5. **model architecture matters for archives** - Qwen3-VL's mixture-of-experts design aligns with collection heterogeneity in ways that warrant theorization

---

## open questions

- how much training data per document type yields diminishing returns?
- does multi-document-type training improve or harm per-type performance?
- can structured output mode enable effective active learning?
- what is the right granularity: page-level vs. entry-level training?
- how do results transfer to other archival collections?

---

## references

- Thinking Machines Lab. (2025). Tinker. https://thinkingmachines.ai/tinker/
- tinker-cookbook historical_ocr recipe: `tinker_cookbook/recipes/historical_ocr/`
- Common School Archive finding aids: [pending link]
- Qwen3-VL model card: https://huggingface.co/Qwen/Qwen3-VL-30B-A3B-Instruct

---

*last updated: 2026-01-27*

---

## update 2026-01-27

- Fix: Updated image links in `output/comprehensive/District-Consolidation-Data_100-116_comprehensive.md` to use repository-relative paths (`../ocr/tables/images/...`) instead of `raw.githubusercontent.com` which returned 404s on GitHub.
- Rationale: Keep comprehensive markdown self-contained and renderable on GitHub; avoid `raw` endpoints that can fail and prefer paths resolvable within the repo.
- Next: Audit remaining comprehensive files and generation scripts to standardize image URL patterns (use relative paths for repo images; `media.githubusercontent.com` for LFS-backed assets).

- Fix: Closed unclosed triple-backtick code fences in comprehensive markdown files (`Amityville-Records_comprehensive.md`, `District-Consolidation-Data_100-116_comprehensive.md`) to ensure proper GitHub rendering.
