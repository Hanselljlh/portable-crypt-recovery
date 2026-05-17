# 09-password-builder.md

## Purpose

This step defines how the app builds password candidate sources for VeraCrypt and TrueCrypt recovery jobs.

The Password Builder does not crack passwords, extract headers, choose hash modes, handle PIM values, handle keyfiles, run Hashcat, or manage the queue.

Its job is to let the user describe likely password patterns, preview the expected candidate count, apply known filters before generation, save generated wordlists inside the workspace, and connect password sources to later job generation.

The app must not use system temp folders for password data, password candidates, generated wordlists, recipes, previews, or temporary candidate chunks.

## Core Design

Passwords are built from ordered segments.

Each segment can have its own variants.

Final password candidates are created by choosing one variant from each enabled segment and joining the selected variants in segment order.

Example:

```text
Segment 1:
  abc

Segment 2:
  123
  567

Segment 3:
  efg
```

Generated candidates:

```text
abc123efg
abc567efg
```

Segment order matters.

Variant order matters.

Duplicate cleanup should preserve first-seen order instead of sorting the final password list. This keeps the user’s most likely guesses earlier.

## User Inputs

The Password Builder should accept:

```text
Password source name
Selected target
Selected header
Selected hash mode set
Selected PIM set, if applicable
Selected keyfile set or keyfile group, if applicable
Ordered password segments
Segment names
Segment variant mode
Exact text variants
Case variant options
Same characters but unknown order
Same characters with unknown order and unknown capitalization
Manual variant lists
Segment filters before generation
Pattern tokens before generation
Candidate count preview
Generated candidate review for small lists
Imported wordlists
External wordlist references
Generate wordlist
Save password recipe
Update job draft
```

## Password Source Modes

The app should support these password source modes:

```text
Segment builder
Manual password list typed or pasted by user
Imported wordlist
External wordlist reference
Generated wordlist from saved recipe
```

### Segment Builder

The segment builder is the main feature for this step.

It creates candidates from ordered password parts.

### Manual Password List

The user may type or paste one candidate per line.

The app should deduplicate while preserving first-seen order.

### Imported Wordlist

The user may import an existing wordlist into the workspace.

Default behavior should copy the wordlist into:

```text
inputs/wordlists/imported/
```

This keeps cleanup simple and portable.

### External Wordlist Reference

The user may optionally reference a very large external wordlist instead of copying it.

External references are advanced and non-portable.

The app should warn that external files must be cleaned separately and may need repair if moved.

### Generated Wordlist

Generated wordlists from the segment builder must always be saved inside:

```text
generated/wordlists/
```

## Segment Variant Modes

Each segment should support these variant modes:

```text
Exact text
Case variants
Same characters, unknown order
Same characters, unknown order plus case variants
Manual variant list
Pattern token expansion
```

## Exact Text Variants

Exact text means the app uses the text exactly as entered.

Examples:

```text
dog
Dog
DOG
123
!
```

Exact text can also be used for separators.

Examples:

```text
-
_
.
!
@
```

No separate separator system is required for version 1. Separators can simply be exact text segments.

The app should not trim spaces inside exact text unless the user clearly chooses cleanup behavior.

Leading and trailing spaces should trigger a warning because they may be accidental.

Suggested warning:

```text
This variant starts or ends with a space. Keep it?
```

## Case Variants

Case variants should generate common capitalization forms from a base word.

Suggested options:

```text
original
lowercase
uppercase
capitalized first letter
title case
all capitalization combinations
```

Example input:

```text
summer
```

Common case variants:

```text
summer
SUMMER
Summer
```

All capitalization combinations should be treated as an advanced option because it can grow quickly.

Example input:

```text
abc
```

All capitalization combinations:

```text
abc
abC
aBc
aBC
Abc
AbC
ABc
ABC
```

The app should deduplicate case results.

Example:

```text
123
```

Case variants do not create useful new values, so duplicates should collapse to one value.

## Same Characters, Unknown Order

This mode is for cases where the user knows the characters but not the order.

Example input:

```text
abc
```

Generated variants:

```text
abc
acb
bac
bca
cab
cba
```

The app should generate unique permutations only.

If the input has repeated characters, duplicates must be removed.

Example input:

```text
aab
```

Unique variants:

