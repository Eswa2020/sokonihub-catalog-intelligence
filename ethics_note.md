# Multimodal Ethics Note: SokoniHub Catalog Integrity

The system scores whether each listing's photo evidence agrees with its title and sends
disagreements to a human review queue. On the current five-listing fixture the overall flag
rate is 0.4 (2 of 5): shoes 1.0 (n=1), bags 0.33 (n=3), textiles 0.0 (n=1). These numbers
describe a test slice, not the marketplace, and are always reported per category with n.

## Who is in the photos
Scores come from image tags (`lab-bow-v1`), not face or body analysis. Any listing whose tags
include person, face, or child is marked `needs_privacy_review: true` and goes to a reviewer
before the photo is reused; LSO-02, a leso shown being worn, is the current example. Encoders
trained on web images are known to score market and duka photos, local dress, and darker skin
tones less reliably than studio shots. Before trusting a live encoder we will compare flag
rates by photo setting, and we will never generate replacement models or retouch photos to
raise scores.

## Whose language
The encoder vocabulary is English-only, and `vocab_gaps.json` lists 13 title tokens it cannot
read. MKB-03 is a correctly photographed woven bag listed in Kiswahili ("Mkoba wa ukili"); it is
flagged only because none of its title words are known. That is a false flag caused by the
encoder, not the seller. Until coverage improves through an expanded vocabulary or a
multilingual encoder, flags on titles with many uncovered tokens are reviewed by a person, and
titles are never rewritten into English to raise a score.

## Generated pixels
Campaign still-lifes are produced only from the hashed prompt in `prompts/gen/` and stored in
`outputs/` with `not_a_photo_of_the_sku: true`, never in `images/` or the reference set. A
generated image cannot authenticate a listing: NK-99 is resolved by the seller, not by drawing a
matching photo. Prompts exclude people and brand logos, and outputs are reviewed for
market-stall stereotypes before any campaign use.

## Review path
A flag is a recommendation, not a decision. Flagged listings reach the seller or a moderator
with the message in `insights.json`; the seller can upload a matching photo or edit the title,
and a reviewer clears the flag when they agree. Titles are never rewritten silently, and no
listing is taken down on this score alone, because a 0.25 bag-of-words threshold is not a
policy. Seller voice-note transcripts are personal data under the Kenya Data Protection Act and
stay out of logs and public outputs.

## Limits
Five listings, a tag-based stand-in encoder, and proxy relevance labels for search. These
results show the controls work; they do not measure accuracy or fairness at marketplace scale.


## Manager summary
Main risks: correct listings written in Kiswahili or Sheng can be flagged because the encoder
does not know their words (MKB-03); photos of people carry personal data; a generated
campaign image could be mistaken for a real product photo; and five listings are too few to
judge accuracy. Mitigations: every flag goes to a person rather than an automatic action,
rates are reported per category with n, person/face/child photos are routed to privacy review,
generated images are labelled and kept out of the reference set, and every model and prompt is
pinned so results can be reproduced. We will not claim the system is bias-free, that it is
accurate at marketplace scale, that a live CLIP model produced these scores, or that a
generated image shows a real product.

## Transfer
The same join, pins, and review path can later check clinic posters and leaflet photos for the
AfyaPlus health service. That work will use its own fixtures: no patient images or triage
records enter this catalog, and no marketplace listings enter triage logs.