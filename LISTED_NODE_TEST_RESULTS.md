# Listed node contracts: measured results

Test run: 2026-10-20. Baseline: the delivered Dirt2Dollar Full50 source snapshot.
Environment: Python 3.12, Playwright 1.64.1, Linux. No browser or web server.
All cases execute real node lifecycle/logic with recorded provider/repository mocks.

| Registered | Passed | Failed | Skipped | Adapter/startup errors |
| ---: | ---: | ---: | ---: | ---: |
| 189 | 150 | 39 | 0 | 0 |

Playwright TypeScript typecheck and Python adapter syntax passed. Test discovery confirms
40 original frontend + 10 original integration + 189 new node scenarios = 239 registered.
The original 50 test bodies and production src/ files are unchanged; those 50 were not
re-executed for this test-only patch. Windows execution is not verified here.

## What the 39 failures mean

27 cases fail only because the sheet requires an older exact exception class:
ValueError/RuntimeError versus current ValidationException/ServiceException. Their
error messages and other assertions pass. These need a decision on the approved error
contract, not an automatic change to production exception handling.

Exception-class cases: TC02, TC03, TC04, TC05, TC06, TC07, TC08, TC09, TC10, TC129, TC148, TC149, TC152, TC159, TC160, TC161, TC162, TC163, TC164, TC165, TC173, TC175, TC176, TC180, TC183, TC184, TC189.

The other 12 cases reveal these behaviour/expectation disagreements:

| Cases | Observation |
| --- | --- |
| TC14, TC18, TC24, TC32, TC33, TC34 | Extracted names differ from the sheet, including instruction text treated as client names and AT&T being reduced to Show. |
| TC49 | Node returns 59.99 under the explicit 0.6/0.4 fixture; sheet expects 60.0. Rounding/expected value needs review. |
| TC109 | Node accepts a controlled unrelated High Risk AI interpretation despite incomplete KPI inputs. |
| TC111, TC112 | With separate zero lead/appointment counts and nonzero improving costs, NO_LEADS/NO_APPOINTMENTS are absent. Current logic checks zero costs instead. |
| TC137 | Created KPI record gets the fallback name, but kpi_dataset.client_name remains null. |
| TC142 | KPI embedding text still contains a DETECTED PATTERNS section when patterns are empty. |

No case is marked test.fail, skipped, or made green using the historical Actual Result.
The source originally records 181 Pass and 8 Fail. New outcomes are independent.
Input assumptions are explicit in LISTED_NODE_TESTS.md and each fixture_note.

## Results by feature

| Feature | Passed | Failed |
| --- | ---: | ---: |
| Client Data Retrieval | 1 | 9 |
| Client Name Extraction | 18 | 6 |
| Final Churn Probability | 15 | 1 |
| Final Client Summary | 12 | 0 |
| Result Persistence | 15 | 0 |
| Historical KPI Match | 14 | 0 |
| Historical Update Match | 14 | 0 |
| KPI Analysis | 11 | 3 |
| KPI Churn Analysis | 9 | 1 |
| KPI Data | 9 | 1 |
| KPI Embedding | 7 | 3 |
| Summary Batch Preparation | 7 | 1 |
| Summary Churn Analysis | 1 | 7 |
| Summary Embedding | 7 | 1 |
| Summary Generation | 5 | 3 |
| Updates Data | 5 | 3 |

## One-to-one case index

Every row maps to frontend/e2e/node-contracts/listed-cases.spec.ts under the shown
feature and exact `TCxx | Scenario` title. Inputs, original sheet fields and assertions
are in tests/playwright_node_cases.json. Search by TC ID in Playwright UI Mode.