```text
aab
aba
baa
```

This mode can grow very quickly, so the app must show a count preview before generating.

## Same Characters, Unknown Order Plus Unknown Capitalization

This mode combines unique character order permutations with case variants.

Example input:

```text
ab
```

Generated variants include:

```text
ab
aB
Ab
AB
ba
bA
Ba
BA
```

This mode can grow extremely quickly.

The app should require preview and confirmation before saving if the generated count is large.

The app should deduplicate results after both permutation and case expansion.

## Manual Variant Lists

The user may type or paste manual variants for a segment.

Rules:

```text
one variant per line
blank lines ignored by default
duplicates removed
first-seen order preserved
optional warning for leading or trailing spaces
```

Example:

```text
dog
Dog
DOG
puppy
Puppy
```

Manual lists should be useful when the user already has likely variants and does not want the app to transform them.

## Pattern Token Expansion

The app should support a simple user-facing pattern token system for segment filters and segment generation.

The token system should mostly follow common Hashcat-style mask tokens, but the normal GUI should avoid confusing custom charset tokens like `?1`.

The app should not expose `?1` as a user-facing token because it can be confused with `?l` depending on the user’s font.

Use `?C` as the app-specific user-facing token for any letter.

User-facing tokens:

```text
?l = lowercase letter, a-z
?u = uppercase letter, A-Z
?C = any letter, lowercase or uppercase
?d = digit, 0-9
?s = symbol
?a = any basic character
?h = lowercase hex character, 0-9 or a-f
?H = uppercase hex character, 0-9 or A-F
```

Important rule:

```text
?C is an app-specific user-facing token.
```

If a later command builder needs to convert this into a Hashcat-compatible mask, it may translate `?C` internally into a Hashcat custom charset.

The user should not have to see or manage that translation.

Example:

```text
?l?d?C?d
```

Means:

```text
lowercase letter
digit
any lowercase or uppercase letter
digit
```

It can generate values such as:

```text
a1a1
a1A1
b2c3
b2C3
```

Known fixed characters should be typed directly.

Example:

```text
1a
1A
```

If the user knows a segment starts with either `1a` or `1A`, that should be entered as an allowed-starts filter or two exact variants, not as a confusing custom charset.

## Ordered Segment Behavior

The user should be able to add, remove, rename, duplicate, enable, disable, and reorder segments.

Suggested segment actions:

```text
Add Segment
Move Segment Up
Move Segment Down
Duplicate Segment
Disable Segment
Delete Segment
Preview Segment Variants
```

Disabled segments should not contribute to candidate generation.

The app should show the segment order clearly.

Example:

```text
1. name
2. year
3. symbol
```

Final candidates are built as:

```text
name + year + symbol
```

The app should not reorder segments automatically.

## OR Variants Inside Each Segment

Each segment contains OR variants.

Example:

```text
Segment 1:
  dog OR Dog OR DOG

Segment 2:
  123 OR 456
```

Generated candidates:

```text
dog123
dog456
Dog123
Dog456
DOG123
DOG456
```

The app should explain this simply:

```text
The app will use one option from each segment, in order.
```

## Segment Filters

Segment filters are applied before generation.

Use segment filters when the user already knows a candidate pattern is impossible or required.

This is the main filtering system.

The app should provide as many useful filter options as practical before generation, because known-invalid candidates should not be generated in the first place.

Supported segment filters should include:

```text
must start with
must not start with
must end with
must not end with
must contain
must not contain
must match pattern tokens
must not match pattern tokens
allowed exact variants
excluded exact variants
allowed prefixes
excluded prefixes
allowed suffixes
excluded suffixes
```

Examples:

```text
must start with 2
must not start with 1
must match ?d?l?d?l?d?l
must start with 1a or 1A
exclude exact segment variant AAb
exclude exact segment variant ABa
exclude exact segment variant BAa
```

Exact exclusions should be case-sensitive.

Example:

```text
AAb
```

is different from:

```text
aab
```

Core rule:

```text
If the user knows a pattern is invalid before generation, it should be entered as a segment filter, not removed later during review.
```

## Position and Pattern Rules

For “same characters but unknown order,” the user should be able to add position rules before generation.

Examples:

```text
Known characters:
123abc

Rule:
must start with 2
```

This avoids generating every possible permutation and then removing most of them later.

