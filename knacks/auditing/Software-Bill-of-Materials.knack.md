# Software Bill of Materials

Load this knack when release, procurement, incident response, or dependency
review needs a structured software component inventory rather than a package
list assembled from memory.

## Mental Model

A software bill of materials, or SBOM, is not a truth oracle. It is a snapshot
of what a tool or build process could observe about a particular software
artifact at a particular time. Treat it as evidence with provenance, scope,
and blind spots.

The working model has four layers:

1. inventory collection from package managers, lockfiles, build systems,
   source scanners, binary scanners, and manual declarations;
2. normalization into identifiers, versions, hashes, suppliers, licenses, and
   dependency relationships;
3. transport or attestation in a format such as SPDX or CycloneDX; and
4. audit use for vulnerability, license, provenance, procurement, and change
   review.

An audit conclusion is only as strong as the inventory scope and generation
evidence behind it.

## Useful Contents

A useful SBOM should identify, when known:

- component name and version;
- supplier, author, or publisher;
- dependency relationships;
- artifact hashes;
- declared license expressions;
- package URLs, CPEs, or other machine-matchable identifiers;
- build and release context; and
- known completeness limitations.

SPDX emphasizes package identity, licensing, and relationships. CycloneDX is
widely used in security and supply-chain workflows and also represents
services, vulnerabilities, and formulation data. Either format can carry
incorrect or incomplete source data.

## Collection Methods

### Package and Lockfile Extraction

Package manifests and lockfiles often provide high-confidence direct and
transitive dependency data. They may miss vendored code, build-time
downloads, runtime plug-ins, generated artifacts, and manually copied source.

### Build-Pipeline Emission

The build can emit metadata as it resolves and assembles components. This
often describes shipped output better than a source manifest, but it depends
on an observable and reproducible build.

### Source Scanning

Source scanners find manifests, license files, fingerprints, and copied code
outside package-manager control. They can misidentify versions, overcount
copies, or miss generated and downloaded artifacts.

### Binary and Container Scanning

Artifact scanners inspect compiled output, packages, images, or deployed
files. They are valuable when build metadata is missing, but may identify a
component without explaining how it was built or why it is present.

### Manual Augmentation

Human-maintained declarations may be required for commercial components,
private forks, firmware, fonts, models, media, and embedded third-party
material. Automation alone rarely proves completeness.

## Reconcile Multiple Views

A mature workflow commonly:

- generates inventory from the build or package resolver;
- scans source or final artifacts for drift and copied material; and
- reconciles disagreements.

Differences are evidence. A source scanner may find vendored code; an artifact
scanner may show that a declared dependency was not shipped. Preserve and
explain the difference rather than averaging it away.

## Audit Modes

### License Review

Compare declared and detected licenses with the actual distribution, hosting,
and modification model. Escalate unknown, custom, dual-licensed, reciprocal,
source-available, and exception-bearing terms.

An SBOM identifies candidate obligations; it does not provide legal advice.
License conclusions require current source material and appropriate legal
review.

### Vulnerability Review

Map components to advisories through package URLs, CPEs, vendor notices, and
ecosystem identifiers. Confirm that the component, version, build options,
patch state, and reachable code path apply to the shipped artifact.

Use VEX or equivalent exploitability context where appropriate. Component
presence alone does not prove reachability or exploitability.

### Provenance and Change Review

Compare SBOMs across releases. Investigate new components, supplier changes,
unexpected transitive dependencies, version drift, and identifier changes.

### Completeness Review

Ask what the generation process could not see:

- build and test dependencies;
- dynamically loaded plug-ins;
- private packages;
- container base-image contents;
- copied or vendored code; and
- separately licensed non-code assets.

## Common Failure Modes

- Treating a polished JSON document as proof of completeness.
- Describing the source tree but not the released image or installer.
- Ignoring copied code because it bypassed the package manager.
- Accepting unknown licenses without review.
- Expecting weak identifiers to map perfectly to vulnerability data.
- Generating the SBOM before final dependency resolution or image assembly.
- Failing to preserve it beside the exact artifact it describes.

## Review Checklist

- Define scope: source, build output, image, deployed service, or procurement
  target.
- Record generator, version, configuration, inputs, and generation time.
- Tie at least one collection path to the released artifact.
- Compare automated output with known vendored, private, and commercial
  components.
- Normalize package URLs, CPEs, SPDX expressions, hashes, and supplier data
  where possible.
- Record completeness limits and unresolved identity matches.
- Preserve the SBOM with release evidence.
- Regenerate when dependencies, build behavior, or packaging changes.

## Further Information

- CISA, SBOM resources: <https://www.cisa.gov/sbom>
- NTIA, minimum elements for an SBOM:
  <https://www.ntia.gov/report/2021/minimum-elements-software-bill-materials-sbom>
- SPDX specifications: <https://spdx.dev/specifications/>
- CycloneDX specification:
  <https://cyclonedx.org/specification/overview/>
- CISA, SBOM consumption guidance:
  <https://www.cisa.gov/resources-tools/resources/securing-software-supply-chain-recommended-practices-software-bill-materials-consumption>
