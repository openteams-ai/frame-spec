# Code Review Norms Example

This example uses **only the four required `v0.2` fields** — `type`, `name`, `description`, and `visibility` — and no suggested fields at all.

It exists to answer a common question: if a Frame's metadata is minimal, where is the value? The answer is the body. Everything useful in this Frame is prose — what reviewers block on, how to label comments, when to stop reviewing and approve. The metadata only says what the file is and who may see it.

The body has no section headings, because `v0.2` does not define any. Sections are worth adding when a Frame is long enough that a reader needs to navigate it, and not before.

Compare with:

- [../minimal/](../minimal/) — the smallest possible valid Frame, kept deliberately abstract
- [../with-suggested-fields/](../with-suggested-fields/) — the same file shape with the optional metadata fields added