The user should also be able to use pattern rules.

Example:

```text
Known characters:
123abc

Pattern:
?d?l?d?l?d?l
```

This means:

```text
digit
lowercase letter
digit
lowercase letter
digit
lowercase letter
```

The app should apply these filters during generation when possible.

If early filtering is not practical for a specific generator, the app should still keep all temporary candidate chunks inside the workspace and remove invalid candidates before saving the final wordlist.

## Candidate Review Step

Candidate review happens after generation.

Candidate review is only for small or manageable lists where the user can visually spot a few wrong candidates.

Candidate review should not be the main filtering system.

The review screen should allow:

```text
view generated candidates
search candidates
select candidates
delete selected candidates
save the edited list
return to segment filters and regenerate
```

The review step should not encourage generating huge lists and filtering them afterward.

Core rule:

```text
Large candidate lists should be filtered before generation, not generated first and cleaned afterward.
```

Suggested candidate review warning:

```text
Candidate review is intended for small lists. If many candidates are wrong, go back and add segment filters before regenerating.
```

The review screen should show only a limited number of candidates at a time.

The app should warn that visible candidate review may expose password guesses on screen.

## Candidate Count Preview

The app must show candidate counts before generating a wordlist.

For segment builder mode:

```text
final candidate count =
segment 1 variant count
× segment 2 variant count
× segment 3 variant count
...
```

Example:

```text
Segment 1 variants: 3
Segment 2 variants: 10
Segment 3 variants: 2

Estimated candidates:
3 × 10 × 2 = 60
```

The preview should include:

```text
segment count
variant count per segment before filters
variant count per segment after filters
estimated candidate count before duplicate cleanup
estimated duplicate count, if known
final candidate count after cleanup, if calculated
output wordlist path
warnings
```

For very large lists, exact duplicate count may require generation.

The app may show:

```text
Exact duplicate count will be known after generation.
```

## Large Candidate Warning

The app should warn when a generated list may be large.

Suggested warning thresholds:

```text
More than 100,000 candidates:
  show warning

More than 1,000,000 candidates:
  require confirmation

More than 10,000,000 candidates:
  recommend using Hashcat masks or a smaller plan instead
```

Suggested warning:

```text
This password plan will generate 1,250,000 candidates. Generated wordlists can consume disk space and may greatly increase runtime.
```

The app should allow the user to continue after confirmation unless a later implementation sets a hard safety limit.

## Duplicate Cleanup

The app should remove duplicate final candidates.

Rules:

```text
remove exact duplicate candidate strings
preserve first-seen order
do not sort final candidates by default
show duplicates removed in preview or generation summary
```

Reason:

```text
The user’s segment and variant order may represent likelihood. Preserving order keeps likely candidates earlier.
```

The app should also deduplicate inside each segment before final generation.

Deduplication levels:

```text
deduplicate variants within each segment
deduplicate final full password candidates
deduplicate imported or pasted manual password lists
```

## Blank and Empty Values

The app should allow an optional empty segment variant only if the user explicitly chooses it.

This supports patterns where a part may or may not exist.

Example:

```text
Segment 2:
  empty
  123
  2024
```

Generated examples:

```text
password
password123
password2024
```

The UI should not silently create empty variants from blank lines.

Blank lines in manual lists should be ignored unless the user intentionally adds an empty variant.

## Character and Encoding Handling

Version 1 should keep encoding simple and predictable.

Suggested rule:

```text
Save generated wordlists as UTF-8 text with one candidate per line.
```

The app should warn if candidates contain unusual control characters.

The app should preserve normal spaces and Unicode characters if the user enters them intentionally.

The app should not automatically normalize Unicode, change line endings inside candidates, or alter password text unless the user chooses a cleanup option.

## Generated Wordlist Format

Generated wordlists should contain one password candidate per line.

Suggested path:

```text
generated/wordlists/password_list_<password_set_id>.txt
```

Suggested example:

```text
dog123!
dog123@
Dog123!
Dog123@
DOG123!
DOG123@
```

The app should not print password candidates in normal logs.

If a preview shows sample candidates, it should show only a small limited sample.

Suggested preview sample limit:

```text
first 20 candidates
```

The app should make clear that previews may expose password guesses on screen.

## Password Recipe Storage

