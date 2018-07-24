# touchpoints
An indexer for source code touchpoints, as described in this article: https://medium.com/@rklazar/touchpoints-smarter-comments-for-maintainable-code-523b62fb88b8. Add the script to your build process/pipeline in order to keep the description file updated and, optionally, to produce a convenient reference to existing and obsolete touchpoints.

## Usage

    python touchpoints.py marker root extensions description_file output_file

  * **marker**: a string that denotes a touchpoint, e.g. "TOUCHPOINT:"
  * **root**: the root directory of the source tree to search
  * **extensions**: the types of files to inspect, e.g. .js .css
  * **description_file**: path to JSON description file (if none exists, a new one will be created)
  * **output_file**: _optional_ path to touchpoint reference file to create (in Markdown format)

Typical usage cycle:

  1. Add/remove touchpoints in your source code
  2. Run the touchpoint indexer
  3. Inspect the description file, adding descriptions for new touchpoints and removing orphaned touchpoints (if desired)
  4. Run the touchpoint indexer to produce the formatted reference list

When looking for a touchpoint, view the reference list and then use your favourite IDE to conduct a search of your source files for the touchpoint name to identify every location where source for the related feature needs changing.

## License

MIT

## Bugs

See <https://github.com/ronaldak/touchpoints/issues>
