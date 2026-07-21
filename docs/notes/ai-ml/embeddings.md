---
tags:
  - Embeddings
  - Foundation Models
  - Geospatial
  - Representation Learning
---

# Embeddings: A Quiet Idea Doing a Lot of the Work

Transformers and large language models get most of the attention right now. Underneath both of them sits a simpler, older idea that's arguably doing more of the practical work: **embeddings**. If you work with Earth observation data — satellite imagery, climate reanalysis, hydrology, crop surveys — you've likely already felt the exact problem embeddings exist to solve, even without the vocabulary for it.

## The problem underneath the tools

Anyone working with Earth data runs into some version of this:

- Landsat gives you 11 spectral bands, Sentinel-2 gives you 13, Sentinel-1 radar gives you 2 — and none of those band sets line up.
- Labeled examples are scarce. A handful of flood events, a few drought years, a small set of crop-disease photos — nowhere near enough to train a model from scratch.
- Data lives in silos: an optical archive here, a radar archive there, climate reanalysis somewhere else entirely.
- The question people actually want to ask — "where else does this look like *this*?" — has no clean way to be asked across sensors, let alone across time.

None of this is really a modeling problem. It's a **representation** problem: there's no shared language for describing what a place *is*, independent of which instrument happened to observe it.

## What an embedding is

Strip away the math and it's simple. An embedding is a fixed-length list of numbers — a vector — produced by a neural network to summarize something, such that things that are alike end up numerically close together, and things that differ end up far apart.

Think of it as an ecological fingerprint. Not a picture of a place, but a compact signature of what's true about it — vegetation structure, moisture, texture, seasonal rhythm. Two locations photographed by entirely different sensors, months apart, can still land on nearly identical fingerprints if they're ecologically alike. That's the point: the embedding sits downstream of the raw pixels, so it stops caring which instrument took the picture.

This is also, quietly, the first thing that happens inside a large language model. Before a transformer does anything with a sentence, it turns every word into exactly this kind of vector — a reduced-dimensional numeric signature — and everything the model does afterward operates on those vectors, not the words themselves. Vision transformers do the same thing with image patches. Once you notice that, an LLM and an Earth-observation model stop looking like different categories of technology. Both are compressing messy, high-dimensional input into a vector that keeps what matters and drops what doesn't. Only the domain changes.

## The one formula worth knowing: cosine similarity

Once two things are each just a list of numbers, how do you measure "similar"? The answer is high-school geometry.

Picture an embedding as an arrow pointing out from the origin — in practice that space has hundreds of dimensions, but the idea works identically in two. Two arrows pointing roughly the same direction represent things that are alike; arrows pointing in different directions represent things that aren't. Cosine similarity measures the angle between them:

```
similarity = (A · B) / (|A| × |B|)
```

The result always falls between -1 and 1: **1** means the two vectors point the same way (as similar as it gets), **0** means they're unrelated, **-1** means they point in opposite directions. That's the entire mechanism behind most of what follows. "Find more like this" is just computing this one number between a query location's embedding and every other location's, then sorting. "What changed here?" is the same calculation between two dates at the same place — a value near 1 means nothing moved; a noticeable drop means something did. No model runs at query time for either operation. The heavy lifting already happened when the embeddings were generated; from there it's arithmetic, just applied across a few hundred dimensions instead of two.

## How this shows up in Earth observation today

A few different projects have taken this idea and turned it into something usable, each with a slightly different shape:

**Model-as-backbone.** Models like Prithvi (NASA/IBM) and Clay are pretrained on large unlabeled satellite archives. You run your own imagery through them to get an embedding, then fine-tune a small task-specific layer on top. Clay's approach is a good illustration of the band problem above — it conditions its embeddings on each band's wavelength, so the same model can accept whatever spectral bands your sensor happens to provide.

**Precomputed, imagery-free.** AlphaEarth Foundations, from Google DeepMind, publishes a ready-made embedding for every 10-meter pixel on Earth, every year since 2017, already fusing optical, radar, LiDAR, climate, and elevation data. No imagery pipeline required — you query the vector for a location and year, and hand it to an ordinary classifier.

**On-demand and exportable.** OlmoEarth, from the Allen Institute for AI, sits between the two — you choose an area, a time span, and a sensor combination, and it computes and exports the embedding as a standard raster you can drop into QGIS or a Python script directly.

## What this looks like in practice

A few concrete, published examples make the abstraction easier to trust.

