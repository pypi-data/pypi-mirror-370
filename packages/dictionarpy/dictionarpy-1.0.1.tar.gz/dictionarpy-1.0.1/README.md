# DictionarPy

Offline dictionary application

### Statistics regarding this version's included dictionary:

```sh
$ dictionarpy -ns
Words:               53081
Definitions:         118456
IPA Transcriptions:  29742
Disk size:           10.45MB
───────────────────────────────────────────────────────
Parts of speech:
    adjective │ intransitive verb │ nom masculin │ noun
    article │ transitive/intransitive verb │ phrase
    definite article │ adverb │ idiom │ auxiliary verb
    pronoun │ abbreviation │ conjunction │ verb
    conjuction │ preposition │ transitive verb │ nom
    féminin │ determiner │ nom │ plural noun
    interjection │ abréviation │ verbe
```

---

## Examples

- Add a word/definition to the database
  
  ```sh
  $ dictionarpy -a -w "my new word" -p "my part of speech" -d "my definition!"
  ```

- Add or update the phonetic/phonemic transcription of a word

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

- Run `dpy -h` for help and additional functions
