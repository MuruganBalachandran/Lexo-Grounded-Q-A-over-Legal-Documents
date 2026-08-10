# Eval Results

**Run date:** 2026-08-10 09:21:35  
**Endpoint:** `http://localhost:8000/ask`  
**Total:** 19 | **Passed:** 3 | **Failed:** 3 | **Errors:** 13

---

## Case-by-case

| ID | Type | Status | Notes |
|----|------|--------|-------|
| 1 | in_corpus | ❌ FAIL | Missing: ['laptops', 'badges', 'source code access']. Cited: ['02_employment_agreement_excerpt.md', '02_employment_agreement_excerpt.md']. |
| 2 | in_corpus | ✅ PASS | Cited: ['02_employment_agreement_excerpt.md']. |
| 3 | in_corpus | ✅ PASS | Cited: ['02_employment_agreement_excerpt.md']. |
| 4 | in_corpus | ❌ FAIL | Missing: ['invoices', 'damaged goods']. Cited: ['01_matter_memo_arvind_v_northfield.md', '05_counsel_notes_settlement.md']. |
| 5 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 6 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 7 | in_corpus | ❌ FAIL | Missing: ['late filings']. Cited: ['03_hearing_notice_template.md']. |
| 8 | in_corpus | ✅ PASS | Cited: ['03_hearing_notice_template.md']. |
| 9 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 10 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 11 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 12 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 13 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 14 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 15 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| 16 | in_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| O1 | out_of_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| O2 | out_of_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |
| O3 | out_of_corpus | ❌ ERROR | Error: 502 Server Error: Bad Gateway for url: http://localhost:8000/ask |

---

## Full Answers

### [1] What notice period applies when Bluecrest or Priya Nambiar ends the employment agreement?
**Status:** FAIL  
**Answer preview:** When either Bluecrest Analytics LLP or Priya Nambiar ends the employment agreement, a notice period of 60 days written notice applies.  
**Cited files:** ['02_employment_agreement_excerpt.md', '02_employment_agreement_excerpt.md']  
**Trace:** ['retrieve', 'grade_chunks', 'generate']  

### [2] How long is the non-compete after leaving Bluecrest, and when does it apply?
**Status:** PASS  
**Answer preview:** The non-compete clause applies for 12 months after leaving Bluecrest.

It applies if the employee:
*   Works for a direct competitor in the same city where Bluecrest has an office.
*   Uses the same c  
**Cited files:** ['02_employment_agreement_excerpt.md']  
**Trace:** ['retrieve', 'grade_chunks', 'generate']  

### [3] What kinds of information are called out as confidential in the Bluecrest excerpt?
**Status:** PASS  
**Answer preview:** The kinds of information called out as confidential are:
*   Pricing sheets
*   Unreleased product roadmaps
*   Customer names marked “confidential” in writing  
**Cited files:** ['02_employment_agreement_excerpt.md']  
**Trace:** ['retrieve', 'grade_chunks', 'generate']  

### [4] What is the civil suit number and who are the parties in the transport invoice dispute memo?
**Status:** FAIL  
**Answer preview:** Based on the information provided:

*   The civil suit number is CV-2024-8812.
*   The parties are Arvind Mehta and Northfield Logistics Pvt. Ltd.  
**Cited files:** ['01_matter_memo_arvind_v_northfield.md', '05_counsel_notes_settlement.md']  
**Trace:** ['retrieve', 'grade_chunks', 'generate']  

### [5] Under the memo, what limitation period applies to contract claims under the fictional Riverside Code?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [6] When is the next hearing in Arvind Mehta v. Northfield, and what is scheduled?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [7] How many clear days before the listed date must parties file written arguments under the hearing notice rules?
**Status:** FAIL  
**Answer preview:** Parties must file written arguments seven clear days before the listed date.  
**Cited files:** ['03_hearing_notice_template.md']  
**Trace:** ['retrieve', 'grade_chunks', 'generate']  

### [8] What time is case CV-2024-8812 listed, and what is it for?
**Status:** PASS  
**Answer preview:** Case CV-2024-8812 is listed for:
*   **Time:** 11:00 a.m.
*   **Purpose:** Arguments on invoice set-off.  
**Cited files:** ['03_hearing_notice_template.md']  
**Trace:** ['retrieve', 'grade_chunks', 'generate']  

### [9] What happened to case CV-2023-4401 (Lakeview Society v. City Water Board), and what is the next date?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [10] For commercial suits above five lakh fictional rupees, what does Section 14 say about mediation?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [11] If a contract fixes no interest rate, what rate may be awarded on admitted dues under Section 22?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [12] What settlement offer did Northfield make in the counsel notes, and what counter-instruction did the client give?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [13] Are the settlement talks described in the counsel notes binding? What is the reminder?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [14] Who is the lessor and lessee for Unit 4B at Harbor View Tower, and what is the monthly rent?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [15] What is the security deposit amount, and within how many days must it be refunded after handover?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [16] Is subletting allowed for the Harbor View lease without extra steps?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [O1] What is the population of Riverside city?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [O2] What penalty applies if Priya breaches the non-compete?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  

### [O3] Who won case CV-2024-8812?
**Status:** ERROR  
**Answer preview:**   
**Cited files:** []  
**Trace:** []  