The app should save the password build recipe inside the workspace.

Suggested folder:

```text
generated/recipes/
```

Suggested filename:

```text
password_recipe_<password_set_id>.json
```

Suggested fields:

```text
schema_version
password_set_id
target_id
header_id
mode_set_id
pim_set_id
keyfile_group_id
created_timestamp
updated_timestamp
password_source_mode
source_name
segments
candidate_count_before_filters
candidate_count_after_filters
candidate_count_before_dedupe
candidate_count_after_dedupe
duplicates_removed
wordlist_path
external_wordlist_path
warnings
notes
```

Suggested segment fields:

```text
segment_id
segment_name
enabled
order
variant_mode
raw_input
case_options
pattern_tokens
allow_empty_variant
filters
variant_count_before_filters
variant_count_after_filters
variant_count_before_dedupe
variant_count_after_dedupe
warnings
```

Suggested filter fields:

```text
filter_id
filter_type
filter_value
case_sensitive
enabled
applied_before_generation
notes
```

## Password Source Metadata

Each password source should have metadata.

Suggested filename:

```text
generated/recipes/password_source_<password_set_id>.json
```

Suggested fields:

```text
schema_version
password_set_id
password_source_mode
display_name
workspace_wordlist_path
external_wordlist_path
is_external
candidate_count
created_timestamp
updated_timestamp
dedupe_enabled
order_preserved
used_in_job_drafts
warnings
notes
```

The metadata should not store cracked results.

The metadata may store the recipe because the recipe itself is part of the recovery strategy and must stay inside the workspace.

## Candidate Generation Process

The app should generate candidates inside the workspace only.

Suggested temporary folder for active generation:

```text
temp/staging/
```

Rules:

```text
do not use system temp folders
write temporary chunks only inside the workspace
write final generated wordlist inside generated/wordlists/
apply known filters before or during generation when practical
deduplicate final candidates
use atomic save behavior where practical
update cleanup manifest
save metadata after generation
```

For large lists, the app may generate in chunks inside the workspace.

Suggested chunk folder:

```text
generated/candidates/
```

Temporary chunks should be cleaned when safe, but the app must not claim secure deletion.

## Imported Wordlists

Imported wordlists should follow Step 2 workspace rules.

Default behavior:

```text
copy imported wordlists into inputs/wordlists/imported/
```

Optional behavior:

```text
reference external wordlist
```

If the user chooses external reference mode, the app should warn:

```text
This wordlist will remain outside the workspace. At cleanup time, you must remember to delete or securely erase this external location separately. The workspace cleanup process cannot remove files saved elsewhere.
```

Imported wordlist metadata should be stored in:

```text
inputs/wordlists/manifests/
```

Suggested metadata fields:

```text
wordlist_id
source_original_path
workspace_copy_path
is_external
file_size
line_count_if_counted
import_timestamp
source_modified_timestamp
notes
```

## Connecting Password Sources to Job Drafts

The Password Builder should update job draft metadata.

A job draft should reference:

```text
password_set_id
password_source_mode
password_wordlist_path
password_recipe_path
candidate_count
is_external_wordlist
warnings
```

The Password Builder should not run Hashcat.

The Password Builder should not create final queued jobs by itself unless the later final job expansion screen is included in this step.

Recommended version 1 behavior:

```text
Password Builder updates job drafts only.
Final queue expansion happens in the later command/job generation step after hash modes, PIMs, keyfiles, and password sources are combined.
```

## Job Count Awareness

The Password Builder should show the full expected job multiplication because it is the last builder step before reports and final build planning.

For VeraCrypt:

```text
runnable VeraCrypt modes
× PIM values
× keyfile sets
× password sources
= VeraCrypt job variants
```

For TrueCrypt:

```text
runnable TrueCrypt modes
× keyfile sets
× password sources
= TrueCrypt job variants
```

The preview should show separate counts for VeraCrypt and TrueCrypt when both are present.

Example:

```text
Runnable VeraCrypt modes: 9
PIM values: 18
Keyfile sets: 4
Password sources: 2
Estimated VeraCrypt job variants: 1,296

Runnable TrueCrypt modes: 6
Keyfile sets: 4
Password sources: 2
Estimated TrueCrypt job variants: 48
```

The Password Builder should also show candidate count per password source.

