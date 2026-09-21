# METRICS.md — Retrieval Quality Comparison

Domain: Open-source package vulnerabilities (DOMAIN_ID = 4)
Embedding model: sentence-transformers/all-MiniLM-L6-v2
Corpus: 47 documents, 200,022 bytes (see reports/hw03/SOURCES.md and
CORPUS_MANIFEST.json)
Questions: 5 (see reports/hw03/questions.yaml), top_k = 5

## 1. Retrieval Quality Comparison

| Technique | Chunks | Avg chunk length (chars) | Top-1 cosine | Mean@k cosine | Recall@5 | Mean retrieval latency (ms) |
|---|---|---|---|---|---|---|
| Token | 284 | 786 | 0.6939 | 0.6335 | 0.70 (3.5/5) | 9.28 |
| Semantic | 98 | 2041 | 0.6694 | 0.5561 | 1.00 (5/5) | 6.96 |
| Sentence-window | 658 | 304 | 0.6921 | 0.6622 | 0.80 (4/5) | 12.24 |

**Recall@5 breakdown per question:**

| Question | Expected source(s) | Token | Semantic | Sentence-window |
|---|---|---|---|---|
| q1 | 02_lodash_CVE-2020-8203.txt | ✅ | ✅ | ✅ |
| q2 | 01_log4j_CVE-2021-44228.txt | ❌ | ✅ | ✅ |
| q3 | 05_django_CVE-2021-35042.txt | ✅ | ✅ | ✅ |
| q4 | 16_xz-utils...txt AND 18_event-stream...txt | ⚠️ partial | ✅ | ❌ |
| q5 | 27_equifax-case-study.txt | ✅ | ✅ | ✅ |

## 2. Confidently-scored retrieval that does NOT contain the answer

**Question q2** ("What CVSS v3.1 base score did Log4Shell (CVE-2021-44228)
receive, and what does that score reflect?") under **Token chunking**:

| Rank | Store score | Cosine sim | Source file |
|---|---|---|---|
| 1 | 0.6734 | 0.6152 | 33_cvss-worked-examples.txt |
| 2 | 0.6283 | 0.6125 | 23_vulnerability-databases-explainer.txt |
| 3 | 0.5444 | 0.6196 | 33_cvss-worked-examples.txt |
| 4 | 0.5238 | 0.5442 | 38_patch-prioritization-kev-epss.txt |
| 5 | 0.5094 | 0.5172 | 33_cvss-worked-examples.txt |

None of Token chunking's top-5 results for this question came from the
expected source file, `01_log4j_CVE-2021-44228.txt`, despite the rank-1
result scoring a reasonably confident 0.6734.

**Why the embedding likely considered this chunk similar:** the top
result comes from `33_cvss-worked-examples.txt`, a document in this
corpus that specifically walks through Log4Shell's CVSS score in detail
as a worked example. The chunk is genuinely topically close to the
query — it discusses Log4Shell and CVSS scoring together — but it is a
*secondary reference* document discussing the score, not the *primary
source* document reporting it. Token-based chunking, being blind to
document identity and topic boundaries, cannot distinguish "a chunk
about Log4Shell's score" from "the chunk that is Log4Shell's own
advisory," so the embedding's topical similarity judgment was reasonable
even though the retrieval was not the intended source.

Semantic and sentence-window chunking both successfully retrieved the
correct primary source (`01_log4j_CVE-2021-44228.txt`) for this same
question, showing this is a real, technique-specific weakness of Token
chunking on this corpus rather than an inherent limitation of the
embedding model itself.

## 3. Observations

Semantic chunking produced by far the fewest chunks (98) and the
largest average chunk length (2041 characters), consistent with the
expectation that most sentences within a single-topic CVE write-up
stay thematically similar, giving the semantic splitter few genuine
"topic shift" boundaries to cut at. This produced the highest Recall@5
(1.00) — larger chunks are more likely to contain a full answer
somewhere inside them — but the lowest mean@k cosine (0.5561), since
larger, more heterogeneous chunks dilute the average relevance across
the top-k results.

Sentence-window chunking produced the most chunks (658) and the
smallest average length (304 characters), and won on mean@k cosine
(0.6622) — its narrow, per-sentence chunks retrieve consistently
focused, relevant text once they do match. However, it missed both
expected sources entirely on the one cross-document question (q4),
suggesting that very fine-grained chunks can lose the broader context
needed to connect two related but separately-discussed incidents (the
XZ Utils backdoor and the event-stream supply-chain attack), even
though the window metadata is meant to preserve some surrounding
context.

Token chunking landed in between on most metrics, but produced this
report's one clear "confidently wrong" case (q2), where a
topically-related secondary document out-competed the true primary
source. This highlights a structural weakness distinct from semantic
relevance: token chunking cannot distinguish where one referenced
CVE's discussion ends and another begins across multi-topic reference
documents in this corpus.

If this experiment were extended with additional queries, we would
expect semantic chunking to remain strongest on straightforward,
single-fact lookups (thanks to high recall), while sentence-window
chunking would likely continue to win on questions demanding precise,
narrow relevance from within a single document, and to continue
struggling specifically on cross-document synthesis questions like q4.

## 4. Conclusion

For this corpus, **semantic chunking is the best overall choice**: it
achieved perfect Recall@5 (1.00), successfully retrieving the correct
source document for every question including the cross-document
synthesis question (q4) that sentence-window chunking missed entirely.
While its mean@k cosine score was the lowest of the three techniques,
reflecting that its larger chunks are less narrowly focused, retrieval
recall — actually finding the right document at all — matters more
than ranking precision for a corpus like this one, where questions
often require synthesizing context from a full incident write-up rather
than a single isolated sentence. Sentence-window chunking is a strong
runner-up, particularly for narrow, single-fact questions, but its
failure on the one multi-document question is a meaningful limitation
for a domain where vulnerabilities are frequently cross-referenced
across multiple documents in this corpus.