**Finding "more like this," anywhere on a map.** Pick a location — a drought-stressed field, a site resembling a known contamination event, a fire-prone hillside — and compute its similarity against every other pixel in a region. The output is a heatmap of everywhere else that looks like the query, ecologically speaking. In one published example, a query pixel over an irrigated field returned other irrigated parcels as the closest matches, and an airport and a dry reservoir as the most dissimilar — with no labels or training involved, just a distance calculation.

**Spotting what changed, automatically.** Compute the embedding for the same place at two points in time and measure the distance between the two vectors. A large distance means something changed. One demonstration used exactly this — no fire-specific model, no burn-scar training — to cleanly highlight a wildfire's scar in California by comparing before-and-after embeddings.

**Mapping a whole region from almost no labels.** Because the embedding has already organized the ecological structure of a landscape, a simple classifier often needs very little labeled data to draw a full map. In one case, sixty labeled pixels — twenty each for mangrove, water, and everything else — were enough to train a plain logistic regression that mapped an entire coastal region well. Adding hundreds more labels barely improved it further, because the embedding was already doing most of the work.

That last point is worth sitting with: the expensive part of a mapping project — collecting enough labels — shrinks from thousands of examples to dozens.

## Where to stay skeptical

Three limits are worth naming plainly:

- **An embedding isn't directly readable.** No single dimension corresponds to a named physical quantity. Translating "this vector" into "elevated soil moisture" takes deliberate extra work.
- **The choice of embedding model shapes the result.** Prithvi, Clay, AlphaEarth, and OlmoEarth won't produce identical vectors for the same location, and that choice isn't neutral.
- **Bias in the training archive travels with the embedding, invisibly** — geographic coverage, sensor era, cloud cover, seasonal sampling. Nothing flags this automatically.

None of that undercuts the value. It just means getting the embedding is the start of an analysis, not the end of one.

## The same pattern, past the edge of Earth science

Here's what makes this worth a second look: none of the problem above is actually specific to satellites. It's a description of any field where data arrives from multiple incompatible instruments, expert labels are scarce relative to raw data, and researchers want to compare things nobody has compared before. Once that shape is visible, it turns up in places that look nothing like remote sensing at first glance.

Biomedical research is a clear example, in outline rather than in detail: a single case is often described by imaging, molecular data, and written notes — different formats, historically siloed, for the same structural reasons a radar archive and an optical archive used to sit apart. Labeled examples of an uncommon condition are scarce for the same reason a labeled flood event is scarce — someone qualified had to produce the label by hand. And "which past cases most resemble this one, across every data type at once" is the same "more like this" query as before, just pointed at a different subject. The general strategy researchers are converging on is familiar by now: encode each data type into a vector, then compare and combine the vectors instead of the raw data, because the raw data was never directly comparable to begin with.

Agriculture sits closer to home and makes the parallel concrete rather than abstract. A crop stress or disease often first shows up as a subtle shift in reflectance and texture — exactly what an Earth-observation embedding is built to catch. The same logic increasingly extends a layer deeper, into plant physiology, with identical mechanics: pretrain broadly, then fine-tune a small model on a handful of labeled examples, because collecting more than a handful is slow no matter which layer of biology is involved.

The point isn't that these fields are the same. It's that the engineering pattern — heterogeneous data in, one comparable vector out, cosine similarity to compare them — doesn't care which domain it's applied to. The math from the middle of this article is the same math wherever it shows up.

## The throughline

Strip the domain-specific nouns away, and the pattern is three steps:

1. A model compresses raw, messy, multi-sensor data into a fixed-length vector.
2. Cosine similarity — no more complicated over a patient record than over a wheat field — measures how alike two vectors are.
3. A small, cheap model sits on top for the task at hand, instead of something large being retrained from scratch every time.

Once a domain's data has an embedding, search, clustering, and classification all become variations on the same few operations, regardless of what the underlying object is.

For a domain scientist, the practical shift isn't "learn to build foundation models." It's that a question which used to need a bespoke model, a large labeled dataset, and months of engineering can often now be answered by borrowing someone else's pretrained embedding and adding a modest amount of labeled data on top. That doesn't replace domain expertise — if anything it rewards it, since knowing exactly which comparisons matter in a field is still the hard part. It just shortens the distance between having a question and getting an answer.

That's the more interesting conversation, past the specifics of any one model or dataset: not whether to use AI, but what in a dataset would be worth comparing to what else, if the comparison were suddenly cheap.
