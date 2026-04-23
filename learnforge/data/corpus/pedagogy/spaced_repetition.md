# Spaced Repetition
## What it is
A learning technique where review intervals increase as knowledge strengthens. Based on the forgetting curve — we forget ~50% within a day without review, but each review extends retention.
## Algorithm
- New card: review after 1 day
- Correct answer: double the interval (1→2→4→8→16 days)
- Wrong answer: reset to 1 day
- Confidence rating (1-5) adjusts the multiplier
## Why it works
Spaced repetition exploits the testing effect (retrieving information strengthens memory more than re-reading) and the spacing effect (distributed practice beats massed practice).
## Implementation
Use a priority queue sorted by next_review date. Present cards that are due. Track: times_seen, times_correct, confidence, last_reviewed, next_review.
