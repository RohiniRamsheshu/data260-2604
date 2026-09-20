# SOURCES.md

Domain: Open-source package vulnerabilities (DOMAIN_ID = SID4 mod 8 = 4)
All sources accessed: 2026-09-20

Each corpus document synthesizes and paraphrases information from one or
more of the public sources listed below, grouped by corpus file. All
technical facts (CVE IDs, affected versions, CVSS scores, patch versions)
are drawn from these sources; content has been rewritten in this corpus's
own words rather than quoted verbatim, per the assignment's documentation
standards.

## 01-18: Individual vulnerability write-ups

| File | Primary sources |
|---|---|
| 01_log4j_CVE-2021-44228.txt | osv.dev/vulnerability/UBUNTU-CVE-2021-44228; nvd.nist.gov CVE-2021-44228; logging.apache.org/log4j/2.x/security.html; huntress.com/threat-library/vulnerabilities/cve-2021-44228 |
| 02_lodash_CVE-2020-8203.txt | github.com/advisories/GHSA-p6mc-m468-83gw; nvd.nist.gov CVE-2020-8203 |
| 03_lodash_CVE-2019-10744.txt | github.com/advisories (GHSA-jf85-cpcp-j695); nvd.nist.gov CVE-2019-10744 |
| 04_requests_CVE-2018-18074.txt | nvd.nist.gov CVE-2018-18074; app.opencve.io/cve/CVE-2018-18074; usn.ubuntu.com/3790-1 |
| 05_django_CVE-2021-35042.txt | nvd.nist.gov CVE-2021-35042; Django project security release notes |
| 06_flask_CVE-2019-1010083.txt | nvd.nist.gov CVE-2019-1010083; Pallets Flask changelog |
| 07_express_CVE-2024-29041.txt | github.com/advisories (GHSA-rv95-896h-c2vc) |
| 08_pyyaml_CVE-2020-14343.txt | nvd.nist.gov CVE-2020-14343; PyYAML changelog |
| 09_jackson-databind_CVE-2020-36518.txt | nvd.nist.gov CVE-2020-36518; FasterXML jackson-databind advisories |
| 10_axios_CVE-2023-45857.txt | github.com/advisories (GHSA-wf5p-g6vw-rhxx) |
| 11_spring-core_CVE-2022-22965.txt | spring.io blog "CVE-2022-22965: Spring Framework RCE via Data Binding on JDK 9+"; nvd.nist.gov CVE-2022-22965 |
| 12_urllib3_CVE-2019-11324.txt | nvd.nist.gov CVE-2019-11324; urllib3 GitHub advisories/changelog |
| 13_struts2_CVE-2017-5638.txt | Apache Struts Security Bulletin S2-045; nvd.nist.gov CVE-2017-5638 |
| 14_openssl_CVE-2014-0160.txt | heartbleed.com; nvd.nist.gov CVE-2014-0160 |
| 15_bash_CVE-2014-6271.txt | nvd.nist.gov CVE-2014-6271; Red Hat Security Advisory (Shellshock) |
| 16_xz-utils_CVE-2024-3094.txt | openwall.com/lists/oss-security disclosure thread; nvd.nist.gov CVE-2024-3094; CISA advisory |
| 17_commons-text_CVE-2022-42889.txt | github.com/advisories (GHSA-599f-7c49-w659); Apache Commons Text security report |
| 18_event-stream_supply-chain-2018.txt | npm security advisory for event-stream; public Copay/BitPay incident disclosure |

## 19-46: Extended case studies, technical deep-dives, and reference material

These documents synthesize information from the sources listed above
(for vulnerabilities they revisit in more depth, e.g. Log4Shell,
Spring4Shell, Text4Shell, jackson-databind, PyYAML) plus the following
additional sources:

| File | Additional sources |
|---|---|
| 19_npm-supply-chain-history.txt | npm security advisories; ua-parser-js maintainer GitHub post-mortem; coverage of colors.js/faker.js and node-ipc incidents |
| 22_cwe-weakness-catalog.txt | cwe.mitre.org; owasp.org Top 10:2021 |
| 23_vulnerability-databases-explainer.txt | cve.org; nvd.nist.gov; docs.github.com (Advisory Database); osv.dev documentation; first.org (CVSS spec) |
| 27_equifax-case-study.txt | U.S. GAO report GAO-18-559 |
| 28_xz-backdoor-extended-analysis.txt | Andres Freund's oss-security disclosure post; CISA advisory |
| 38_patch-prioritization-kev-epss.txt | cisa.gov/known-exploited-vulnerabilities-catalog; first.org (EPSS documentation) |
| 42_session-cookie-security.txt | owasp.org Session Management Cheat Sheet; developer.mozilla.org (Set-Cookie docs) |
| All others (20, 21, 24-26, 29-37, 39-41, 43-47) | Synthesized from the primary vulnerability sources above; no additional external sources beyond those already cited within each document's own "Sources" section |

## Note on source fidelity

All technical facts (affected versions, patch versions, CVSS scores, CVE/
GHSA identifiers) are cross-checked against the primary sources listed
above. Descriptive/narrative text has been paraphrased and expanded upon
in this corpus author's own words rather than reproduced verbatim from
any source, per copyright and originality requirements.
