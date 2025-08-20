# DictionarPy

Offline dictionary application

---

## Examples

- Add a word/definition to the database
  
  ```sh
  $ dictionarpy -a -w "my new word" -p "my part of speech" -d "my definition!"
  ```

- Add or update the phonetic/phonemic transcription

  ```sh
  $ dictionarpy -a -w "my new word" -i "/mj nu wɝd/"
  ```

- Show the definitions for a word (use `-n` to avoid ansi escape sequences)

  ```sh
  $ dictionarpy -n "my new word"                                                
  ┌──────────────────────┐
  │     my new word      │
  │     /mj nu wɝd/      │
  ├──────────────────────┤
  │ 1. my part of speech │
  │    my definition!    │
  └──────────────────────┘
  ```

- Remove a word/definition from the database

  ```sh
  $ dictionarpy -r 1 "my new word"
  ```

- Learn a random word!

  ```sh
  $ dictionarpy "$(dictionarpy -z)"
  ```
