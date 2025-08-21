# DictionarPy

Offline dictionary application

### Statistics regarding this version's included dictionary:

```sh
$ dictionarpy -ns
Words:               53101
Definitions:         118487
IPA Transcriptions:  29746
Disk size:           10.46MB
───────────────────────────────────────────────────────
Parts of speech:
    conjunction │ transitive/intransitive verb
    conjuction │ nom masculin │ article │ idiom
    definite article │ phrase │ nom féminin │ determiner
    │ adjective │ interjection │ transitive verb │ plural
    noun │ abbreviation │ nom │ auxiliary verb │ verb
    abréviation │ intransitive verb │ preposition
    adverb │ noun │ pronoun │ verbe
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