Example:

```text
Password source 1: 60 candidates
Password source 2: 12,000 candidates
```

## UI Behavior

Suggested Password Builder screen:

```text
Password Builder

Target:
  <target name>

Header:
  <header candidate>

Mode set:
  <mode set summary>

PIM set:
  <PIM summary, if applicable>

Keyfile set:
  <keyfile summary, if applicable>

Password source:
  Name: <source name>

Password options:
  [ ] Build from ordered segments
  [ ] Type or paste manual password list
  [ ] Import wordlist into workspace
  [ ] Reference external wordlist

Segment builder:
  Segment list:
    1. <segment name>
    2. <segment name>
    3. <segment name>

Segment variant mode:
  [ ] Exact text
  [ ] Case variants
  [ ] Same characters, unknown order
  [ ] Same characters, unknown order plus case variants
  [ ] Manual variant list
  [ ] Pattern token expansion

Segment filters:
  [ ] Must start with
  [ ] Must not start with
  [ ] Must end with
  [ ] Must not end with
  [ ] Must match pattern
  [ ] Must not match pattern
  [ ] Exclude exact variants

Buttons:
  Add Segment
  Move Segment Up
  Move Segment Down
  Preview Segment Variants
  Preview Candidate Count
  Generate Wordlist
  Review Small Generated List
  Save Password Source
  Clear
  Cancel
```

## Preview Before Saving

The Password Builder should require preview before saving or generating a wordlist.

Preview should include:

```text
selected target
selected header
selected mode set
selected PIM set, if applicable
selected keyfile set, if applicable
password source mode
segment count
segment order
variant count per segment before filters
variant count per segment after filters
candidate count before dedupe
candidate count after dedupe, if known
duplicates removed, if known
sample candidates, limited and optional
output wordlist path
recipe path
warnings
estimated job multiplication
```

## Files Created or Modified

This step may create or modify:

```text
inputs/wordlists/imported/*
inputs/wordlists/manifests/wordlist_<wordlist_id>.json

generated/wordlists/password_list_<password_set_id>.txt
generated/candidates/*
generated/recipes/password_recipe_<password_set_id>.json
generated/recipes/password_source_<password_set_id>.json

jobs/drafts/job_<job_id>.json
jobs/command-previews/password_preview_<job_id>.txt

headers/metadata/header_<header_id>.json
targets/targets.json

logs/app/*
logs/errors/*

cleanup/cleanup-manifest.json
workspace.json
settings.json
```

## Workspace Folders Used

This step uses:

```text
inputs/wordlists/imported/
inputs/wordlists/manifests/
generated/wordlists/
generated/candidates/
generated/recipes/
jobs/drafts/
jobs/command-previews/
headers/metadata/
targets/
logs/app/
logs/errors/
cleanup/
temp/staging/
```

This step must not use:

```text
system temp folders
external folders by default
original volume files
original target files
external wordlists unless explicitly selected
```

## App Behavior

The app should:

```text
load the selected target, header, hash mode set, PIM set, and keyfile set
allow building passwords from ordered segments
allow OR variants inside each segment
preserve segment order
preserve variant order
support exact text variants
support case variants
support same characters with unknown order
support same characters with unknown order and unknown capitalization
support manual variant lists
support pattern token expansion
use ?C as the user-facing any-letter token
avoid exposing ?1 as a user-facing token
allow optional explicit empty variants
ignore blank manual-list lines by default
deduplicate segment variants
apply segment filters before generation when practical
deduplicate final password candidates
preserve first-seen order during duplicate cleanup
show candidate count before generation
show candidate counts before and after filters where practical
warn about large candidate counts
provide candidate review only for small generated lists
save generated wordlists inside generated/wordlists/
save temporary candidate chunks inside the workspace only
save password recipes inside generated/recipes/
allow imported wordlists copied into inputs/wordlists/imported/
allow external wordlist references only as an advanced explicit choice
warn when external wordlists reduce portability and cleanup simplicity
update job draft metadata
show full job multiplication estimates using hash modes, PIMs, keyfiles, and password sources
save immediately after creating or changing a password source
update the cleanup manifest
```

## Safety Rules

The Password Builder must follow these rules:

