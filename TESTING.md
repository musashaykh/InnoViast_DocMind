\# 🧪 Testing Log — DocMind AI



\## Functional Tests



| # | Test Question | Expected | Result | Pass/Fail |

|---|---------------|----------|--------|-----------|

| 1 | What is a variable in Python? | Answer + source | Correct answer with source badge (Python\_Basics.txt) | ✅ Pass |

| 2 | How do I fix a NameError? | Answer + source | Correct answer with source badge | ✅ Pass |

| 3 | What's the weather today? | Fallback triggered | Correctly showed "not found" warning | ✅ Pass |

| 4 | what is python | Answer + source | Initially failed (see bugs below), now working after fixes | ✅ Pass |



\## Edge Case Tests



| # | Test | Expected | Result | Pass/Fail |

|---|------|----------|--------|-----------|

| 1 | Gibberish text | Fallback triggered | Correctly triggered fallback | ✅ Pass |

| 2 | Upload non-PDF/TXT file | Rejected by uploader | File type filter works | ✅ Pass |

| 3 | Question before any docs uploaded | "No knowledge base" message | Handled correctly | ✅ Pass |



\## UI/UX Tests



\- \[x] Sidebar doc count updates after upload

\- \[x] Source badges visually distinct (green/yellow)

\- \[x] Loading spinner / streaming appears during generation

\- \[x] Dark custom theme renders correctly

\- \[x] Delete document button works and rebuilds knowledge base



\## Bugs Found \& Fixed (Real Debugging Log)



| # | Bug | Root Cause | Fix |

|---|-----|-----------|-----|

| 1 | Blank Streamlit page on first Phase 6 run | `app.py` file got truncated while saving in Notepad | Recreated full file, saved as UTF-8 |

| 2 | Valid questions incorrectly triggering fallback | `SIMILARITY\_THRESHOLD = 0.5` too strict — Chroma's L2-based relevance scores run lower than expected | Empirically tested real scores via `debug\_scores.py`, recalibrated threshold to `0.3`, then further to `0.15` |

| 3 | Duplicate chunks in vector store (identical scores/content appearing twice) | `Chroma.from\_documents()` appends to existing `persist\_directory` instead of overwriting; re-running `vectorstore.py` duplicated all chunks | Added automatic `shutil.rmtree()` cleanup before rebuild in `create\_vectorstore()` |

| 4 | Deployed app had no knowledge base (blank retrieval) | `chroma\_db/` is correctly excluded via `.gitignore`, so it never reached GitHub/Streamlit Cloud | Added auto-rebuild logic in `get\_vectorstore()` — builds DB from `/data` automatically if missing (e.g. on fresh deployment) |

| 5 | Source badge and answer text contradicting each other (badge showed sources while answer said "not found") | Source lookup and answer generation used two separate, independent retrieval calls that could disagree | Unified into single `get\_relevant\_context()` call; source badge now only shown if the LLM's actual answer doesn't contain the fallback phrase |

| 6 | LLM confused short queries like "what is python" with instructions, or failed to answer despite relevant content existing | `====` separator lines and header noise in `Python\_Basics.txt` diluted chunk embeddings; prompt lacked clear context/question boundaries | Cleaned formatting noise from source `.txt` file; rebuilt vector store; added explicit `<context></context>` XML delimiters to `RAG\_PROMPT` |

| 7 | Weak/generic queries missing genuinely relevant chunks | `TOP\_K = 3` too narrow — relevant chunk was ranked 4th | Increased `TOP\_K` to 6 |

| 8 | `Remove-Item`/`rmdir /s /q` syntax errors on Windows | Used Command Prompt (cmd.exe) syntax in PowerShell | Used PowerShell-native `Remove-Item -Recurse -Force` |

| 9 | `PermissionError` when deleting `chroma\_db` | A running Streamlit/Python process still had the SQLite file open | Stopped all Python processes before deleting/rebuilding |



\## Known Limitations (documented, not bugs)



\- Chat history resets on page refresh (Streamlit session-based, no persistent DB)

\- First response after startup can be slower (\~5-10s cold start for embedding model download)

\- Deleting a document triggers a full knowledge base rebuild rather than targeted removal (simpler, more robust approach given Chroma's API)



\## Testing Methodology



Testing was done iteratively and empirically rather than purely by intuition — actual similarity scores were inspected via a custom `debug\_scores.py` diagnostic script before tuning thresholds, rather than guessing values. This caught the real gap between relevant (positive, 0.08–0.42) and irrelevant (negative, \~-0.40) query scores, which directly informed the final threshold of 0.15.



\---



\*\*Tested by:\*\* \[Your Name]

\*\*Date:\*\* July 2026

\*\*Environment:\*\* Windows, Python 3.11, local + Streamlit Community Cloud deployment

