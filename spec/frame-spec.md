# The Frame Specification for Organizational Context Artifacts

| | |
|---|---|
| **Document** | `draft-mcandrew-frame-spec-00` |
| **Intended status** | Standards Track |
| **Stream** | IETF (not yet submitted) |
| **Author** | Chuck McAndrew, OpenTeams |
| **Date** | 7 September 2026 |
| **Source** | `spec/frame-spec.md` in this repository (the working draft); `spec/v0.2.md` is the released, normative snapshot |

<a id="abstract"></a>

## Abstract

A Frame is a scoped, text-based artifact that carries the cultural and operational context within which work happens: terminology, rules, goals, style, norms, and process, authored by an organization and loaded as context for AI systems and read by people. This document specifies the Frame data model, the elements a Frame carries and what they mean, the rules by which Frames compose, and three encodings (Markdown, YAML, and JSON) in which a Frame may be written. It defines conformance for both documents and implementations, and it registers media types for the encodings. The Markdown encoding is the existing Frame Spec v0.2 file format; every valid v0.2 Frame is a valid Frame under this specification.

<a id="status-of-this-memo"></a>

## Status of This Memo

This document is written in the structure of an IETF Internet-Draft and is intended for eventual submission to the IETF. It has not been submitted, has no standing in any IETF process, and is a working draft. Its requirements language, section structure, security considerations, and IANA considerations follow Internet-Draft conventions so that submission, when it happens, is a formatting exercise rather than a rewrite. Until then the authoritative copy is the Markdown file named above.

<a id="table-of-contents"></a>

## Table of Contents

