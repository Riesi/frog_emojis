Most of theses frogs are based on the SVGs of the twitter emoji set (https://twemoji.twitter.com). Others are unique designs with other inspirations in mind.

Have fun using them! 🐸

## License

By contributing you agree to license your contribution under the terms of the GPLv3 (for code) and CC-BY 4.0 (for graphics) licenses. The corresponding license can be found in the LICENCE and LICENSE-GRAPHICS file respectively. The following links also reference to the licenses:

GPLv3: <http://www.gnu.org/licenses/gpl-3.0.txt>

CC-BY 4.0: <https://github.com/twitter/twemoji/blob/gh-pages/LICENSE-GRAPHICS>

## Contributing
When submitting PRs keep the following in mind please:

- only submit SVGs.
- don't have spaces in your file names. Use snake_case or camelCase instead.
- only submit SVGs with the file ending `.svg`. Not `.SVG` or `.sVg`

## Generating PNGs 
If you want to generate PNGs from the SVGs, you can use the `gen_png.py` script.

### Dependencies
- Python 3.9 - To run the script.
- Inkscape - Used to generate the PNGs. Needs to be located in PATH.
- (Optional) git - Can be used to automatically add a new commit with the generated PNGs.

### Usage
```
gen_png.py [OPTION]

-h, --help                      Shows this help message.
-a, --all                       Regenerates all PNGs.
-s, --specific [FILENAME]...    Regenerate the PNGs for each FILENAME in the "svg" folder. The '.svg' suffix is optional.
-g, --git                       Regenerates all PNGs and creates a git commit for them. Requires 'git' to be installed and located in PATH.
```