| Sheet ID | Feature | Exact Playwright title | Result | Failure detail |
| --- | --- | --- | --- | --- |
| TC01 | Client Data Retrieval | TC01 \| Valid client name | Passed |  |
| TC02 | Client Data Retrieval | TC02 \| Client does not exist | Failed | TC02: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC03 | Client Data Retrieval | TC03 \| Empty client name | Failed | TC03: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC04 | Client Data Retrieval | TC04 \| Null client name | Failed | TC04: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC05 | Client Data Retrieval | TC05 \| Client name contains only spaces | Failed | TC05: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC06 | Client Data Retrieval | TC06 \| Lowercase client name | Failed | TC06: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC07 | Client Data Retrieval | TC07 \| Uppercase client name | Failed | TC07: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC08 | Client Data Retrieval | TC08 \| Misspelled client name | Failed | TC08: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC09 | Client Data Retrieval | TC09 \| Special characters in client name | Failed | TC09: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC10 | Client Data Retrieval | TC10 \| Numeric client name | Failed | TC10: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC11 | Client Name Extraction | TC11 \| Valid client name | Passed |  |
| TC12 | Client Name Extraction | TC12 \| Valid multi-word client name | Passed |  |
| TC13 | Client Name Extraction | TC13 \| Valid client name with updates | Passed |  |
| TC14 | Client Name Extraction | TC14 \| Client keyword with summary | Failed | TC14: context.client_name equal "Pristine"; Expected: "Pristine"; Received: "Pristine summary" |
| TC15 | Client Name Extraction | TC15 \| Client name after about | Passed |  |
| TC16 | Client Name Extraction | TC16 \| Multi-word client name | Passed |  |
| TC17 | Client Name Extraction | TC17 \| Multi-word client name | Passed |  |
| TC18 | Client Name Extraction | TC18 \| Query without client name | Failed | TC18: context.client_name equal null; Expected: null; Received: "Show churn"; TC18: context.metadata.client_name_extraction_method equal "not_found"; Expected: "not_found"; Received: "code" |
| TC19 | Client Name Extraction | TC19 \| Unrelated query | Passed |  |
| TC20 | Client Name Extraction | TC20 \| Lowercase query | Passed |  |
| TC21 | Client Name Extraction | TC21 \| Uppercase query | Passed |  |
| TC22 | Client Name Extraction | TC22 \| Mixed-case query | Passed |  |
| TC23 | Client Name Extraction | TC23 \| Client name containing numbers | Passed |  |
| TC24 | Client Name Extraction | TC24 \| Client name containing special character | Failed | TC24: context.client_name equal "AT&T"; Expected: "AT&T"; Received: "Show" |
| TC25 | Client Name Extraction | TC25 \| Client name containing hyphen | Passed |  |
| TC26 | Client Name Extraction | TC26 \| Client name containing period | Passed |  |
| TC27 | Client Name Extraction | TC27 \| Client name containing apostrophe | Passed |  |
| TC28 | Client Name Extraction | TC28 \| Query with leading and trailing spaces | Passed |  |
| TC29 | Client Name Extraction | TC29 \| Empty query | Passed |  |
| TC30 | Client Name Extraction | TC30 \| Query contains only spaces | Passed |  |
| TC31 | Client Name Extraction | TC31 \| Null query | Passed |  |
| TC32 | Client Name Extraction | TC32 \| Query without client name | Failed | TC32: context.client_name equal null; Expected: null; Received: "What is the current"; TC32: context.metadata.client_name_extraction_method equal "not_found"; Expected: "not_found"; Received: "code" |
| TC33 | Client Name Extraction | TC33 \| KPI query without client name | Failed | TC33: context.client_name equal null; Expected: null; Received: "Give me the"; TC33: context.metadata.client_name_extraction_method equal "not_found"; Expected: "not_found"; Received: "code" |
| TC34 | Client Name Extraction | TC34 \| Client name at beginning of query | Failed | TC34: context.client_name equal "Yardworx"; Expected: "Yardworx"; Received: "Yardworx show me the" |
| TC35 | Final Churn Probability | TC35 \| Both Summary and KPI probabilities are high | Passed |  |
| TC36 | Final Churn Probability | TC36 \| Summary probability is high and KPI is below high threshold | Passed |  |
| TC37 | Final Churn Probability | TC37 \| Both probabilities are below high threshold | Passed |  |
| TC38 | Final Churn Probability | TC38 \| Both probabilities are low | Passed |  |
| TC39 | Final Churn Probability | TC39 \| KPI is high while Summary is below high threshold | Passed |  |
| TC40 | Final Churn Probability | TC40 \| Moderate Summary and KPI probabilities | Passed |  |
| TC41 | Final Churn Probability | TC41 \| Summary is exactly at high-risk threshold | Passed |  |
| TC42 | Final Churn Probability | TC42 \| KPI is exactly at high threshold while Summary is below it | Passed |  |
| TC43 | Final Churn Probability | TC43 \| Both probabilities are exactly at high-risk threshold | Passed |  |
| TC44 | Final Churn Probability | TC44 \| Both probabilities are zero | Passed |  |
| TC45 | Final Churn Probability | TC45 \| Summary probability is missing | Passed |  |
| TC46 | Final Churn Probability | TC46 \| KPI probability is missing | Passed |  |
| TC47 | Final Churn Probability | TC47 \| Campaign status has no configured weights | Passed |  |
| TC48 | Final Churn Probability | TC48 \| Campaign repository connection fails | Passed |  |
| TC49 | Final Churn Probability | TC49 \| Decimal probability calculation | Failed | TC49: context.final_probability equal 60; Expected: 60; Received: 59.99 |
| TC50 | Final Churn Probability | TC50 \| Maximum Summary probability with zero KPI probability | Passed |  |
| TC51 | Final Client Summary | TC51 \| Valid summary update | Passed |  |
| TC52 | Final Client Summary | TC52 \| Valid summary for another client | Passed |  |
| TC53 | Final Client Summary | TC53 \| Satisfaction score is zero | Passed |  |
| TC54 | Final Client Summary | TC54 \| Satisfaction score is maximum | Passed |  |
| TC55 | Final Client Summary | TC55 \| Missing client ID | Passed |  |
| TC56 | Final Client Summary | TC56 \| Missing client name | Passed |  |
| TC57 | Final Client Summary | TC57 \| Missing summary | Passed |  |
| TC58 | Final Client Summary | TC58 \| Empty client ID | Passed |  |
| TC59 | Final Client Summary | TC59 \| Empty client name | Passed |  |
| TC60 | Final Client Summary | TC60 \| Empty summary | Passed |  |
| TC61 | Final Client Summary | TC61 \| Long summary | Passed |  |
| TC62 | Final Client Summary | TC62 \| Missing satisfaction score | Passed |  |
| TC63 | Result Persistence | TC63 \| Existing client record | Passed |  |
| TC64 | Result Persistence | TC64 \| New client record | Passed |  |
| TC65 | Result Persistence | TC65 \| High-risk new client | Passed |  |
| TC66 | Result Persistence | TC66 \| Low-risk new client | Passed |  |
| TC67 | Result Persistence | TC67 \| Missing client ID | Passed |  |
| TC68 | Result Persistence | TC68 \| Missing client name | Passed |  |
| TC69 | Result Persistence | TC69 \| Missing summary | Passed |  |
| TC70 | Result Persistence | TC70 \| Missing recommendations | Passed |  |
| TC71 | Result Persistence | TC71 \| Empty recommendations list | Passed |  |
| TC72 | Result Persistence | TC72 \| Client name with apostrophe | Passed |  |
| TC73 | Result Persistence | TC73 \| Zero satisfaction score | Passed |  |
| TC74 | Result Persistence | TC74 \| Maximum satisfaction score | Passed |  |
| TC75 | Result Persistence | TC75 \| Zero churn probability | Passed |  |
| TC76 | Result Persistence | TC76 \| Maximum churn probability | Passed |  |
| TC77 | Result Persistence | TC77 \| Missing satisfaction score | Passed |  |
| TC78 | Historical KPI Match | TC78 \| Valid 768-dimensional KPI embedding with multiple matches | Passed |  |
| TC79 | Historical KPI Match | TC79 \| Valid embedding with exactly one historical match | Passed |  |
| TC80 | Historical KPI Match | TC80 \| No historical KPI matches found | Passed |  |
| TC81 | Historical KPI Match | TC81 \| Repository returns no result | Passed |  |
| TC82 | Historical KPI Match | TC82 \| Custom similarity threshold | Passed |  |
| TC83 | Historical KPI Match | TC83 \| Custom match count | Passed |  |
| TC84 | Historical KPI Match | TC84 \| Missing KPI embedding | Passed |  |
| TC85 | Historical KPI Match | TC85 \| Empty KPI embedding | Passed |  |
| TC86 | Historical KPI Match | TC86 \| KPI embedding has fewer than 768 dimensions | Passed |  |
| TC87 | Historical KPI Match | TC87 \| KPI embedding has more than 768 dimensions | Passed |  |
| TC88 | Historical KPI Match | TC88 \| Valid embedding with negative values | Passed |  |
| TC89 | Historical KPI Match | TC89 \| Zero-valued KPI embedding | Passed |  |
| TC90 | Historical KPI Match | TC90 \| Mixed positive and negative embedding values | Passed |  |
| TC91 | Historical KPI Match | TC91 \| Repository connection failure | Passed |  |
| TC92 | Historical Update Match | TC92 \| Multiple historical summary matches | Passed |  |
| TC93 | Historical Update Match | TC93 \| Single historical summary match | Passed |  |
| TC94 | Historical Update Match | TC94 \| No historical matches found | Passed |  |
| TC95 | Historical Update Match | TC95 \| Repository returns no match data | Passed |  |
| TC96 | Historical Update Match | TC96 \| Custom similarity threshold | Passed |  |
| TC97 | Historical Update Match | TC97 \| Custom maximum match count | Passed |  |
| TC98 | Historical Update Match | TC98 \| Missing summary embedding | Passed |  |
| TC99 | Historical Update Match | TC99 \| Empty summary embedding | Passed |  |
| TC100 | Historical Update Match | TC100 \| Summary embedding has fewer than 768 dimensions | Passed |  |
| TC101 | Historical Update Match | TC101 \| Summary embedding has 767 dimensions | Passed |  |
| TC102 | Historical Update Match | TC102 \| Moderate similarity historical match | Passed |  |
| TC103 | Historical Update Match | TC103 \| Similarity exactly at threshold | Passed |  |
| TC104 | Historical Update Match | TC104 \| Three historical summary matches | Passed |  |
| TC105 | Historical Update Match | TC105 \| Repository connection failure | Passed |  |
| TC106 | KPI Analysis | TC106 \| Negative KPI performance with high risk | Passed |  |
| TC107 | KPI Analysis | TC107 \| Improving KPI performance | Passed |  |
| TC108 | KPI Analysis | TC108 \| Stable KPI performance | Passed |  |
| TC109 | KPI Analysis | TC109 \| Incomplete KPI data | Failed | TC109: context.kpi_interpretation.analysis.business_summary matches "incomplete\|insufficient\|missing"; Expected pattern: /incomplete\|insufficient\|missing/i; Received string:  "Generated interpretation of declining performance." |
| TC110 | KPI Analysis | TC110 \| Multiple negative KPI trends | Passed |  |
| TC111 | KPI Analysis | TC111 \| Zero leads with improving funnel indicators | Failed | TC111: context.kpi_interpretation.matched_pattern_names contains "NO_LEADS"; Expected value: "NO_LEADS"; Received array: ["CPL_IMPROVING", "CPL_7D_DROP", "VOLATILE_CPL", "CPAPT_IMPROVING", "CPAPT_7D_DROP", "ADSPEND_DECREASING", "LOW_CPL_LOW_CPAPT", "FULL_FUNNEL_HEALTHY", "RECENT_POSITIVE_MOMENTUM", "MTD_STRONGER_THAN_30D", …] |
| TC112 | KPI Analysis | TC112 \| Zero appointments with improving funnel indicators | Failed | TC112: context.kpi_interpretation.matched_pattern_names contains "NO_APPOINTMENTS"; Expected value: "NO_APPOINTMENTS"; Received array: ["CPL_IMPROVING", "CPL_7D_DROP", "VOLATILE_CPL", "CPAPT_IMPROVING", "CPAPT_7D_DROP", "ADSPEND_DECREASING", "LOW_CPL_LOW_CPAPT", "FULL_FUNNEL_HEALTHY", "RECENT_POSITIVE_MOMENTUM", "MTD_STRONGER_THAN_30D", …] |
| TC113 | KPI Analysis | TC113 \| Missing client ID | Passed |  |
| TC114 | KPI Analysis | TC114 \| Missing KPI dataset | Passed |  |
| TC115 | KPI Analysis | TC115 \| Missing current KPIs | Passed |  |
| TC116 | KPI Analysis | TC116 \| Extreme worsening KPI performance | Passed |  |
| TC117 | KPI Analysis | TC117 \| Strong positive KPI performance | Passed |  |
| TC118 | KPI Analysis | TC118 \| LLM provider connection failure | Passed |  |
| TC119 | KPI Analysis | TC119 \| Pattern repository connection failure | Passed |  |
| TC120 | KPI Churn Analysis | TC120 \| Valid KPI analysis | Passed |  |
| TC121 | KPI Churn Analysis | TC121 \| Missing KPI dataset | Passed |  |
| TC122 | KPI Churn Analysis | TC122 \| Missing current KPIs | Passed |  |
| TC123 | KPI Churn Analysis | TC123 \| Missing KPI interpretation | Passed |  |
| TC124 | KPI Churn Analysis | TC124 \| Missing KPI matches | Passed |  |
| TC125 | KPI Churn Analysis | TC125 \| Invalid JSON response | Passed |  |
| TC126 | KPI Churn Analysis | TC126 \| Missing required keys in LLM output | Passed |  |
| TC127 | KPI Churn Analysis | TC127 \| Non-integer probability | Passed |  |
| TC128 | KPI Churn Analysis | TC128 \| Probability out of range | Passed |  |
| TC129 | KPI Churn Analysis | TC129 \| Groq provider failure | Failed | TC129: error.type equal "RuntimeError"; Expected: "RuntimeError"; Received: "ServiceException" |
| TC130 | KPI Data | TC130 \| Valid KPI data processing | Passed |  |
| TC131 | KPI Data | TC131 \| Client not found in repository | Passed |  |
| TC132 | KPI Data | TC132 \| Missing client ID | Passed |  |
| TC133 | KPI Data | TC133 \| Multiple KPI records | Passed |  |
| TC134 | KPI Data | TC134 \| Numeric KPI normalization | Passed |  |
| TC135 | KPI Data | TC135 \| Latest record using created date | Passed |  |
| TC136 | KPI Data | TC136 \| KPI window detection | Passed |  |
| TC137 | KPI Data | TC137 \| Client name fallback | Failed | TC137: context.kpi_dataset.client_name equal "Yardworx Land Management"; Expected: "Yardworx Land Management"; Received: null |
| TC138 | KPI Data | TC138 \| Latest client update fallback | Passed |  |
| TC139 | KPI Data | TC139 \| Empty repository after creation attempt | Passed |  |
| TC140 | KPI Embedding | TC140 \| Normal KPI data with high-risk interpretation | Passed |  |
| TC141 | KPI Embedding | TC141 \| current_kpis unavailable, use kpi_dataset | Passed |  |
| TC142 | KPI Embedding | TC142 \| No KPI patterns detected | Failed | TC142: context.kpi_embedding_content excludes "DETECTED PATTERNS"; Expected substring: not "DETECTED PATTERNS"; Received string:        "========== CLIENT ========== |
| TC143 | KPI Embedding | TC143 \| KPI interpretation contains incomplete analysis | Passed |  |
| TC144 | KPI Embedding | TC144 \| Some KPI values are missing | Passed |  |
| TC145 | KPI Embedding | TC145 \| KPI values are stored as strings | Passed |  |
| TC146 | KPI Embedding | TC146 \| Existing embedding record is found | Passed |  |
| TC147 | KPI Embedding | TC147 \| No existing embedding record, create new record | Passed |  |
| TC148 | KPI Embedding | TC148 \| Client ID is missing | Failed | TC148: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC149 | KPI Embedding | TC149 \| KPI interpretation is missing | Failed | TC149: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC150 | Summary Batch Preparation | TC150 \| Normal batching with valid client updates | Passed |  |
| TC151 | Summary Batch Preparation | TC151 \| Verify batch metadata | Passed |  |
| TC152 | Summary Batch Preparation | TC152 \| No client updates available | Failed | TC152: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC153 | Summary Batch Preparation | TC153 \| Verify update formatting | Passed |  |
| TC154 | Summary Batch Preparation | TC154 \| Updates should not be split across batches | Passed |  |
| TC155 | Summary Batch Preparation | TC155 \| Small updates combined into one batch | Passed |  |
| TC156 | Summary Batch Preparation | TC156 \| Large single update | Passed |  |
| TC157 | Summary Batch Preparation | TC157 \| Verify batch text generation | Passed |  |
| TC158 | Summary Churn Analysis | TC158 \| Valid summary analysis | Passed |  |
| TC159 | Summary Churn Analysis | TC159 \| Missing summary text | Failed | TC159: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC160 | Summary Churn Analysis | TC160 \| Missing summary matches | Failed | TC160: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC161 | Summary Churn Analysis | TC161 \| Invalid JSON response | Failed | TC161: error.type equal "ValueError"; Expected: "ValueError"; Received: "ServiceException" |
| TC162 | Summary Churn Analysis | TC162 \| Missing required keys | Failed | TC162: error.type equal "ValueError"; Expected: "ValueError"; Received: "ServiceException" |
| TC163 | Summary Churn Analysis | TC163 \| Non-integer probability | Failed | TC163: error.type equal "ValueError"; Expected: "ValueError"; Received: "ServiceException" |
| TC164 | Summary Churn Analysis | TC164 \| Probability out of range | Failed | TC164: error.type equal "ValueError"; Expected: "ValueError"; Received: "ServiceException" |
| TC165 | Summary Churn Analysis | TC165 \| Groq provider exception | Failed | TC165: error.type equal "RuntimeError"; Expected: "RuntimeError"; Received: "ServiceException" |
| TC166 | Summary Embedding | TC166 \| Valid summary embedding | Passed |  |
| TC167 | Summary Embedding | TC167 \| Missing client ID | Passed |  |
| TC168 | Summary Embedding | TC168 \| Missing summary | Passed |  |
| TC169 | Summary Embedding | TC169 \| Existing embedding updated | Passed |  |
| TC170 | Summary Embedding | TC170 \| New embedding saved | Passed |  |
| TC171 | Summary Embedding | TC171 \| Dictionary embedding response | Passed |  |
| TC172 | Summary Embedding | TC172 \| Vector dictionary response | Passed |  |
| TC173 | Summary Embedding | TC173 \| Embedding provider exception | Failed | TC173: error.type equal "RuntimeError"; Expected: "RuntimeError"; Received: "ServiceException" |
| TC174 | Summary Generation | TC174 \| Valid summary generation | Passed |  |
| TC175 | Summary Generation | TC175 \| Missing client ID | Failed | TC175: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC176 | Summary Generation | TC176 \| Missing summary batches | Failed | TC176: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC177 | Summary Generation | TC177 \| Invalid provider response | Passed |  |
| TC178 | Summary Generation | TC178 \| Invalid JSON response | Passed |  |
| TC179 | Summary Generation | TC179 \| Missing required JSON key | Passed |  |
| TC180 | Summary Generation | TC180 \| Groq provider exception | Failed | TC180: error.type equal "RuntimeError"; Expected: "RuntimeError"; Received: "ServiceException" |
| TC181 | Summary Generation | TC181 \| Multiple batch token accumulation | Passed |  |
| TC182 | Updates Data | TC182 \| Valid existing client | Passed |  |
| TC183 | Updates Data | TC183 \| Missing client ID | Failed | TC183: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC184 | Updates Data | TC184 \| None workflow context | Failed | TC184: error.type equal "ValueError"; Expected: "ValueError"; Received: "ValidationException" |
| TC185 | Updates Data | TC185 \| New client | Passed |  |
| TC186 | Updates Data | TC186 \| Missing summary | Passed |  |
| TC187 | Updates Data | TC187 \| Missing satisfaction score | Passed |  |
| TC188 | Updates Data | TC188 \| Previous record stored | Passed |  |
| TC189 | Updates Data | TC189 \| Repository exception | Failed | TC189: error.type equal "RuntimeError"; Expected: "RuntimeError"; Received: "ServiceException" |
