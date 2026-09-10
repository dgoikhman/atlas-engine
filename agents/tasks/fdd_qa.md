# Task: QA flagged FDD extractions

Review every file matching `data/fdd_extracted/*.REVIEW.json`. Each contains
a raw extraction that failed validation, with the error.

For each one:
1. Read the raw text and the error. Apply the data-quality skill's sanity
   ranges.
2. If the model output was malformed but the underlying values are clearly
   present and plausible, write the corrected JSON to the matching
   `<id>.json` and delete the REVIEW file.
3. If values are implausible or genuinely absent from the document, keep the
   REVIEW file and append a `"qa_note"` explaining what a human must check.
   Never guess a number that is not supported by the source.
4. Finish by printing a table: file, action taken, confidence.

If any file was corrected, commit the changes on branch
`fix/fdd-qa-<today's date>` and open a PR summarizing the batch.