```text
only support legitimate recovery of user-owned or authorized volumes
do not crack passwords itself
do not run Hashcat
do not modify original VeraCrypt or TrueCrypt volumes
do not use original target files
work only from saved workspace target/header/job metadata
store generated wordlists inside the workspace
store generated candidate chunks inside the workspace
store password recipes inside the workspace
store imported wordlists inside the workspace by default
treat generated passwords, candidate lists, imported wordlists, and password recipes as sensitive recovery data
treat password patterns and recipes as forensic-trail data
do not use system temp folders
do not silently save generated password material outside the workspace
do not upload, transmit, or exfiltrate passwords, candidates, wordlists, headers, metadata, jobs, logs, or results
do not print full password lists in logs, previews, reports, or errors
do not claim secure deletion is guaranteed
describe cleanup as trace centralization and minimization
warn when external wordlists are used
record external wordlist references in the cleanup manifest
```

## Open Questions

Open questions for later steps:

```text
exact hard limit, if any, for generated candidate count
whether very large password plans should be forced into Hashcat mask mode instead of generated wordlists
whether advanced Hashcat mask generation should be added after version 1
whether Hashcat rules should be added as a separate later feature
exact UI layout for showing sample candidates safely
exact line-count strategy for very large imported wordlists
exact final queue job expansion screen behavior
exact report formatting for successful password source details
whether successful reports should show the full recovered password, hide it by default, or require reveal
exact implementation method for translating ?C into Hashcat-compatible custom charset syntax if mask generation is added later
```

## Final Decisions

```text
The Password Builder is Step 9.
The Password Builder handles password source creation only.
The Password Builder must not redesign hash mode selection, PIM handling, keyfile handling, queue running, or reports.
The app must support segment-based password building.
Passwords are built from ordered segments.
Each segment supports OR variants.
Each segment has its own variants.
Final candidates are created by selecting one variant from each segment in order.
Segment order must be preserved.
Variant order must be preserved.
Duplicate cleanup should preserve first-seen order instead of sorting.
The app must support exact text variants.
The app must support case variants.
The app must support same characters with unknown order.
The app must support same characters with unknown order and unknown capitalization.
The app must support manual variant lists.
The app must support pattern token expansion.
The app should use ?C as the user-facing token for any letter.
The app should not expose ?1 as a user-facing token because it can look like ?l depending on font.
The app may translate ?C internally into Hashcat-compatible custom charset syntax later.
Exact text segments can be used as separators.
No special separator system is required for version 1.
The app may support explicit empty variants, but blank lines should be ignored by default.
The app must support segment filters before generation.
Segment filters should include starts-with, does-not-start-with, ends-with, does-not-end-with, contains, does-not-contain, match pattern, does-not-match pattern, allowed exact variants, and excluded exact variants.
Known-invalid candidates should be filtered before generation when practical.
Candidate review is separate from segment filters.
Candidate review happens after generation and is only for small or manageable lists.
Candidate review should allow manual deletion of selected candidates.
Candidate review should encourage the user to return to filters if many candidates are wrong.
The app must show candidate count before generating a wordlist.
The app should show counts before and after filters where practical.
The app must warn about large generated candidate counts.
The app must deduplicate variants inside each segment.
The app must deduplicate final password candidates.
The app must save generated wordlists in generated/wordlists/.
The app must save password recipes in generated/recipes/.
The app may use generated/candidates/ for workspace-local candidate chunks.
The app must not use system temp folders for password data.
The app should support manual typed or pasted password lists.
The app should support imported wordlists.
Imported wordlists should be copied into inputs/wordlists/imported/ by default.
The app may support external wordlist references as an advanced non-portable option.
External wordlist references must be warned about and recorded in the cleanup manifest.
The Password Builder should update job draft metadata.
The Password Builder should show full job multiplication estimates across hash modes, PIMs, keyfiles, and password sources.
The Password Builder should not run Hashcat.
The Password Builder should not create final queued jobs by itself unless a later final job expansion screen is added.
Generated passwords, generated candidates, password recipes, and wordlists are sensitive recovery data.
Password patterns and recipes are forensic-trail data.
All app-created password files must stay inside the workspace by default.
The app must not print full password lists in logs, reports, or errors.
The app must update the cleanup manifest for generated wordlists, candidate chunks, recipes, imported wordlists, and external wordlist references.
```
