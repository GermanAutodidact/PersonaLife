# English and German

[Deutsch](languages.de.md) · [English README](../README.md)

All public guide pages have an English original and a complete German counterpart ending in `.de.md`. Each page links to the other language. Event identifiers, schema keys, command names, third-party source evidence and the original Apache license remain unchanged.

## Interface language

```sh
personalife --language en --help
personalife --language de --help
personalife --sprache de persona create
```

Set `PERSONALIFE_LANGUAGE=en` or `de` for the CLI default. Put the global language option before the command. CLI help, setup questions and PersonaLife's own error messages use this language. Technical diagnostics originating in Python, SQLite, pip or external providers may retain their original wording so useful details are not lost.

The installers accept `-Language de` in PowerShell or `de` as the shell script's first argument. Their own messages and the recommended next command are localized; dependency installers and test runner diagnostics are external output.

## Persona language

A profile's `language` is `en` or `de`; older profiles default to English. `persona(language='de')` creates localized occupation task examples, place names, hobbies and routines. `get_presets('de')` provides translated labels while keeping preset IDs stable.

New engine-generated activity labels, story events, chat labels, explanations and model-context instructions use the stored persona language. Your names, custom task text and chat summaries are preserved. Changing a language does not translate existing historical events or future plans already recorded. New days use the new language. Rebuild no canonical history merely for translation.

A CLI language option changes the interface, not an existing persona's stored language. A JSON profile's explicit language takes precedence; without it, CLI creation uses the interface language.

## API and LLM

`Accept-Language: de` or `en` selects API errors and preset labels. Regional variants and quality values are supported. With no supported preference, the server's configured language is used. New personas inherit that language only if their profile omits `language`.

Endpoint paths, command names and JSON keys remain the same in both languages. Structured state values such as `planned`, `completed` and location IDs remain machine-readable identifiers. Existing stored text is returned as recorded, not automatically translated by an HTTP header.

Context contains `language`; narrative adapters request that output language from the model. This is a model instruction, not a guarantee about a remote provider. It does not add a model dependency to deterministic simulation.

## Examples

```sh
python examples/three_days.py --language en --output demo-output-en
python examples/three_days.py --language de --output demo-output-de
```

Use `examples/jenna.json` or `examples/jenna.de.json` for equivalent complete profiles. Committed human-readable examples are in `examples/generated/` and `examples/generated-de/`.

## Repository description

GitHub has one About description field. `repository-metadata.json` provides English, German and a combined bilingual description, plus shared relevant topics. These are prepared values, not automatically applied settings. Package indexes likewise use one primary package description; language-specific long descriptions are available in the linked READMEs.
