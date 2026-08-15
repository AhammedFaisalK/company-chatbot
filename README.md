## Known Limitations

- **Non-English response quality:** The chatbot can respond in the user's
  language (e.g. Malayalam), and facts are translated correctly, but
  grammar/phrasing may feel less natural than native English responses.
  This is a limitation of the underlying LLM (Llama 3.3 via Groq), which
  is primarily trained on English data. Upgrading to a model with stronger
  multilingual support, or adding a dedicated translation step, would
  improve this if needed later.