- [1. Introduction](#intro)
   - [1.1. Why a Data Model](#why-model)
   - [1.2. Design Principles](#principles)
   - [1.3. Relationship to Frame Spec v0.2](#rel-v02)
- [2. Conventions and Terminology](#conventions)
   - [2.1. Requirements Language](#reqlang)
   - [2.2. Terminology](#terms)
- [3. Data Model](#model)
   - [3.1. Overview](#model-overview)
   - [3.2. Identity](#identity)
   - [3.3. Conformance Model](#conformance-model)
- [4. Elements](#elements)
   - [4.1. How Elements Are Defined](#element-def)
   - [4.2. Required Elements](#required)
      - [4.2.1. identifier](#el-identifier)
      - [4.2.2. guidance](#el-guidance)
   - [4.3. Descriptive Elements](#descriptive)
      - [4.3.1. title](#el-title)
      - [4.3.2. description](#el-description)
      - [4.3.3. version](#el-version)
      - [4.3.4. versionNotes](#el-versionnotes)
      - [4.3.5. status](#el-status)
      - [4.3.6. maintainer](#el-maintainer)
      - [4.3.7. scope](#el-scope)
      - [4.3.8. visibility](#el-visibility)
      - [4.3.9. license](#el-license)
      - [4.3.10. issued](#el-issued)
      - [4.3.11. canonicalSource](#el-canonicalsource)
   - [4.4. Content Refinements](#refinements)
      - [4.4.1. The Dumb-Down Rule](#dumb-down)
      - [4.4.2. Terminology Structured Form](#terminology-form)
   - [4.5. Relations](#relations)
      - [4.5.1. composition](#el-composition)
      - [4.5.2. derivedFrom](#el-derivedfrom)
      - [4.5.3. previousVersion](#el-previousversion)
      - [4.5.4. guards](#el-guards)
   - [4.6. Representation-Level Elements](#representation)
   - [4.7. Extension Elements](#extensions)
   - [4.8. Summary of Elements](#element-summary)
- [5. Composition](#composition)
   - [5.1. Rules](#composition-rules)
   - [5.2. Declared Variation](#declared-variation)
   - [5.3. Reference Syntax](#ref-syntax)
   - [5.4. Session Composition](#session)
   - [5.5. Worked Example](#composition-example)
- [6. Encodings](#encodings)
   - [6.1. Requirements Common to All Encodings](#enc-common)
   - [6.2. Markdown Encoding](#enc-markdown)
      - [6.2.1. Document Structure](#md-structure)
      - [6.2.2. Body Structure](#md-body)
      - [6.2.3. Terminology in Markdown](#md-terminology)
      - [6.2.4. Media Type](#md-mediatype)
      - [6.2.5. Example](#md-example)
   - [6.3. YAML Encoding](#enc-yaml)
   - [6.4. JSON Encoding](#enc-json)
- [7. Conformance Profiles](#profiles)
- [8. Implementation Status](#impl-status)
- [9. Security Considerations](#security)
   - [9.1. Threat Model](#threat-model)
   - [9.2. Instruction Injection](#injection)
   - [9.3. Composition Extends Trust](#trust-composition)
   - [9.4. Identity Is a Claim](#identity-claim)
   - [9.5. Visibility Is Not Access Control](#visibility-security)
   - [9.6. Unknown Elements](#unknown-security)
   - [9.7. Resource Exhaustion](#resources)
   - [9.8. Guards Are Declared, Not Enforced](#guards-security)
   - [9.9. Residual Risk](#residual)
- [10. IANA Considerations](#iana)
   - [10.1. Media Type Registrations](#iana-media)
      - [10.1.1. application/frame+json](#iana-json)
      - [10.1.2. application/frame+yaml](#iana-yaml)
      - [10.1.3. Markdown Variant "frame"](#iana-markdown-variant)
   - [10.2. Frame Element Names Registry](#iana-elements)
   - [10.3. Frame Status Values Registry](#iana-status)
   - [10.4. Frame Visibility Values Registry](#iana-visibility)
   - [10.5. Frame Refinements Registry](#iana-refinements)
- [11. References](#references)
   - [11.1. Normative References](#normative-references)
   - [11.2. Informative References](#informative-references)
- [Appendix A. Relationship to Other Vocabularies](#crosswalk)
- [Appendix B. Machine-Readable Profile](#dctap)
- [Appendix C. Conformance Profile Template](#profile-template)
- [Appendix D. Changes from Frame Spec v0.2](#changes)
- [Acknowledgements](#acknowledgements)
- [Author's Address](#authors-address)

<a id="intro"></a>

## 1. Introduction

Organizations accumulate implicit context: brand voice, technical terminology, regulatory constraints, departmental conventions, team norms, project goals. When AI systems are put to work without that context, the organization must re-explain itself in every interaction. A Frame makes that context explicit and portable. The Intelligence Hub whitepaper [[INTHUB]](#ref-INTHUB) defines a Frame as "a scoped, text-based artifact" that carries "the cultural and operational context within which work happens", and describes Frames as "first-class artifacts: they live independently of Cogs and Ops and can be authored, discovered, exchanged, and inherited on their own."

Two things follow from that definition and motivate this document. First, a Frame is exchanged: between people, between tools, between organizations. Second, a Frame is loaded as context for an AI system, so what it means, how several Frames combine, and who stands behind one are questions with operational consequences.

<a id="why-model"></a>

### 1.1. Why a Data Model

Frame Spec v0.2 [[FRAME-V02]](#ref-FRAME-V02) defines a Frame as a Markdown file whose YAML front matter carries four required fields, with a free-form body. That definition has served early adoption well, and it is preserved here in full as the Markdown encoding ([Section 6.2](#enc-markdown)). It is, however, a definition of a file layout rather than of a Frame. A registry that stores Frames as database rows, a desktop application that holds them in memory, and a Markdown file on disk all hold Frames, and a specification predicated on files cannot say what they have in common.

This document therefore specifies the Frame itself, independent of any encoding, and then specifies encodings as bindings of that model. The approach follows the separation between an abstract artifact and its distributions in the W3C Data Catalog Vocabulary [[DCAT3]](#ref-DCAT3), and the separation between a domain model, an element set, and encoding syntax guidelines in the Singapore Framework for application profiles [[SINGAPORE]](#ref-SINGAPORE). Where an element of the model corresponds to a term already defined by an established vocabulary, this document says so ([Appendix A](#crosswalk)) rather than defining a new meaning.

<a id="principles"></a>

### 1.2. Design Principles

Four principles shape the specification.

- **Minimum obligation:** Only what is required for two independent systems to exchange a Frame is mandatory: which Frame this is, and what it says. Everything else is optional in the model, with obligation declared by encodings and by implementation profiles ([Section 7](#profiles)). This follows the guidance of [[RFC2119]](#ref-RFC2119), Section 6, that requirement keywords are to be used "only where it is actually required for interoperation".
- **Graceful degradation:** A Frame's content is free-form text that may optionally be structured into labeled sections. A reader that does not understand a section MUST treat its content as ordinary guidance and MUST NOT discard it ([Section 4.4.1](#dumb-down)). A minimal Frame and a richly structured Frame are therefore the same kind of object, read at two levels of detail.
- **Borrowed meaning:** Where an element means the same thing as a term in [[DCTERMS]](#ref-DCTERMS), [[SCHEMA-ORG]](#ref-SCHEMA-ORG), [[PROV-O]](#ref-PROV-O), [[SKOS]](#ref-SKOS), [[DCAT3]](#ref-DCAT3), or [[ADMS]](#ref-ADMS), the element is defined by reference to that term. One relation, composition, has no equivalent in any established vocabulary and is defined here.
- **Declared variation:** Implementations differ in what they resolve and how they merge. Rather than forbid variation this specification cannot enforce, it requires each implementation to publish a conformance profile stating its behavior ([Section 7](#profiles)), so that authors can know how a layered set of Frames will behave in a given tool.

<a id="rel-v02"></a>

### 1.3. Relationship to Frame Spec v0.2

Frame Spec v0.2 [[FRAME-V02]](#ref-FRAME-V02) is not amended. Its file format is the Markdown encoding of this specification, and its four required front matter fields remain required in that encoding. Every document that conforms to v0.2 conforms to this specification, and a Markdown document conforming to this specification passes the v0.2 reference validator. [Appendix D](#changes) lists what this document adds.

<a id="conventions"></a>

## 2. Conventions and Terminology

<a id="reqlang"></a>

### 2.1. Requirements Language

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "NOT RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in BCP 14 [[RFC2119]](#ref-RFC2119) [[RFC8174]](#ref-RFC8174) when, and only when, they appear in all capitals, as shown here.

<a id="terms"></a>

### 2.2. Terminology

- **Frame:** The abstract artifact this document specifies: a scoped, text-based carrier of organizational context, identified independently of any particular version or encoding.
- **Frame Version:** A specific revision of a Frame. A Frame Version carries the Frame's content.
- **Representation:** A serialization of a Frame Version in one encoding. The same Frame Version may have Markdown, YAML, and JSON Representations.
- **Element:** A named property of a Frame or Frame Version, defined in [Section 4](#elements).
- **Refinement:** An element that narrows the general content element, `guidance`, to a named kind of content, such as `rules` or `terminology` ([Section 4.4](#refinements)).
- **Composition:** The relation by which one Frame's content combines with another's when the first is activated, with the declaring Frame taking precedence ([Section 5](#composition)).
- **Reader:** An implementation that parses a Representation into the Frame model. A reader may also resolve composition.
- **Writer:** An implementation that produces a Representation from the Frame model.
- **Registry:** An implementation that stores Frames, assigns or records their identifiers, and serves Representations to readers.
- **Conformance profile:** A published statement of the choices an implementation makes among the behaviors this specification leaves optional ([Section 7](#profiles)).
- **Guard:** A validation component that checks the output of AI work, as described in [[INTHUB]](#ref-INTHUB), Section 5. This document defines only how a Frame refers to a Guard, not what a Guard is.
- **Cog, Op:** An AI worker and an orchestrated workflow respectively, as described in [[INTHUB]](#ref-INTHUB), Sections 4.4 and 4.5. Cogs and Ops consume Frames; this document defines the reference form they use to name one ([Section 5.3](#ref-syntax)).

<a id="model"></a>

## 3. Data Model

<a id="model-overview"></a>

### 3.1. Overview

The model has three entities and a small set of relations, shaped on the distinction in [[DCAT3]](#ref-DCAT3) between a dataset and its distributions.

```
Frame                 the abstract artifact; persists across versions
  identifier, title, description, maintainer, scope,
  visibility, license, canonicalSource
  |
  +-- derivedFrom          (relation) adapted or forked from that Frame
  |
  +-- Frame Version        a revision
        version, status, versionNotes, issued,
        guidance and its refinements
        |
        +-- composition    (relation) ordered references to other
        |                  Frames; the declaring Frame has precedence
        +-- guards         (relation) Guards to run on output
        |
        +-- Representation a serialization of this version
              mediaType, checksum, byteSize
```

*Figure 1: The Frame data model*

A Frame persists across its versions and carries the elements that identify and describe it, and its lineage (`derivedFrom`). A Frame Version carries the content, the elements that describe a revision, and the relations that can differ between revisions (`composition`, `guards`). A Representation is one encoding of one version and carries the elements that describe bytes. In a single document the Frame-level and version-level elements appear together; the distinction matters to registries, which MAY treat Frame-level elements as shared across versions, and to consumers that must name a version unambiguously, which is done by `identifier` together with `version` and, where bytes matter, a Representation's `checksum`.

<a id="identity"></a>

### 3.2. Identity

Every Frame has exactly one `identifier`. It identifies the Frame, not a version of it and not a Representation of it. An identifier is a claim made by the Frame about itself; it is not an authentication of that claim ([Section 9](#security)).

When a Frame is read from a location and carries no explicit `identifier`, the identifier is the retrieval location, as specified by each encoding ([Section 6.1](#enc-common)). This is how [[RO-CRATE]](#ref-RO-CRATE) and [[AGENTS-MD]](#ref-AGENTS-MD) identify their artifacts, and it means a Frame exchanged as a bare file always has an identifier.

Two rules govern changes to an identifier and are normative for readers and registries:

1. A reader or registry that assigns an identifier to a Frame that arrived without one MUST NOT present that identifier as a claim the Frame made about itself.
2. A reader or registry that changes a Frame's identifier MUST record the prior identifier in `derivedFrom`.

The second rule makes every fork visible. A Frame carrying `identifier: acme/brand-voice` that is imported into another organization's registry and stored as `contoso/brand-voice` MUST carry `derivedFrom: acme/brand-voice`. How a registry derives a new identifier is a profile concern ([Section 7](#profiles)), not a model one.

A distribution mechanism may assign its own artifact identity at the envelope layer, as a package manager or content-addressed store does. Such an identity is distinct from the Frame's `identifier`. A distribution mechanism SHOULD record the Frame's `identifier` alongside its own and is bound by the rules above if it changes the Frame-level identifier. The `canonicalSource` element is where a Frame may point at its authoritative envelope location.

<a id="conformance-model"></a>

### 3.3. Conformance Model

Conformance is defined at two levels.

A *document* conforms to an encoding of this specification if it satisfies that encoding's requirements ([Section 6](#encodings)). A document does not conform to "the Frame Specification" in the abstract; it conforms to the Markdown, YAML, or JSON encoding. The registered value vocabularies of [Section 4](#elements) are RECOMMENDED for documents; a value that is not registered does not make a document non-conformant, and readers preserve it.

An *implementation* conforms to this specification if it satisfies the requirements of [Section 4](#elements), [Section 5](#composition), and [Section 3.2](#identity) for the encodings it supports, and publishes a conformance profile ([Section 7](#profiles)) declaring its choices among the behaviors this specification leaves optional.

<a id="elements"></a>

## 4. Elements

<a id="element-def"></a>

### 4.1. How Elements Are Defined

Each element is defined by a name, a label, a definition, an obligation, whether it is repeatable, the vocabulary term it corresponds to, and a comment. This follows the definition-and-comment convention of [[DCTERMS]](#ref-DCTERMS). Obligation uses the keywords of [Section 2.1](#reqlang) and applies at the model layer; encodings and profiles MAY require an element that the model leaves optional, and MUST NOT make a mandatory element optional.

An element's correspondence to an established term is stated as "maps to". Where the correspondence is exact, the element means what the term means. Where it is partial, this is stated. Where no term exists, the element is marked Frame-native and the reason is given. Per [[DCAP]](#ref-DCAP), a profile "may add technical constraints on use of properties (such as repeatability), or provide more narrow interpretations of definitions for particular purposes, but they should not contradict the meaning of the properties intended by their maintainers"; the same rule binds this document's use of borrowed terms and binds implementation profiles' use of the elements defined here.

Element names are given in lower camel case. Encodings state how names are spelled in each syntax.

<a id="required"></a>

### 4.2. Required Elements

Exactly two elements are mandatory at the model layer.

<a id="el-identifier"></a>

#### 4.2.1. identifier

- **Label:** Identifier
- **Definition:** An unambiguous reference to the Frame within a given context.
- **Obligation:** MUST
- **Repeatable:** No
- **Maps to:** `dcterms:identifier` [[DCTERMS]](#ref-DCTERMS)
- **Comment:** Identifies the Frame across its versions and copies; it is not the version's identity. The value SHOULD be either a URI [[RFC3986]](#ref-RFC3986) or a `qualified-ref` as defined in [Section 5.3](#ref-syntax). The value SHOULD NOT contain the character "@", which [Section 5.3](#ref-syntax) uses to separate a version from a reference. When absent from a document, the identifier is the retrieval location ([Section 6.1](#enc-common)). See [Section 3.2](#identity).

<a id="el-guidance"></a>

#### 4.2.2. guidance

- **Label:** Guidance
- **Definition:** Context that orients work performed within the Frame's scope.
- **Obligation:** MUST be present; MAY be empty
- **Repeatable:** Yes
- **Maps to:** Frame-native. The nearest terms, `schema:text` and `dcterms:description`, describe a resource rather than orient work, so neither is claimed as equivalent.
- **Comment:** The body of the Frame. Its value is text intended to be read by people and loaded as context for AI systems. It MAY be empty because Frame Spec v0.2 never required body content; presence is structural, since every encoding has a content position. A Frame with empty guidance is valid and carries nothing. In a single document `guidance` has one value; it is repeatable because composition ([Section 5](#composition)) combines the guidance of several Frames.

<a id="descriptive"></a>

### 4.3. Descriptive Elements

The following elements describe the Frame or a version of it. None is mandatory at the model layer.

<a id="el-title"></a>

#### 4.3.1. title

- **Label:** Title
- **Definition:** A name given to the Frame.
- **Obligation:** SHOULD
- **Repeatable:** No
- **Maps to:** `dcterms:title` [[DCTERMS]](#ref-DCTERMS); `schema:name` [[SCHEMA-ORG]](#ref-SCHEMA-ORG)
- **Comment:** A short human-readable name, such as "Editorial Style Guide". Implementations MUST NOT constrain `title` to an identifier syntax such as a slug; constraining it to such a syntax contradicts the term's meaning rather than narrowing it. Systems that need a stable key use `identifier`.

<a id="el-description"></a>

#### 4.3.2. description

- **Label:** Description
- **Definition:** An account of the Frame: what it is for and when it should be used.
- **Obligation:** SHOULD
- **Repeatable:** No
- **Maps to:** `dcterms:description` [[DCTERMS]](#ref-DCTERMS); `schema:abstract` [[SCHEMA-ORG]](#ref-SCHEMA-ORG)
- **Comment:** One or two sentences are RECOMMENDED. This specification imposes no length limit.

<a id="el-version"></a>

#### 4.3.3. version

- **Label:** Version
- **Definition:** The revision of the Frame that this Frame Version represents.
- **Obligation:** SHOULD
- **Repeatable:** No
- **Maps to:** `dcat:version` [[DCAT3]](#ref-DCAT3); `schema:version` [[SCHEMA-ORG]](#ref-SCHEMA-ORG)
- **Comment:** Tracks the Frame's own revision history, not the version of this specification. Semantic Versioning [[SEMVER]](#ref-SEMVER) is RECOMMENDED. Registries SHOULD require `version` on publication even though the model does not require it on exchange.

<a id="el-versionnotes"></a>

#### 4.3.4. versionNotes

- **Label:** Version Notes
- **Definition:** A description of the changes between this Frame Version and the previous one.
- **Obligation:** MAY
- **Repeatable:** Yes
- **Maps to:** `adms:versionNotes` [[ADMS]](#ref-ADMS)
- **Comment:** What a changelog entry carries.

<a id="el-status"></a>

#### 4.3.5. status

- **Label:** Status
- **Definition:** The stage of this Frame Version in its lifecycle.
- **Obligation:** MAY
- **Repeatable:** No
- **Maps to:** `schema:creativeWorkStatus` [[SCHEMA-ORG]](#ref-SCHEMA-ORG)
- **Comment:** The value SHOULD be one of the values in the Frame Status Values registry ([Section 10.3](#iana-status)); the initial values are `draft`, `review`, `approved`, `deprecated`, and `revoked`. A reader MUST preserve a value that is not registered and MUST NOT reject a Frame for carrying one; it MAY warn. Frame Spec v0.2 did not define this element, and Frames written to it carry values such as `stable` that predate the registry. Readers MUST NOT treat registered values as interchangeable.

<a id="el-maintainer"></a>

#### 4.3.6. maintainer

- **Label:** Maintainer
- **Definition:** The person, team, or organization that manages contributions to, and publication of, the Frame, and is accountable for it.
- **Obligation:** SHOULD
- **Repeatable:** Yes
- **Maps to:** `schema:maintainer` [[SCHEMA-ORG]](#ref-SCHEMA-ORG); secondarily `schema:accountablePerson` (partial: that term's range is a person only, and a maintainer may be a team)
- **Comment:** [[INTHUB]](#ref-INTHUB) requires that each Frame be "owned by and accountable to a human or a group of humans that intentionally manage it." The maintainer is that party. This element declares accountability; enforcing it is a registry concern outside this specification.

<a id="el-scope"></a>

#### 4.3.7. scope

- **Label:** Scope
- **Definition:** A statement of where the Frame applies.
- **Obligation:** MAY
- **Repeatable:** No
- **Maps to:** `dcterms:audience` [[DCTERMS]](#ref-DCTERMS) (partial)
- **Comment:** Typical values name an organizational level or relationship: `company`, `department`, `team`, `project`, `role`, `partner`, `personal`. No grammar is imposed. The mapping to `dcterms:audience` is partial; scope describes applicability rather than an intended audience, and no established term matches exactly.

<a id="el-visibility"></a>

#### 4.3.8. visibility

- **Label:** Visibility
- **Definition:** The sharing boundary the maintainer declares for the Frame.
- **Obligation:** MAY
- **Repeatable:** No
- **Maps to:** `dcterms:accessRights` [[DCTERMS]](#ref-DCTERMS); `schema:conditionsOfAccess` [[SCHEMA-ORG]](#ref-SCHEMA-ORG)
- **Comment:** The value SHOULD be one of the values in the Frame Visibility Values registry ([Section 10.4](#iana-visibility)); the initial values are `private`, `internal`, `shared`, and `public`, which Frame Spec v0.2 listed as suggested values. A reader MUST preserve a value that is not registered and MUST NOT reject a Frame for carrying one; it MAY warn. Visibility is declared intent and travels with the Frame. It is not an access control, and readers MUST NOT treat it as one; who may read a Frame is decided by the system that holds it. See [Section 9](#security).

<a id="el-license"></a>

#### 4.3.9. license

- **Label:** License
- **Definition:** A legal document giving official permission to do something with the Frame.
- **Obligation:** MAY
- **Repeatable:** No
- **Maps to:** `dcterms:license` [[DCTERMS]](#ref-DCTERMS)
- **Comment:** A URI or an SPDX license identifier [[SPDX]](#ref-SPDX) is RECOMMENDED. Cross-organization exchange, which [[INTHUB]](#ref-INTHUB) anticipates for "the vast majority of Frames", depends on this being stated.

<a id="el-issued"></a>

#### 4.3.10. issued

- **Label:** Issued
- **Definition:** The date of formal issuance of this Frame Version.
- **Obligation:** MAY
- **Repeatable:** No
- **Maps to:** `dcterms:issued` [[DCTERMS]](#ref-DCTERMS)
- **Comment:** The value MUST be a date or date-time in the format of [[RFC3339]](#ref-RFC3339).

<a id="el-canonicalsource"></a>

#### 4.3.11. canonicalSource

- **Label:** Canonical Source
- **Definition:** The authoritative location of the Frame.
- **Obligation:** MAY
- **Repeatable:** No
- **Maps to:** `schema:sameAs` [[SCHEMA-ORG]](#ref-SCHEMA-ORG); secondarily `prov:specializationOf` [[PROV-O]](#ref-PROV-O) for a local copy that specializes the canonical Frame
- **Comment:** A URI. Disambiguates identifiers that are unique only within one registry, and lets a copy point at the place its updates come from. A registry SHOULD emit `canonicalSource` when more than one registry may hold Frames with the same `identifier`.

<a id="refinements"></a>

### 4.4. Content Refinements

The content of a Frame is its `guidance`. Ten optional elements refine `guidance` to a named kind of content. Each refinement is a subproperty of `guidance` in the sense of [[DCTERMS]](#ref-DCTERMS): a value of a refinement is also a value of `guidance`.

All ten are defined with obligation MAY and repeatable Yes. Their definitions are those of [[INTHUB]](#ref-INTHUB), Section 4.3, which lists them as what a Frame carries.

- **rules** (Rules): What is and is not acceptable behavior within the scope.
- **terminology** (Terminology): The words, names, and definitions specific to the organization, function, or project. See [Section 4.4.2](#terminology-form).
- **goals** (Goals): What success looks like; what outcomes are valued.
- **style** (Style): Tone of voice, formatting conventions, brand expression.
- **norms** (Norms): Implicit expectations about how work gets done.
- **skills** (Skills): Named capabilities the work depends on.
- **toolSpecs** (Tool Specifications): Specifications of the tools the Frame expects to be available. Comment: [[INTHUB]](#ref-INTHUB) describes these as "Nebi (or similar) spec files", so values are typically references to environment specifications rather than prose.
- **prompts** (Prompts): Reusable prompt fragments to be loaded into an AI worker's context.
- **architecture** (Architecture): Relevant software and system context that orients the work.
- **businessProcess** (Business Process): The procedural backbone that the work follows.

Every refinement's value is content, exactly as `guidance` is. A refinement MAY additionally define a structured form that a reader MAY extract; `terminology` defines one ([Section 4.4.2](#terminology-form)).

<a id="dumb-down"></a>

#### 4.4.1. The Dumb-Down Rule

The following rule is normative and is the mechanism by which a Frame with no refinements and a Frame with all ten are the same kind of object.

A reader that does not implement a refinement MUST treat its value as `guidance`. It MUST NOT discard the value.

A reader that implements a refinement but cannot extract the refinement's structured form from a value MUST keep the value as that refinement's content. It MUST NOT reject the Frame and MUST NOT demote the value to `guidance` on that account.

This is the dumb-down principle of [[DC-USAGE]](#ref-DC-USAGE): "A client should be able to ignore any qualifier and use the value as if it were unqualified." Its consequence is that a reader which knows only `guidance` sees a plain body, a reader which knows the refinements sees typed sections, and no content is lost in either case.

<a id="terminology-form"></a>

#### 4.4.2. Terminology Structured Form

A value of `terminology` MAY be structured as a set of concepts, each with a preferred label and a definition, and optionally alternative labels. Each such concept is a `skos:Concept` [[SKOS]](#ref-SKOS); the preferred label is its `skos:prefLabel`, the definition its `skos:definition`, and each alternative label a `skos:altLabel`. Encodings state how the structured form is written ([Section 6](#encodings)).

Content under `terminology` that does not fit the structured form is unstructured `terminology` content and is governed by [Section 4.4.1](#dumb-down). Three of the example Frames published with [[FRAME-V02]](#ref-FRAME-V02) carry a Terminology section whose entries are usage preferences rather than definitions; under this specification they are valid.

<a id="relations"></a>

### 4.5. Relations

Four elements relate a Frame to other artifacts.

<a id="el-composition"></a>

#### 4.5.1. composition

- **Label:** Composition
- **Definition:** A Frame whose content combines with this Frame's content when this Frame is activated, with this Frame taking precedence.
- **Obligation:** MAY
- **Repeatable:** Yes; the order of values is significant
- **Maps to:** Frame-native. See below.
- **Comment:** The value is a reference as defined in [Section 5.3](#ref-syntax). The rules governing composition are in [Section 5](#composition). No established vocabulary term means "combines with at activation": `schema:isBasedOn` and `prov:wasDerivedFrom` mean that one artifact was made from another, which is derivation and is expressed by `derivedFrom`. Mapping composition to a derivation term would contradict that term's meaning. The Markdown encoding spells this element `inherits` for compatibility with [[FRAME-V02]](#ref-FRAME-V02).

<a id="el-derivedfrom"></a>

#### 4.5.2. derivedFrom

- **Label:** Derived From
- **Definition:** A Frame from which this Frame was adapted, forked, or otherwise derived.
- **Obligation:** MAY; MUST be present when [Section 3.2](#identity) requires it
- **Repeatable:** Yes
- **Maps to:** `prov:wasDerivedFrom` [[PROV-O]](#ref-PROV-O); `prov:hadPrimarySource` where the source was authoritative
- **Comment:** Records lineage. Distinct from `composition`, which is a relation at activation time, and from `previousVersion`, which is a relation between versions of one Frame.

<a id="el-previousversion"></a>

#### 4.5.3. previousVersion

- **Label:** Previous Version
- **Definition:** The Frame Version that this Frame Version revises.
- **Obligation:** MAY
- **Repeatable:** No
- **Maps to:** `dcat:previousVersion` [[DCAT3]](#ref-DCAT3); `prov:wasRevisionOf` [[PROV-O]](#ref-PROV-O)
- **Comment:** Version lineage. A registry that tracks versions SHOULD populate this.

<a id="el-guards"></a>

#### 4.5.4. guards

- **Label:** Guards
- **Definition:** A Guard that must be run on output produced under this Frame.
- **Obligation:** MAY
- **Repeatable:** Yes
- **Maps to:** `dcterms:requires` [[DCTERMS]](#ref-DCTERMS): "a related resource that is required by the described resource to support its function, delivery, or coherence"
- **Comment:** The value is a reference as defined in [Section 5.3](#ref-syntax). [[INTHUB]](#ref-INTHUB) lists Output Guards among what a Frame carries and states that "one of the critical things that Frames can do is define a Validation or Verification tool (a Guard) that must be called and pass on the output of the system." This element is a relation rather than a refinement of `guidance` because a Guard is run on output, not read as context; under [Section 4.4.1](#dumb-down) a refinement would degrade to prose loaded into a model, which is the wrong failure mode for a validation requirement. What a Guard is, how it is run, and how the reference resolves are outside this specification. Unlike the other relations, `guards` participates in composition ([Section 5](#composition), rule 5).

<a id="representation"></a>

### 4.6. Representation-Level Elements

Three elements describe a Representation and appear only in encoding metadata and registries, never in a Frame's content.

- **mediaType:** The media type of the Representation. Maps to `dcat:mediaType` [[DCAT3]](#ref-DCAT3). The values for the encodings defined here are registered in [Section 10](#iana).
- **checksum:** A digest of the Representation's bytes, with its algorithm. Maps to `spdx:checksum` [[SPDX]](#ref-SPDX). SHA-256 is RECOMMENDED.
- **byteSize:** The size of the Representation in bytes. Maps to `dcat:byteSize` [[DCAT3]](#ref-DCAT3).

<a id="extensions"></a>

### 4.7. Extension Elements

An element name beginning with `x-` is an extension element and is reserved for implementation-specific use. Extension names are never registered ([Section 10.2](#iana-elements)).

Readers MUST preserve elements they do not recognize, including extension elements, and MUST NOT reject a Frame for carrying them. Writers MUST emit preserved unknown elements when producing a Representation, so that round trips through a reader that does not understand an element are lossless.

Unknown elements are metadata, not content. A reader MUST NOT present the value of an unrecognized element to an AI system as guidance. See [Section 9](#security).

<a id="element-summary"></a>

### 4.8. Summary of Elements

| Element | Obligation | Repeatable | Level |
|---|---|---|---|
| identifier | MUST | no | Frame |
| guidance | MUST (may be empty) | yes | Version |
| title | SHOULD | no | Frame |
| description | SHOULD | no | Frame |
| version | SHOULD | no | Version |
| versionNotes | MAY | yes | Version |
| status | MAY | no | Version |
| maintainer | SHOULD | yes | Frame |
| scope | MAY | no | Frame |
| visibility | MAY | no | Frame |
| license | MAY | no | Frame |
| issued | MAY | no | Version |
| canonicalSource | MAY | no | Frame |
| rules, terminology, goals, style, norms, skills, toolSpecs, prompts, architecture, businessProcess | MAY | yes | Version |
| composition | MAY | yes, ordered | Version |
| derivedFrom | MAY | yes | Frame |
| previousVersion | MAY | no | Version |
| guards | MAY | yes | Version |
| mediaType, checksum, byteSize | per encoding | no | Representation |

*Table 1: Elements at a glance*

Twenty-seven elements are defined at the Frame and Frame Version levels, of which two are mandatory, ten are refinements, and fifteen are optional descriptive and relational elements. Three are defined at the Representation level.

<a id="composition"></a>

## 5. Composition

Composition is the relation by which several Frames become one body of context. It arises in two ways: a Frame declares it through the `composition` element, or a user or application activates several Frames together for a work session. [[INTHUB]](#ref-INTHUB) names the second case as a distinct property: "Multiple Frames can be combined for a given work session." The rules below govern both.

<a id="composition-rules"></a>

### 5.1. Rules

1. Composition is explicit. A Frame composes only what it declares, and a session composes only what was activated.
2. Composition is ordered. Among the values of `composition`, earlier entries have lower precedence than later entries. Among Frames activated in a session, the order of activation is the order of precedence, with the most recently activated Frame highest.
3. The declaring Frame has the highest precedence. Where a Frame's own content conflicts with the content of a Frame it composes, the declaring Frame's content wins.
4. Transitive resolution is OPTIONAL. If A composes B and B composes C, an implementation MAY resolve C when activating A, but is not required to. An implementation MUST declare in its conformance profile whether it resolves composition transitively.
5. Only content elements and `guards` compose. The values of `guidance` and its refinements combine according to rule 6. The values of `guards` accumulate: a Guard declared by any Frame in the composed set applies to the result. The elements that describe the Frame itself (`identifier`, `title`, `description`, `version`, `versionNotes`, `status`, `maintainer`, `scope`, `visibility`, `license`, `issued`, `canonicalSource`, `derivedFrom`, `previousVersion`) MUST NOT be inherited from a composed Frame.
6. Resolution follows repeatability. For a repeatable content element, composition concatenates the values of all composed Frames in order of increasing precedence. For a content element that a profile declares non-repeatable, the value of the highest-precedence Frame in which the element is present replaces all others.
7. A reader that resolves composition and encounters a reference it cannot resolve MUST NOT silently ignore it; it MUST either fail or report the unresolved reference. A reader that resolves no composition MUST declare so in its conformance profile and SHOULD surface the presence of unresolved composition to the user.
8. A reader that resolves composition MUST detect cycles and MUST NOT loop.
9. Reference syntax is classified, not enforced. A reader classifies each reference according to [Section 5.3](#ref-syntax) and declares in its conformance profile which forms it resolves. Reference syntax is never grounds for rejecting a Frame.

Rules 1 through 4 are those of [[FRAME-V02]](#ref-FRAME-V02), carried over unchanged except that rule 4 now requires the declaration it previously recommended.

Rule 5 exists for two reasons. For the descriptive elements, a Frame that omits `description` must not silently acquire its parent's; a Frame's description is its own. For `guards`, the reverse holds: a Guard attached by a composed Frame must not be silently dropped by a Frame that does not mention it. [[INTHUB]](#ref-INTHUB) gives the motivating case, a compliance Frame "pointing to a Guard that must be run after every output"; if a child could remove that Guard by omission, the compliance Frame would not do what it exists to do. Excluding a Frame from the composed set entirely removes its Guards along with its content.

Rule 6 makes merge behavior a consequence of the element definitions rather than a separate specification. Two narrowings of rule 6 are permitted to profiles and MUST be declared: deduplication of identical values within a repeatable element, and replacement by key within a repeatable element whose values carry a natural key. The `terminology` element is the standing example of the second: [[SKOS]](#ref-SKOS) permits at most one preferred label per language within a concept scheme, so a composed Frame's definition of a term replaces a lower-precedence Frame's definition of the same term. A profile MUST NOT drop non-identical values under either narrowing.

Rule 7's second sentence exists so that rule 4 and rule 7 do not conflict. An implementation that silently ignores `composition` does not conform; the same implementation that declares "resolves no composition" in its profile does.

<a id="declared-variation"></a>

### 5.2. Declared Variation

[[INTHUB]](#ref-INTHUB), Section 8.1, asks that "a Frame inherited by one Cog will be interpreted the same way by another." This specification guarantees identical interpretation of content, since [Section 4.4.1](#dumb-down) forbids content loss, and identical precedence. It permits declared variation in resolution depth (rule 4) and in merge narrowing (rule 6). Full uniformity would require making transitive resolution mandatory, which [[FRAME-V02]](#ref-FRAME-V02) chose not to do and which at least one implementation does not perform [[FRAME-SPEC-21]](#ref-FRAME-SPEC-21). The tradeoff is stated rather than hidden: an author who needs identical behavior across tools consults their conformance profiles, which exist so that the variation is visible.

<a id="ref-syntax"></a>

### 5.3. Reference Syntax

The values of `composition`, `guards`, and `derivedFrom` are references. This specification defines a grammar that classifies a reference by form. It does not define how any form is resolved; that is the concern of the implementation that holds the referenced artifact, and each implementation declares which forms it resolves.

```abnf
frame-ref     = pinned-ref / qualified-ref / uri-ref
              / path-ref / name-ref

pinned-ref    = qualified-ref "@" version
qualified-ref = publisher "/" frame-name
publisher     = 1*ref-char
frame-name    = 1*ref-char
ref-char      = ALPHA / DIGIT / "-" / "_" / "."
version       = 1*VCHAR          ; Semantic Versioning RECOMMENDED

uri-ref       = URI              ; <URI, see [RFC3986], Section 3>
path-ref      = ( "./" / "../" / "/" ) 1*VCHAR
name-ref      = VCHAR *( VCHAR / SP )
```

*Figure 2: Reference syntax (ABNF, RFC 5234)*

The core rules ALPHA, DIGIT, SP, and VCHAR are those of [[RFC5234]](#ref-RFC5234), Appendix B.

A reader classifies a reference by trying the alternatives in the order listed and taking the first that matches. Because `name-ref` matches any non-empty string of visible characters and spaces, every reference is at least a `name-ref`; the grammar never fails. In a `pinned-ref`, the last "@" in the string separates the version from the qualified reference. Encodings trim leading and trailing white space from a reference before classification.

The forms have the following intended meanings.

- **pinned-ref:** A Frame identified by publisher and name, at a specific version. `acme/brand-voice@1.2.0`.
- **qualified-ref:** A Frame identified by publisher and name, at whatever version the resolver selects. `acme/brand-voice`.
- **uri-ref:** A Frame at a URI. `https://frames.example.com/acme/brand-voice`.
- **path-ref:** A Frame at a filesystem path relative to the referring document or absolute. `./company-core.frame.md`.
- **name-ref:** A Frame identified by a name the resolver knows how to look up. `company-core`, `Company Core`.

This grammar is also the form in which a Cog or Op manifest names the Frames it depends on. [[INTHUB]](#ref-INTHUB), Section 5.6, shows an Op manifest with a `frames` block; this is the syntax of its entries.

<a id="session"></a>

### 5.4. Session Composition

When an application combines Frames that do not declare each other, as when a user activates a company Frame, a department Frame, and a project Frame together, rules 2, 3, 5, and 6 apply with the activation order as the precedence order. The application is the reader for the purposes of rules 7 through 9. The result is that the layering a desktop application performs at runtime and the resolution a registry performs from declared composition are governed by the same rules and produce comparable results.

<a id="composition-example"></a>

### 5.5. Worked Example

Three Frames: `acme/company-core`, composed by `acme/brand-voice`, composed by `acme/q4-playbook`. Each carries `rules` (repeatable), `style` (repeatable at the model layer), a `description`, and the first carries a `guards` reference.

```
acme/company-core            (lowest precedence)
  description: Company-wide context.
  rules:       [cite sources]
  style:       formal
  guards:      [acme/pii-guard]

acme/brand-voice             composes acme/company-core
  description: How we sound.
  rules:       [no hype]
  style:       plain

acme/q4-playbook             composes acme/brand-voice (highest)
  description: (absent)
  rules:       [lead with impact]
  style:       (absent)
```

*Figure 3: Three Frames before composition*

Resolved at the model layer, where every content element is repeatable:

```
description: (absent)             rule 5: not inherited
rules: [cite sources, no hype, lead with impact]
                                  rule 6: concatenated, low to high
style: [formal, plain]            rule 6: concatenated
guards: [acme/pii-guard]          rule 5: accumulated
```

*Figure 4: Result at the model layer*

Resolved under a profile that declares `style` non-repeatable:

```
description: (absent)
rules: [cite sources, no hype, lead with impact]
style: plain                      rule 6: highest present value wins
guards: [acme/pii-guard]
```

*Figure 5: Result under a profile narrowing style*

Both results conform. They differ because one profile narrowed a repeatable element, and the profile must say so.

<a id="encodings"></a>

## 6. Encodings

An encoding is a binding of the model to a syntax. This document defines three. A document conforms to exactly the encoding it is written in.

<a id="enc-common"></a>

### 6.1. Requirements Common to All Encodings

- **Identifier default:** A document with no explicit `identifier` is identified by the location it was retrieved from, expressed as a URI where one exists. A document exchanged without a location (for example, pasted into a message) has no identifier until a reader or registry assigns one, at which point [Section 3.2](#identity) applies.
- **Unknown elements:** A reader MUST preserve, and a writer MUST emit, elements the implementation does not recognize ([Section 4.7](#extensions)).
- **Round trip:** Converting a document from one encoding to another and back MUST preserve the value of every element. Encodings are not required to preserve source layout, comments, or key order.
- **Character encoding:** Documents MUST be encoded in UTF-8.
- **Version token:** An encoding MAY carry a token declaring the specification version the document was written to. Readers MUST accept a token naming any version of this specification and MAY warn on a version they do not recognize.

<a id="enc-markdown"></a>

### 6.2. Markdown Encoding

The Markdown encoding is the file format of [[FRAME-V02]](#ref-FRAME-V02). A document conforming to v0.2 conforms to this encoding. This section restates v0.2's requirements in the terms of this specification and adds the mapping of body structure to elements.

<a id="md-structure"></a>

#### 6.2.1. Document Structure

A document is a Markdown file beginning with a YAML front matter block delimited by lines consisting of three hyphens, followed by a Markdown body.

The front matter is a YAML mapping [[YAML12]](#ref-YAML12). Its keys are element names, with two aliases retained from v0.2: the key `name` denotes `title`, and the key `inherits` denotes `composition`. A writer producing this encoding MUST use the aliased spellings so that v0.2 readers continue to accept the document.

The following front matter keys are REQUIRED in this encoding, as they are in v0.2: `type`, `name`, `description`, `visibility`. The `type` value MUST be `frame` or `frame [<major>.<minor>]`, where the bracketed token names the specification version; `frame [0.3]` denotes this document, and `frame [0.2]` denotes [[FRAME-V02]](#ref-FRAME-V02) and remains valid. The `type` key is the version token of [Section 6.1](#enc-common) and is specific to this encoding; it exists so that a reader can distinguish a Frame from other Markdown files, which structured encodings do not need.

<a id="md-body"></a>

#### 6.2.2. Body Structure

The body is the `guidance` element, with the following rule for extracting refinements.

A level-two heading (a line beginning with two hash characters) whose text, after trimming white space and ignoring case, equals the label of a refinement begins a section whose content is that refinement's value. The labels are: Rules, Terminology, Goals, Style, Norms, Skills, Tool Specifications, Prompts, Architecture, Business Process. A section extends to the next level-two heading or the end of the document. Headings of level three and deeper within a section belong to that section.

Every other level-two heading, and all content not within a refinement section, is `guidance`. A reader MUST NOT treat an unrecognized heading as an error. A heading whose text merely contains a label, such as "Rules of the Game" or "Review Norms", is not a match and its section is `guidance`; readers MUST NOT match labels by prefix, suffix, or similarity.

A writer emits exactly one `guidance` value per document, containing all non-refinement content in document order with its own headings preserved, and emits each refinement as a level-two section with its label. Because refinement sections are extracted wherever they occur and re-emitted after the guidance, a document whose refinement sections are interleaved with loose prose will not preserve its layout across a round trip; it will preserve every element value. Authors who care about layout SHOULD place refinement sections last.

<a id="md-terminology"></a>

#### 6.2.3. Terminology in Markdown

Within a Terminology section, a list item of the form `- **term**: definition` is a concept in the structured form of [Section 4.4.2](#terminology-form); the bold text is the preferred label and the remainder is the definition. Any other content in the section is unstructured `terminology` content. A reader MUST NOT fail on the shape of a list item.

<a id="md-mediatype"></a>

#### 6.2.4. Media Type

The media type of this encoding is `text/markdown` [[RFC7763]](#ref-RFC7763) with the parameters `charset=utf-8` and `variant=frame` ([Section 10.1.3](#iana-markdown-variant)).

<a id="md-example"></a>

#### 6.2.5. Example

```markdown
---
type: frame [0.3]
identifier: acme/brand-voice
name: Brand Voice
description: How Acme sounds in public writing.
visibility: internal
version: 1.2.0
status: approved
maintainer: marketing
license: CC-BY-4.0
inherits:
  - acme/company-core@2.0.0
guards:
  - acme/pii-guard
---

Be plain and direct. Prefer short sentences.

## Rules

- No performance claims without a cited benchmark.

## Terminology

- **customer**: an organization that has deployed an Acme Hub.
- Prefer "Hub" over "instance".

## Things We Avoid

- The word "revolutionary".
```

*Figure 6: A Frame in the Markdown encoding*

In this example `guidance` is the opening paragraph together with the "Things We Avoid" section; `rules` has one value; `terminology` has one structured concept and one unstructured entry.

<a id="enc-yaml"></a>

### 6.3. YAML Encoding

A document is a single YAML mapping [[YAML12]](#ref-YAML12) whose keys are element names in lower camel case and whose values are the elements' values. `guidance` and the refinements are keys at the top level of the mapping. Repeatable elements are sequences; a non-repeatable element is a scalar. A `terminology` value in the structured form is a sequence of mappings with the keys `term`, `definition`, and optionally `altTerms`, corresponding to `skos:prefLabel`, `skos:definition`, and `skos:altLabel`.

The key `type` MAY be present with a value of the form given in [Section 6.2.1](#md-structure), and MUST NOT be required; a structured document does not need a discriminator to be recognized.

The media type of this encoding is `application/frame+yaml` ([Section 10.1.2](#iana-yaml)).

```yaml
identifier: acme/brand-voice
title: Brand Voice
description: How Acme sounds in public writing.
visibility: internal
version: 1.2.0
status: approved
maintainer: [marketing]
license: CC-BY-4.0
composition:
  - acme/company-core@2.0.0
guards:
  - acme/pii-guard
guidance: |
  Be plain and direct. Prefer short sentences.

  ## Things We Avoid

  - The word "revolutionary".
rules:
  - No performance claims without a cited benchmark.
terminology:
  - term: customer
    definition: an organization that has deployed an Acme Hub.
  - Prefer "Hub" over "instance".
```

*Figure 7: The same Frame in the YAML encoding*

<a id="enc-json"></a>

### 6.4. JSON Encoding

A document is a single JSON object [[RFC8259]](#ref-RFC8259) whose members are element names in lower camel case. The structure is that of the YAML encoding: repeatable elements are arrays, non-repeatable elements are strings, and a structured `terminology` value is an array of objects with the members `term`, `definition`, and optionally `altTerms`.

A document MAY include a `@context` member whose value maps element names to the vocabulary terms of [Appendix A](#crosswalk), and a `@type` member with the value `Frame`, making the document a JSON-LD document [[JSON-LD11]](#ref-JSON-LD11). Readers that do not process JSON-LD MUST preserve these members as they would any unrecognized element.

The media type of this encoding is `application/frame+json` ([Section 10.1.1](#iana-json)).

```json
{
  "@context": "https://frames.example.org/context/v0.3",
  "@type": "Frame",
  "identifier": "acme/brand-voice",
  "title": "Brand Voice",
  "description": "How Acme sounds in public writing.",
  "visibility": "internal",
  "version": "1.2.0",
  "status": "approved",
  "maintainer": ["marketing"],
  "license": "CC-BY-4.0",
  "composition": ["acme/company-core@2.0.0"],
  "guards": ["acme/pii-guard"],
  "guidance": "Be plain and direct. Prefer short sentences.\n\n## Things We Avoid\n\n- The word \"revolutionary\".",
  "rules": ["No performance claims without a cited benchmark."],
  "terminology": [
    {"term": "customer",
     "definition": "an organization that has deployed an Acme Hub."},
    "Prefer \"Hub\" over \"instance\"."
  ]
}
```

*Figure 8: The same Frame in the JSON encoding*

<a id="profiles"></a>

## 7. Conformance Profiles

An implementation that conforms to this specification MUST publish a conformance profile. A profile is a short document, in any form, that declares the implementation's choices for every behavior this specification leaves optional. It MAY additionally narrow elements as permitted by [Section 4.1](#element-def) and [Section 5.1](#composition-rules), and MUST declare each narrowing.

A profile MUST state:

1. Which encodings the implementation reads and writes.
2. Whether it resolves composition at all, and if so, whether transitively (rule 4).
3. Which reference forms of [Section 5.3](#ref-syntax) it resolves (rule 9).
4. Which narrowings of rule 6 it applies, and to which elements.
5. Which elements it treats as non-repeatable beyond those the model defines as such, and which elements it requires beyond `identifier` and `guidance`.
6. How it derives an identifier for a Frame that arrives without one ([Section 3.2](#identity)), if it does so.
7. How it treats `visibility`, confirming that it is not used as an access control.

[Appendix C](#profile-template) gives a template. Two implementations' profiles are described in [Section 8](#impl-status).

<a id="impl-status"></a>

## 8. Implementation Status

This section records the status of known implementations of this specification at the time of posting, following [[RFC7942]](#ref-RFC7942). The description of an implementation here is not an endorsement. This section is to be removed before publication as an RFC.

- **Nebari Frames:** [[NEBARI-FRAMES]](#ref-NEBARI-FRAMES). A registry with a web application, a command-line client, and a Model Context Protocol endpoint. Reads and writes the Markdown encoding; stores Frames in a structured form close to the YAML encoding. Resolves composition transitively with cycle detection, resolves only `pinned-ref` forms, narrows six refinements (`toolSpecs`, `goals`, `style`, `norms`, `architecture`, `businessProcess`) to non-repeatable, applies replacement by key to `terminology`, and deduplicates repeatable values. At the time of posting it constrains `title` to an identifier syntax and rejects unrecognized headings, unrecognized front matter keys, and unstructured terminology entries, none of which conforms to this specification; changes to remove those behaviors are planned. Maturity: beta.
- **Collab:** A desktop application that reads the Markdown encoding and resolves no composition [[FRAME-SPEC-21]](#ref-FRAME-SPEC-21). Conformance to this specification requires publication of a profile declaring that behavior. Maturity: unknown to the author.

<a id="security"></a>

## 9. Security Considerations

This section follows the guidance of [[RFC3552]](#ref-RFC3552).

<a id="threat-model"></a>

### 9.1. Threat Model

A Frame is text loaded as context for an AI system. Whatever a Frame says, the system it is loaded into is disposed to follow. The attacker of interest therefore controls, or can influence, the content of a Frame that a target will load: by authoring a Frame the target installs, by modifying a Frame in transit or at rest, by controlling a Frame that a trusted Frame composes, or by controlling a registry the target retrieves from. Attacks on the transport (eavesdropping, replay, insertion, deletion, modification, and interposition) are in scope insofar as they deliver a modified Frame; their mitigation is the responsibility of the transport and of the registry, and is outside this specification.

<a id="injection"></a>

### 9.2. Instruction Injection

A Frame is, by design, instructions. There is no distinction this specification can draw between a Frame's legitimate guidance and an attacker's, because both are text in the `guidance` element. Implementations and users MUST treat the decision to load a Frame as the decision to trust its author with influence over the system's behavior, and SHOULD load Frames only from sources they trust. The `maintainer`, `canonicalSource`, `checksum`, and `derivedFrom` elements exist to make provenance visible; none of them authenticates it. Authentication of a Frame's origin is a registry and transport concern.

<a id="trust-composition"></a>

### 9.3. Composition Extends Trust

Loading a Frame that composes others extends trust to every Frame in the composed set, and, if the reader resolves transitively, to their composed Frames in turn. A reader that resolves composition SHOULD make the fully resolved set visible to the user before loading it. Rule 7 of [Section 5.1](#composition-rules) requires that an unresolvable reference be reported rather than silently dropped, so that a user is not misled about what was loaded. Rule 5's accumulation of `guards` means a composed Frame can attach a validation requirement to a child; it also means a malicious composed Frame could attach a Guard reference the child's author did not intend, which a reader that surfaces the resolved set makes visible.

<a id="identity-claim"></a>

### 9.4. Identity Is a Claim

An `identifier` is asserted by the Frame. A Frame may claim any identifier, including one belonging to a Frame its author does not control. The identity rules of [Section 3.2](#identity) make a change of identifier visible through `derivedFrom`; they do not prevent an attacker from omitting `derivedFrom`. Consumers that need to know whether a Frame is the one it claims to be MUST rely on a registry's attestation or on a `checksum` obtained through a trusted channel, not on the identifier alone. `canonicalSource` helps a consumer find the authoritative copy; it does not prove that the copy in hand matches it.

<a id="visibility-security"></a>

### 9.5. Visibility Is Not Access Control

The `visibility` element declares the maintainer's intent. A Frame marked `private` carries no protection of any kind. A reader MUST NOT infer from `visibility` that a Frame is protected, and a registry MUST NOT rely on it in place of access control. This is stated as a requirement because the element's name invites the misreading.

<a id="unknown-security"></a>

### 9.6. Unknown Elements

Readers preserve elements they do not recognize ([Section 4.7](#extensions)). An attacker could place instructions in an extension element in the hope that a reader forwards them to the model. [Section 4.7](#extensions) therefore requires that unrecognized elements never be presented to an AI system as guidance. An implementation that forwards arbitrary metadata into model context does not conform.

<a id="resources"></a>

### 9.7. Resource Exhaustion

Composition can be deep, wide, or cyclic. Rule 8 requires cycle detection. Implementations that resolve composition SHOULD bound resolution depth and the total size of the resolved content, and SHOULD apply size limits to individual Representations. A registry that caps stored size but not resolved size remains exposed to a Frame that composes many large Frames.

<a id="guards-security"></a>

### 9.8. Guards Are Declared, Not Enforced

A Frame may declare that a Guard must be run on output. This specification does not run Guards, and a declaration is not an enforcement. Whether a declared Guard is honored is the responsibility of the runtime that executes the work, under whatever Guard contract applies. Consumers MUST NOT assume that output produced under a Frame was validated merely because the Frame declares a Guard.

<a id="residual"></a>

### 9.9. Residual Risk

After the mitigations above, the residual risk is the behavior of an AI system under adversarial context, which this specification cannot bound. A Frame from a trusted source, unmodified, correctly composed, with every declared Guard run, may still induce behavior its author did not anticipate. The accountability that [[INTHUB]](#ref-INTHUB) places on a Frame's maintainer is a social and organizational control, not a technical one, and this specification's contribution is to make the maintainer, the provenance, and the composed set visible so that the control can operate.

<a id="iana"></a>

## 10. IANA Considerations

<a id="iana-media"></a>

### 10.1. Media Type Registrations

<a id="iana-json"></a>

#### 10.1.1. application/frame+json

IANA is requested to register the following media type in the standards tree, per [[RFC6838]](#ref-RFC6838).

- **Type name:** application
- **Subtype name:** frame+json
- **Required parameters:** N/A
- **Optional parameters:** N/A
- **Encoding considerations:** Same as `application/json` [[RFC8259]](#ref-RFC8259). Binary.
- **Security considerations:** See [Section 9](#security) of this document.
- **Interoperability considerations:** N/A
- **Published specification:** This document, [Section 6.4](#enc-json).
- **Applications that use this media type:** Registries, desktop applications, and AI systems that exchange organizational context artifacts.
- **Fragment identifier considerations:** As for `application/json`.
- **Additional information:** File extension: `.frame.json`. Structured syntax suffix `+json` per [[RFC6839]](#ref-RFC6839).
- **Person and email address to contact for further information:** See the Author's Address section.
- **Intended usage:** COMMON
- **Restrictions on usage:** None
- **Author:** See the Author's Address section.
- **Change controller:** IETF

<a id="iana-yaml"></a>

#### 10.1.2. application/frame+yaml

IANA is requested to register the following media type in the standards tree, per [[RFC6838]](#ref-RFC6838).

- **Type name:** application
- **Subtype name:** frame+yaml
- **Required parameters:** N/A
- **Optional parameters:** N/A
- **Encoding considerations:** Same as `application/yaml` [[RFC9512]](#ref-RFC9512). Binary.
- **Security considerations:** See [Section 9](#security) of this document, and the security considerations of [[RFC9512]](#ref-RFC9512).
- **Interoperability considerations:** As for `application/yaml`.
- **Published specification:** This document, [Section 6.3](#enc-yaml).
- **Applications that use this media type:** As for `application/frame+json`.
- **Fragment identifier considerations:** As for `application/yaml`.
- **Additional information:** File extension: `.frame.yaml`. Structured syntax suffix `+yaml` per [[RFC9512]](#ref-RFC9512).
- **Person and email address to contact for further information:** See the Author's Address section.
- **Intended usage:** COMMON
- **Restrictions on usage:** None
- **Author:** See the Author's Address section.
- **Change controller:** IETF

<a id="iana-markdown-variant"></a>

#### 10.1.3. Markdown Variant "frame"

IANA is requested to register the following variant in the Markdown Variants registry established by [[RFC7763]](#ref-RFC7763).

- **Identifier:** frame
- **Name:** Frame
- **Description:** CommonMark-compatible Markdown preceded by a YAML front matter block carrying Frame elements, as specified in [Section 6.2](#enc-markdown) of this document. Level-two headings matching registered refinement labels denote structured sections.
- **Additional parameters:** None
- **Fragment identifiers:** As for `text/markdown`.
- **References:** This document.
- **Contact information:** See the Author's Address section.

<a id="iana-elements"></a>

### 10.2. Frame Element Names Registry

IANA is requested to create a registry named "Frame Element Names". The registration policy is Specification Required [[RFC8126]](#ref-RFC8126). Each entry consists of an element name in lower camel case, a label, the level at which it applies (Frame, Version, or Representation), whether it is repeatable, the element it refines if any, and a reference to its defining specification. Names beginning with `x-` are reserved for Private Use and MUST NOT be registered.

The initial contents are the elements defined in [Section 4](#elements) of this document: the twenty-seven Frame- and Version-level elements and the three Representation-level elements listed in [Section 4.8](#element-summary), each with reference to this document.

<a id="iana-status"></a>

### 10.3. Frame Status Values Registry

IANA is requested to create a registry named "Frame Status Values". The registration policy is Specification Required [[RFC8126]](#ref-RFC8126). Each entry consists of a value (lower case, ASCII letters and hyphens), a one-sentence meaning, and a reference.

Initial contents:

| Value | Meaning | Reference |
|---|---|---|
| draft | Not yet ready for use | This document |
| review | Under review by the maintainer or a designated reviewer | This document |
| approved | Approved for use within its declared visibility | This document |
| deprecated | Superseded; use is discouraged | This document |
| revoked | Withdrawn; MUST NOT be used | This document |

*Table 2: Initial Frame Status Values*

<a id="iana-visibility"></a>

### 10.4. Frame Visibility Values Registry

IANA is requested to create a registry named "Frame Visibility Values". The registration policy is Specification Required [[RFC8126]](#ref-RFC8126). Each entry consists of a value (lower case, ASCII letters and hyphens), a one-sentence meaning, and a reference.

Initial contents:

| Value | Meaning | Reference |
|---|---|---|
| private | Intended for the maintainer only | This document |
| internal | Intended for the maintainer's organization | This document |
| shared | Intended for named parties outside the organization | This document |
| public | Intended for anyone | This document |

*Table 3: Initial Frame Visibility Values*

<a id="iana-refinements"></a>

### 10.5. Frame Refinements Registry

IANA is requested to create a registry named "Frame Refinements". The registration policy is Specification Required [[RFC8126]](#ref-RFC8126). Each entry consists of an element name (which MUST also be registered in the Frame Element Names registry), the label used to recognize it in the Markdown encoding, the element it refines, and a reference. Labels are compared case-insensitively and MUST be unique within the registry under that comparison.

Initial contents: the ten refinements of [Section 4.4](#refinements), each refining `guidance`, with the labels given in [Section 6.2.2](#md-body), with reference to this document.

<a id="references"></a>

## 11. References

<a id="normative-references"></a>

### 11.1. Normative References

<a id="ref-FRAME-V02"></a>
**[FRAME-V02]** "Frame Spec v0.2.0", August 2026, [spec/v0.2.md](v0.2.md) in this repository.

<a id="ref-RFC2119"></a>
**[RFC2119]** Bradner, S., "Key words for use in RFCs to Indicate Requirement Levels", BCP 14, RFC 2119, DOI 10.17487/RFC2119, March 1997, <https://www.rfc-editor.org/rfc/rfc2119>.

<a id="ref-RFC3339"></a>
**[RFC3339]** Klyne, G. and C. Newman, "Date and Time on the Internet: Timestamps", RFC 3339, DOI 10.17487/RFC3339, July 2002, <https://www.rfc-editor.org/rfc/rfc3339>.

<a id="ref-RFC3986"></a>
**[RFC3986]** Berners-Lee, T., Fielding, R., and L. Masinter, "Uniform Resource Identifier (URI): Generic Syntax", STD 66, RFC 3986, DOI 10.17487/RFC3986, January 2005, <https://www.rfc-editor.org/rfc/rfc3986>.

<a id="ref-RFC5234"></a>
**[RFC5234]** Crocker, D., Ed. and P. Overell, "Augmented BNF for Syntax Specifications: ABNF", STD 68, RFC 5234, DOI 10.17487/RFC5234, January 2008, <https://www.rfc-editor.org/rfc/rfc5234>.

<a id="ref-RFC6838"></a>
**[RFC6838]** Freed, N., Klensin, J., and T. Hansen, "Media Type Specifications and Registration Procedures", BCP 13, RFC 6838, DOI 10.17487/RFC6838, January 2013, <https://www.rfc-editor.org/rfc/rfc6838>.

<a id="ref-RFC6839"></a>
**[RFC6839]** Hansen, T. and A. Melnikov, "Additional Media Type Structured Syntax Suffixes", RFC 6839, DOI 10.17487/RFC6839, January 2013, <https://www.rfc-editor.org/rfc/rfc6839>.

<a id="ref-RFC7763"></a>
**[RFC7763]** Leonard, S., "The text/markdown Media Type", RFC 7763, DOI 10.17487/RFC7763, March 2016, <https://www.rfc-editor.org/rfc/rfc7763>.

<a id="ref-RFC8126"></a>
**[RFC8126]** Cotton, M., Leiba, B., and T. Narten, "Guidelines for Writing an IANA Considerations Section in RFCs", BCP 26, RFC 8126, DOI 10.17487/RFC8126, June 2017, <https://www.rfc-editor.org/rfc/rfc8126>.

<a id="ref-RFC8174"></a>
**[RFC8174]** Leiba, B., "Ambiguity of Uppercase vs Lowercase in RFC 2119 Key Words", BCP 14, RFC 8174, DOI 10.17487/RFC8174, May 2017, <https://www.rfc-editor.org/rfc/rfc8174>.

<a id="ref-RFC8259"></a>
**[RFC8259]** Bray, T., Ed., "The JavaScript Object Notation (JSON) Data Interchange Format", STD 90, RFC 8259, DOI 10.17487/RFC8259, December 2017, <https://www.rfc-editor.org/rfc/rfc8259>.

<a id="ref-RFC9512"></a>
**[RFC9512]** Polli, R., Wilde, E., and E. Aro, "YAML Media Type", RFC 9512, DOI 10.17487/RFC9512, February 2024, <https://www.rfc-editor.org/rfc/rfc9512>.

<a id="ref-SEMVER"></a>
**[SEMVER]** Preston-Werner, T., "Semantic Versioning 2.0.0", 2013, <https://semver.org/spec/v2.0.0.html>.

<a id="ref-YAML12"></a>
**[YAML12]** YAML Language Development Team, "YAML Ain't Markup Language (YAML) Version 1.2, Revision 1.2.2", October 2021, <https://yaml.org/spec/1.2.2/>.

<a id="informative-references"></a>

### 11.2. Informative References

<a id="ref-ADMS"></a>
**[ADMS]** W3C, "Asset Description Metadata Schema (ADMS)", August 2013, <https://www.w3.org/TR/vocab-adms/>.

<a id="ref-AGENTS-MD"></a>
**[AGENTS-MD]** Agentic AI Foundation, "AGENTS.md", 2026, <https://agents.md/>.

<a id="ref-DC-USAGE"></a>
**[DC-USAGE]** Dublin Core Metadata Initiative, "Using Dublin Core", November 2005, <https://www.dublincore.org/specifications/dublin-core/usageguide/>.

<a id="ref-DCAP"></a>
**[DCAP]** Dublin Core Metadata Initiative, "Guidelines for Dublin Core Application Profiles", May 2009, <https://www.dublincore.org/specifications/dublin-core/profile-guidelines/>.

<a id="ref-DCAT3"></a>
**[DCAT3]** W3C, "Data Catalog Vocabulary (DCAT) - Version 3", August 2024, <https://www.w3.org/TR/vocab-dcat-3/>.

<a id="ref-DCTAP"></a>
**[DCTAP]** Dublin Core Metadata Initiative, "DCTAP Elements", Draft, December 2022, <https://www.dublincore.org/specifications/dctap/elements/>.

<a id="ref-DCTERMS"></a>
**[DCTERMS]** Dublin Core Metadata Initiative, "DCMI Metadata Terms", January 2020, <https://www.dublincore.org/specifications/dublin-core/dcmi-terms/>.

<a id="ref-FRAME-SPEC-21"></a>
**[FRAME-SPEC-21]** openteams-ai/frame-spec, issue 21, "Investigation: inherits field and frame composition behavior in Collab", July 2026, <https://github.com/openteams-ai/frame-spec/issues/21>.

<a id="ref-INTHUB"></a>
**[INTHUB]** Oliphant, T., "The Distributed AI Economy: Intelligence Hubs, Frames, Cogs, Ops, and the Accountability Plane (Revision 9)", August 2026, <https://github.com/openteams-ai/inthub-whitepaper>.

<a id="ref-JSON-LD11"></a>
**[JSON-LD11]** W3C, "JSON-LD 1.1", July 2020, <https://www.w3.org/TR/json-ld11/>.

<a id="ref-NEBARI-FRAMES"></a>
**[NEBARI-FRAMES]** nebari-dev, "Nebari Frames", 2026, <https://github.com/nebari-dev/nebari-frames>.

<a id="ref-PROV-O"></a>
**[PROV-O]** W3C, "PROV-O: The PROV Ontology", April 2013, <https://www.w3.org/TR/prov-o/>.

<a id="ref-RFC3552"></a>
**[RFC3552]** Rescorla, E. and B. Korver, "Guidelines for Writing RFC Text on Security Considerations", BCP 72, RFC 3552, DOI 10.17487/RFC3552, July 2003, <https://www.rfc-editor.org/rfc/rfc3552>.

<a id="ref-RFC7942"></a>
**[RFC7942]** Sheffer, Y. and A. Farrel, "Improving Awareness of Running Code: The Implementation Status Section", BCP 205, RFC 7942, DOI 10.17487/RFC7942, July 2016, <https://www.rfc-editor.org/rfc/rfc7942>.

<a id="ref-RO-CRATE"></a>
**[RO-CRATE]** ResearchObject.org, "RO-Crate Metadata Specification 1.1", 2021, <https://www.researchobject.org/ro-crate/1.1/>.

<a id="ref-SCHEMA-ORG"></a>
**[SCHEMA-ORG]** Schema.org Community Group, "Schema.org Vocabulary", 2026, <https://schema.org/>.

<a id="ref-SINGAPORE"></a>
**[SINGAPORE]** Dublin Core Metadata Initiative, "The Singapore Framework for Dublin Core Application Profiles", January 2008, <https://www.dublincore.org/specifications/dublin-core/singapore-framework/>.

<a id="ref-SKOS"></a>
**[SKOS]** W3C, "SKOS Simple Knowledge Organization System Reference", August 2009, <https://www.w3.org/TR/skos-reference/>.

<a id="ref-SPDX"></a>
**[SPDX]** The Linux Foundation, "The System Package Data Exchange (SPDX) Specification", 2024, <https://spdx.github.io/spdx-spec/>.

<a id="crosswalk"></a>

## Appendix A. Relationship to Other Vocabularies

This appendix collects the correspondences stated element by element in [Section 4](#elements). An implementation that emits JSON-LD [[JSON-LD11]](#ref-JSON-LD11) uses these as its context.

| Element | Term | Fit |
|---|---|---|
| identifier | dcterms:identifier | exact |
| title | dcterms:title; schema:name | exact |
| description | dcterms:description; schema:abstract | exact |
| version | dcat:version; schema:version | exact |
| versionNotes | adms:versionNotes | exact |
| status | schema:creativeWorkStatus | exact |
| maintainer | schema:maintainer; schema:accountablePerson | exact; partial |
| scope | dcterms:audience | partial |
| visibility | dcterms:accessRights; schema:conditionsOfAccess | exact |
| license | dcterms:license | exact |
| issued | dcterms:issued | exact |
| canonicalSource | schema:sameAs; prov:specializationOf | exact; secondary |
| guidance | (none; nearest schema:text) | Frame-native |
| refinements | subproperties of guidance | Frame-native |
| terminology values | skos:Concept, skos:prefLabel, skos:definition, skos:altLabel | exact |
| composition | (none) | Frame-native |
| derivedFrom | prov:wasDerivedFrom; prov:hadPrimarySource | exact |
| previousVersion | dcat:previousVersion; prov:wasRevisionOf | exact |
| guards | dcterms:requires | exact |
| mediaType | dcat:mediaType | exact |
| checksum | spdx:checksum | exact |
| byteSize | dcat:byteSize | exact |

*Table 4: Element to vocabulary crosswalk*

The Frame-native terms (`guidance`, the ten refinements, and `composition`) require a namespace at which their URIs are published. The choice of namespace is a governance matter for the stewards of this specification and is not made here.

<a id="dctap"></a>

## Appendix B. Machine-Readable Profile

The element set of [Section 4](#elements) is published as a tabular application profile in the format of [[DCTAP]](#ref-DCTAP), with two columns beyond DCTAP's own: `mapsTo`, the crosswalk term, and `refines`, the refined element. A validator that reads this file can check obligation, repeatability, and value constraints without hard-coding the element set. The companion file `frame-core.csv` published with this specification is identical to the block below.

```csv
propertyID,propertyLabel,mandatory,repeatable,valueNodeType,valueDataType,valueConstraint,valueConstraintType,mapsTo,refines,note
identifier,Identifier,true,false,literal,xsd:string,,,dcterms:identifier,,Frame-level; defaults to retrieval location
guidance,Guidance,true,true,literal,xsd:string,,,,,Frame-native; may be empty
title,Title,false,false,literal,xsd:string,,,dcterms:title,,MUST NOT be slug-constrained
description,Description,false,false,literal,xsd:string,,,dcterms:description,,
version,Version,false,false,literal,xsd:string,,,dcat:version,,SemVer recommended
versionNotes,Version Notes,false,true,literal,xsd:string,,,adms:versionNotes,,
status,Status,false,false,literal,xsd:string,draft review approved deprecated revoked,picklist,schema:creativeWorkStatus,,registry; recommended values; others preserved
maintainer,Maintainer,false,true,literal,xsd:string,,,schema:maintainer,,accountable party
scope,Scope,false,false,literal,xsd:string,,,dcterms:audience,,partial mapping
visibility,Visibility,false,false,literal,xsd:string,private internal shared public,picklist,dcterms:accessRights,,not an access control; recommended values; others preserved
license,License,false,false,IRI,,,,dcterms:license,,
issued,Issued,false,false,literal,xsd:dateTime,,,dcterms:issued,,RFC 3339
canonicalSource,Canonical Source,false,false,IRI,,,,schema:sameAs,,
rules,Rules,false,true,literal,xsd:string,,,,guidance,
terminology,Terminology,false,true,literal,xsd:string,,,,guidance,structured form is skos:Concept
goals,Goals,false,true,literal,xsd:string,,,,guidance,
style,Style,false,true,literal,xsd:string,,,,guidance,
norms,Norms,false,true,literal,xsd:string,,,,guidance,
skills,Skills,false,true,literal,xsd:string,,,,guidance,
toolSpecs,Tool Specifications,false,true,literal,xsd:string,,,,guidance,typically references to spec files
prompts,Prompts,false,true,literal,xsd:string,,,,guidance,
architecture,Architecture,false,true,literal,xsd:string,,,,guidance,
businessProcess,Business Process,false,true,literal,xsd:string,,,,guidance,
composition,Composition,false,true,literal,xsd:string,frame-ref,pattern,,,Frame-native; ordered
derivedFrom,Derived From,false,true,literal,xsd:string,frame-ref,pattern,prov:wasDerivedFrom,,
previousVersion,Previous Version,false,false,literal,xsd:string,,,dcat:previousVersion,,
guards,Guards,false,true,literal,xsd:string,frame-ref,pattern,dcterms:requires,,composes by accumulation
mediaType,Media Type,false,false,literal,xsd:string,,,dcat:mediaType,,Representation level
checksum,Checksum,false,false,literal,xsd:string,,,spdx:checksum,,Representation level
byteSize,Byte Size,false,false,literal,xsd:integer,,,dcat:byteSize,,Representation level
```

*Figure 9: frame-core.csv*

<a id="profile-template"></a>

## Appendix C. Conformance Profile Template

```
Implementation:        <name and version>
Specification:         draft-mcandrew-frame-spec-00
Encodings read:        <markdown | yaml | json>
Encodings written:     <markdown | yaml | json>
Resolves composition:  <no | yes, non-transitive | yes, transitive>
Reference forms:       <pinned-ref | qualified-ref | uri-ref
                        | path-ref | name-ref>
Rule 6 narrowings:     <none | dedup: <elements>
                        | replace-by-key: <elements>>
Non-repeatable:        <elements narrowed beyond the model>
Additionally required: <elements beyond identifier and guidance>
Identifier minting:    <not performed | policy>
Visibility:            declared intent only; not an access control
Notes:                 <anything else an author should know>
```

*Figure 10: Conformance profile template*

Example, for the registry described in [Section 8](#impl-status):

```
Implementation:        Nebari Frames <version>
Specification:         draft-mcandrew-frame-spec-00
Encodings read:        markdown
Encodings written:     markdown
Resolves composition:  yes, transitive, with cycle detection
Reference forms:       pinned-ref only
Rule 6 narrowings:     dedup: all repeatable elements (last
                        occurrence kept); replace-by-key: terminology
Non-repeatable:        toolSpecs, goals, style, norms, architecture,
                        businessProcess
Additionally required: version (on publication)
Identifier minting:    slugified title; reject on collision
Visibility:            declared intent only; not an access control
Notes:                 internal storage is YAML but is not the YAML
                        encoding of this specification
```

*Figure 11: Example profile*

<a id="changes"></a>

## Appendix D. Changes from Frame Spec v0.2

This specification adds to [[FRAME-V02]](#ref-FRAME-V02); it does not remove or alter any v0.2 requirement for documents in the Markdown encoding.

- A data model ([Section 3](#model)) independent of any encoding, with Frame, Frame Version, and Representation.
- Definitions, obligations, and vocabulary correspondences for every element ([Section 4](#elements)), including definitions for `visibility` and `name` (as `title`), which v0.2 required without defining.
- Separation of identity (`identifier`) from display (`title`).
- Ten optional refinements of the body with the dumb-down rule ([Section 4.4](#refinements)).
- The `status`, `license`, `issued`, `canonicalSource`, `versionNotes`, `derivedFrom`, `previousVersion`, and `guards` elements.
- Registries for `status` and `visibility` values ([Section 10](#iana)). Registered values are RECOMMENDED; unregistered values are preserved, so Frames written before the registries existed remain valid.
- Composition rules 5 through 9 ([Section 5.1](#composition-rules)), session composition ([Section 5.4](#session)), and a reference grammar ([Section 5.3](#ref-syntax)).
- Identity rules ([Section 3.2](#identity)).
- The extensibility rule and the `x-` prefix ([Section 4.7](#extensions)).
- YAML and JSON encodings ([Section 6.3](#enc-yaml), [Section 6.4](#enc-json)) and media types for all three encodings ([Section 10](#iana)).
- Conformance profiles ([Section 7](#profiles)).
- Security considerations ([Section 9](#security)).

<a id="acknowledgements"></a>

## Acknowledgements

The definition of a Frame and the list of what a Frame carries are those of Travis Oliphant's Intelligence Hub whitepaper. Frame Spec v0.2 and its examples, on which the Markdown encoding rests, are the work of Trent Oliphant, WD Martinez, Mia Thurdekoos, the contributors known there as mcshayla and Vaidehi2510, and the other contributors to this repository. The dumb-down principle and the discipline of defining an element by definition and comment come from the Dublin Core Metadata Initiative.

<a id="authors-address"></a>

## Author's Address

Chuck McAndrew  
OpenTeams  
Email: cmcandrew@openteams.com
